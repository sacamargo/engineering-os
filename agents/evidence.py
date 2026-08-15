"""Evidence helpers for agent execution — integrate with Evidence Model."""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ExecutionEvidence:
    id: str
    claim: str
    kind: str
    pointer: str
    task_id: str
    agent_id: str
    certainty: str = "observed"
    produced_by: str = "agent_runtime"
    timestamp: float = field(default_factory=time.time)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_evidence(
    claim: str,
    *,
    kind: str,
    pointer: str,
    task_id: str,
    agent_id: str,
    details: dict[str, Any] | None = None,
) -> ExecutionEvidence:
    return ExecutionEvidence(
        id=f"eos.evidence.agent.{uuid.uuid4().hex[:10]}",
        claim=claim,
        kind=kind,
        pointer=pointer,
        task_id=task_id,
        agent_id=agent_id,
        details=details or {},
    )


def task_may_complete(evidence: list[ExecutionEvidence], *, require_tests: bool = False) -> bool:
    """Success requires concrete evidence — never 'done' alone."""
    if not evidence:
        return False
    if require_tests and not any(e.kind == "tests" for e in evidence):
        return False
    return True
