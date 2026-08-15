"""Human approval protocol — agents cannot skip gates."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Decision = Literal["approve", "reject"]


@dataclass
class ApprovalRequest:
    id: str
    task_id: str
    agent_id: str
    reason: str
    risk_level: str
    status: str = "pending"
    decision: Decision | None = None
    decided_by: str | None = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ApprovalRecord:
    request_id: str
    decision: Decision
    decided_by: str
    reason: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def decide(request: ApprovalRequest, decision: Decision, *, by: str, reason: str = "") -> ApprovalRecord:
    request.status = "decided"
    request.decision = decision
    request.decided_by = by
    return ApprovalRecord(request.id, decision, by, reason or decision)
