"""Failure handling — classify failures without automatic retries."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

Action = Literal["retry", "replan", "escalate", "block", "abort"]


@dataclass
class FailureDecision:
    task_id: str
    classification: str
    retryable: bool
    action: Action
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def classify_failure(task_id: str, error_kind: str, message: str = "") -> FailureDecision:
    kind = error_kind.lower()
    if kind in {"timeout", "network", "transient"}:
        return FailureDecision(task_id, kind, True, "retry", message or "transient failure")
    if kind in {"validation", "gate"}:
        return FailureDecision(task_id, kind, False, "block", message or "validation failed")
    if kind in {"missing_capability", "missing_knowledge"}:
        return FailureDecision(task_id, kind, False, "escalate", message or "coverage gap")
    if kind in {"human_rejection"}:
        return FailureDecision(task_id, kind, False, "replan", message or "human rejected")
    if kind in {"assumption_broken", "dependency"}:
        return FailureDecision(task_id, kind, False, "replan", message or "plan assumptions invalid")
    return FailureDecision(task_id, kind or "unknown", False, "block", message or "root cause unknown")
