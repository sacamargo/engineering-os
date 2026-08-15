"""Production human approval — agents/skills/orchestrator cannot approve."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any


FORBIDDEN_APPROVERS = ("agent:", "skill:", "orchestrator", "delivery-runtime", "system:auto")


@dataclass
class ProductionApproval:
    id: str
    release_candidate_id: str
    environment: str
    scope: str
    decision: str  # approved | rejected | pending
    approver: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def is_human_approver(approver: str) -> bool:
    a = (approver or "").strip().lower()
    if not a:
        return False
    if a.startswith(FORBIDDEN_APPROVERS):
        return False
    if a in {"agent", "skill", "orchestrator"}:
        return False
    return a.startswith("human:") or a.startswith("user:")


def record_production_approval(
    *,
    approval_id: str,
    release_candidate_id: str,
    environment: str,
    scope: str,
    decision: str,
    approver: str,
    evidence: list[dict[str, Any]] | None = None,
) -> ProductionApproval:
    if environment == "production" and decision == "approved" and not is_human_approver(approver):
        raise PermissionError("HUMAN_APPROVAL_REQUIRED: agent/skill/orchestrator cannot approve production")
    return ProductionApproval(
        id=approval_id,
        release_candidate_id=release_candidate_id,
        environment=environment,
        scope=scope,
        decision=decision,
        approver=approver,
        evidence=list(evidence or []),
        notes=["Production never auto-approved by Agent/Skill/Orchestrator"],
    )
