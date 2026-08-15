"""Production Operations core models — vendor neutral.

ProductionOperation ≠ Deployment ≠ Release ≠ ReleaseCandidate ≠ Incident ≠ Rollback
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

OpsStatus = Literal[
    "planned",
    "validating",
    "awaiting_approval",
    "deploying",
    "verifying",
    "succeeded",
    "failed",
    "degraded",
    "rollback_required",
    "rolling_back",
    "rolled_back",
    "needs_human",
    "cancelled",
]

HealthStatus = Literal["healthy", "degraded", "unhealthy", "unknown"]
RiskLevel = Literal["low", "medium", "high", "critical"]
EnvClass = Literal["local", "development", "test", "staging", "production"]


def _id(prefix: str) -> str:
    return f"eos.{prefix}.{uuid.uuid4().hex[:12]}"


@dataclass
class ProductionEnvironment:
    id: str
    name: EnvClass
    classification: EnvClass
    risk: RiskLevel
    deployment_policy: str  # allow | deny | approval_required
    approval_policy: str  # none | optional | human_required
    health_checks: list[str] = field(default_factory=list)
    rollback_policy: str = "human_required"  # auto_allowed | human_required
    adapter: str = "local_fake"
    permissions_required: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_PRODUCTION_ENVIRONMENTS: dict[str, ProductionEnvironment] = {
    "local": ProductionEnvironment(
        "eos.env.local",
        "local",
        "local",
        "low",
        "allow",
        "none",
        ["application"],
        "auto_allowed",
        "local_fake",
        ["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
    ),
    "development": ProductionEnvironment(
        "eos.env.development",
        "development",
        "development",
        "low",
        "allow",
        "none",
        ["application"],
        "auto_allowed",
        "local_fake",
        ["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
    ),
    "test": ProductionEnvironment(
        "eos.env.test",
        "test",
        "test",
        "medium",
        "allow",
        "optional",
        ["application", "api"],
        "auto_allowed",
        "local_fake",
        ["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
    ),
    "staging": ProductionEnvironment(
        "eos.env.staging",
        "staging",
        "staging",
        "high",
        "approval_required",
        "human_required",
        ["application", "api", "dependency"],
        "human_required",
        "local_fake",
        ["PRODUCTION_READ", "PRODUCTION_DEPLOY", "PRODUCTION_ROLLBACK"],
    ),
    "production": ProductionEnvironment(
        "eos.env.production",
        "production",
        "production",
        "critical",
        "approval_required",
        "human_required",
        ["application", "api", "database", "dependency", "error_rate", "latency"],
        "human_required",
        "local_fake",
        [
            "PRODUCTION_READ",
            "PRODUCTION_DEPLOY",
            "PRODUCTION_ROLLBACK",
            "PRODUCTION_INCIDENT_MANAGE",
        ],
    ),
}


@dataclass
class DeploymentTarget:
    id: str
    application: str
    environment: str
    version: str
    artifact_id: str
    adapter: str
    configuration_ref: str | None = None  # never a secret value
    health_policy: str = "require_healthy"
    rollback_policy: str = "human_required"
    release_kind: str = "backend"  # backend | web | ios | android | bundle

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProductionOperation:
    id: str
    release_candidate_id: str
    environment: str
    target_id: str
    status: OpsStatus = "planned"
    dry_run: bool = False
    evidence: list[dict[str, Any]] = field(default_factory=list)
    gaps: list[dict[str, Any]] = field(default_factory=list)
    approval_id: str | None = None
    deployment_id: str | None = None
    health_status: HealthStatus = "unknown"
    notes: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DeploymentRecord:
    id: str
    operation_id: str
    target_id: str
    adapter: str
    status: str  # pending | running | succeeded | failed | unsupported
    evidence: list[dict[str, Any]] = field(default_factory=list)
    started_at: float | None = None
    ended_at: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def new_operation(*, release_candidate_id: str, environment: str, target_id: str, dry_run: bool = False) -> ProductionOperation:
    return ProductionOperation(
        id=_id("prodop"),
        release_candidate_id=release_candidate_id,
        environment=environment,
        target_id=target_id,
        dry_run=dry_run,
        notes=["ProductionOperation ≠ Deployment ≠ ReleaseCandidate"],
    )
