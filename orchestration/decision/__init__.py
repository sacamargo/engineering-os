"""Decision recording for material planning choices."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DecisionRecord:
    id: str
    title: str
    choice: str
    reason: str
    context: str = ""
    alternatives: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    consequences: list[str] = field(default_factory=list)
    reversibility: str = "medium"
    decided_by: str = "planning_orchestrator"
    status: str = "proposed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def decisions_from_plan(plan_decisions: list[dict[str, Any]]) -> list[DecisionRecord]:
    out: list[DecisionRecord] = []
    for d in plan_decisions:
        out.append(
            DecisionRecord(
                id=d["id"],
                title=d.get("title", ""),
                choice=d.get("choice", ""),
                reason=d.get("reason", ""),
                alternatives=list(d.get("alternatives") or []),
                reversibility=d.get("reversibility", "medium"),
                status=d.get("status", "proposed"),
            )
        )
    return out
