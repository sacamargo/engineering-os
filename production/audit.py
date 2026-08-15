"""Immutable audit trail for production operations."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any

from production.secrets import assert_no_secrets


@dataclass(frozen=True)
class AuditEvent:
    actor: str
    role: str
    agent: str | None
    task: str | None
    release: str | None
    environment: str
    action: str
    decision: str | None
    timestamp: float
    evidence: tuple[tuple[str, Any], ...]
    result: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "actor": self.actor,
            "role": self.role,
            "agent": self.agent,
            "task": self.task,
            "release": self.release,
            "environment": self.environment,
            "action": self.action,
            "decision": self.decision,
            "timestamp": self.timestamp,
            "evidence": dict(self.evidence),
            "result": self.result,
        }


@dataclass
class AuditTrail:
    events: list[AuditEvent] = field(default_factory=list)

    def append(
        self,
        *,
        actor: str,
        role: str,
        environment: str,
        action: str,
        result: str,
        agent: str | None = None,
        task: str | None = None,
        release: str | None = None,
        decision: str | None = None,
        evidence: dict[str, Any] | None = None,
    ) -> AuditEvent:
        payload = evidence or {}
        assert_no_secrets(payload)
        # frozenset/tuple for immutability of evidence snapshot
        ev = AuditEvent(
            actor=actor,
            role=role,
            agent=agent,
            task=task,
            release=release,
            environment=environment,
            action=action,
            decision=decision,
            timestamp=time.time(),
            evidence=tuple(sorted(payload.items(), key=lambda x: x[0])),
            result=result,
        )
        self.events.append(ev)
        return ev

    def to_list(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self.events]
