"""Role Resolution — specialization metadata for plans/tasks.

ROLE ≠ AGENT ≠ CAPABILITY.
Bindings load from JSON so new roles/bindings do not require orchestrator code edits.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from orchestration.capability.arbitration import ArbitrationResult
from orchestration.intent import StructuredIntent

ExecutorHint = Literal["human", "ai_agent", "automation", "external_system"]

BINDINGS_PATH = Path(__file__).resolve().parent / "bindings.json"


@dataclass
class RoleAssignment:
    role_id: str
    source: str
    capability_ids: list[str] = field(default_factory=list)
    specialized: bool = False
    automatable: bool = True
    human_required: bool = False
    human_approval_required: bool = False
    future_agent_eligible: bool = True
    executor_hint: ExecutorHint = "ai_agent"
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RoleResolution:
    roles: list[RoleAssignment]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "roles": [r.to_dict() for r in self.roles],
            "notes": self.notes,
            "role_ids": [r.role_id for r in self.roles],
        }


def load_bindings(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or BINDINGS_PATH).read_text(encoding="utf-8"))


def resolve_roles(
    intent: StructuredIntent,
    arbitration: ArbitrationResult,
    bindings: dict[str, Any] | None = None,
) -> RoleResolution:
    data = bindings or load_bindings()
    human_required_roles = set(data.get("human_required_roles") or [])
    by_cap = {b["capability_id"]: list(b.get("role_ids") or []) for b in data.get("bindings") or []}
    gap_roles = data.get("gap_area_roles") or {}

    assignments: dict[str, RoleAssignment] = {}
    notes = [
        "Roles are specialization metadata, not Agents.",
        "Humans may fulfill roles; future Agents may fulfill multiple roles.",
    ]

    def upsert(role_id: str, **kwargs: Any) -> None:
        existing = assignments.get(role_id)
        if existing is None:
            assignments[role_id] = RoleAssignment(role_id=role_id, **kwargs)
            return
        existing.capability_ids = sorted(set(existing.capability_ids + kwargs.get("capability_ids", [])))
        existing.human_required = existing.human_required or kwargs.get("human_required", False)
        existing.human_approval_required = existing.human_approval_required or kwargs.get(
            "human_approval_required", False
        )
        existing.specialized = existing.specialized or kwargs.get("specialized", False)
        if kwargs.get("executor_hint") == "human":
            existing.executor_hint = "human"
            existing.automatable = False
            existing.future_agent_eligible = False

    for cap_id in arbitration.selected:
        for role_id in by_cap.get(cap_id, []):
            human = role_id in human_required_roles
            upsert(
                role_id,
                source="capability_binding",
                capability_ids=[cap_id],
                specialized=True,
                automatable=not human,
                human_required=human,
                human_approval_required=human,
                future_agent_eligible=not human,
                executor_hint="human" if human else "ai_agent",
                reason=f"Bound from {cap_id}",
            )

    for item in arbitration.insufficient:
        area = item.get("area")
        for role_id in gap_roles.get(area, []):
            human = role_id in human_required_roles or bool(item.get("blocking"))
            if area in {"electrical_engineering", "physical_access_control"}:
                human = True
            upsert(
                role_id,
                source=f"gap:{area}",
                capability_ids=[],
                specialized=True,
                automatable=not human,
                human_required=human,
                human_approval_required=human,
                future_agent_eligible=not human,
                executor_hint="human" if human else "ai_agent",
                reason=f"gap area {area}",
            )

    # Intent-based extras without creating Capabilities
    if "investigate_incident" in intent.possible_intents:
        upsert(
            "eos.role.incident-responder",
            source="intent",
            capability_ids=[],
            specialized=True,
            automatable=True,
            human_required=False,
            human_approval_required=True,
            future_agent_eligible=True,
            executor_hint="human",
            reason="production incident intents require human authority for prod access",
        )
    if "build" in intent.possible_intents:
        upsert(
            "eos.role.product-manager",
            source="intent",
            capability_ids=[],
            specialized=False,
            automatable=False,
            human_required=False,
            human_approval_required=True,
            future_agent_eligible=False,
            executor_hint="human",
            reason="product scope clarifications",
        )
        upsert(
            "eos.role.requirements-engineer",
            source="intent",
            capability_ids=[],
            specialized=True,
            automatable=True,
            human_required=False,
            human_approval_required=False,
            future_agent_eligible=True,
            executor_hint="ai_agent",
            reason="requirements capture for build intents",
        )

    return RoleResolution(roles=list(assignments.values()), notes=notes)
