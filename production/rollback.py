"""Rollback execution + policy — verify health after rollback."""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any

from production.adapters.base import AdapterRequest, AdapterResult
from production.health import aggregate_health, health_allows_success


@dataclass
class RollbackExecution:
    id: str
    from_version: str
    to_version: str
    reason: str
    policy: str  # auto_allowed | human_required
    authorized_by: str | None
    status: str  # planned | authorized | executing | verified | failed | needs_human
    evidence: list[dict[str, Any]] = field(default_factory=list)
    health_after: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def rollback_policy_decision(
    *,
    environment_policy: str,
    health: str,
    auto_rollback_allowed: bool,
) -> str:
    """Return auto_rollback | human_required | none."""
    if health not in {"unhealthy", "degraded"}:
        return "none"
    if environment_policy == "auto_allowed" and auto_rollback_allowed:
        return "auto_rollback"
    return "human_required"


def execute_rollback(
    adapter: Any,
    *,
    operation_id: str,
    target: dict[str, Any],
    environment: str,
    artifact_id: str,
    from_version: str,
    to_version: str,
    reason: str,
    policy: str,
    authorized_by: str | None,
) -> RollbackExecution:
    rid = f"eos.rollback.{uuid.uuid4().hex[:10]}"
    if policy == "human_required" and not authorized_by:
        return RollbackExecution(
            rid,
            from_version,
            to_version,
            reason,
            policy,
            None,
            "needs_human",
            evidence=[{"kind": "HUMAN_ROLLBACK_REQUIRED"}],
        )
    req = AdapterRequest(
        operation_id=operation_id,
        target=target,
        environment=environment,
        artifact_id=artifact_id,
        previous_version=to_version,
    )
    result: AdapterResult = adapter.rollback(req)
    evidence = list(result.evidence)
    if result.status != "ok":
        return RollbackExecution(
            rid,
            from_version,
            to_version,
            reason,
            policy,
            authorized_by,
            "failed",
            evidence=evidence + [{"kind": "ROLLBACK_FAILED", "message": result.message}],
            health_after="unknown",
        )
    # Must verify health after rollback — adapter OK ≠ success
    health_res = adapter.health(req)
    evidence.extend(health_res.evidence)
    health = aggregate_health([health_res.health_hint])
    status = "verified" if health_allows_success(health) else "failed"
    if status == "failed":
        evidence.append({"kind": "ROLLBACK_FAILED", "reason": f"post-rollback health={health}"})
    return RollbackExecution(
        rid,
        from_version,
        to_version,
        reason,
        policy,
        authorized_by,
        status,
        evidence=evidence,
        health_after=health,
    )
