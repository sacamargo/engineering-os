"""DeploymentVerification — deploy OK ≠ succeeded without health evidence."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from production.health import HealthStatus, health_allows_success

VerificationDecision = Literal[
    "succeeded",
    "degraded",
    "rollback_required",
    "needs_human",
    "failed",
]


@dataclass
class DeploymentVerification:
    deployment_id: str
    health: HealthStatus
    evidence: list[dict[str, Any]] = field(default_factory=list)
    decision: VerificationDecision = "needs_human"
    policy: str = "require_healthy"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def verify_deployment(
    *,
    deployment_id: str,
    health: HealthStatus,
    evidence: list[dict[str, Any]] | None = None,
    policy: str = "require_healthy",
) -> DeploymentVerification:
    ev = list(evidence or [])
    if health == "unknown":
        return DeploymentVerification(
            deployment_id,
            health,
            ev + [{"kind": "UNKNOWN_HEALTH", "note": "UNKNOWN ≠ HEALTHY"}],
            "needs_human",
            policy,
        )
    if health_allows_success(health) and policy == "require_healthy":
        return DeploymentVerification(deployment_id, health, ev, "succeeded", policy)
    if health == "degraded":
        return DeploymentVerification(deployment_id, health, ev, "degraded", policy)
    if health == "unhealthy":
        return DeploymentVerification(deployment_id, health, ev, "rollback_required", policy)
    return DeploymentVerification(deployment_id, health, ev, "failed", policy)
