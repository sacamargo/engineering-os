"""Core Delivery object models — vendor neutral."""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

BuildStatus = Literal["pending", "running", "succeeded", "failed", "cancelled"]
ValidationStatus = Literal["NOT_RUN", "PASSED", "FAILED", "BLOCKED", "UNKNOWN"]
DeliveryStatus = Literal[
    "draft",
    "building",
    "validating",
    "ready",
    "blocked",
    "needs_human",
    "released",
    "failed",
    "cancelled",
]
RiskLevel = Literal["low", "medium", "high", "critical"]
EnvironmentName = Literal["local", "development", "test", "staging", "production"]


def _id(prefix: str) -> str:
    return f"eos.{prefix}.{uuid.uuid4().hex[:12]}"


@dataclass
class DeliveryArtifact:
    """Build/package/report artifact — distinct from Execution Layer work-product artifacts."""

    id: str
    type: str  # source_bundle | package | test_report | security_report | build_output | other
    origin: str
    version: str = "0.0.0"
    digest: str | None = None
    path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    evidence_ids: list[str] = field(default_factory=list)
    status: str = "created"
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def digest_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()


@dataclass
class Build:
    id: str
    changeset_id: str
    environment: EnvironmentName
    inputs: dict[str, Any] = field(default_factory=dict)
    commands: list[str] = field(default_factory=list)
    artifact_ids: list[str] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    status: BuildStatus = "pending"
    duration_seconds: float = 0.0
    failure_reason: str | None = None
    started_at: float | None = None
    ended_at: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def mark_succeeded(self, *, evidence: list[dict[str, Any]], artifact_ids: list[str]) -> None:
        if not evidence:
            raise ValueError("build cannot succeed without evidence")
        self.status = "succeeded"
        self.evidence.extend(evidence)
        self.artifact_ids.extend(artifact_ids)
        self.ended_at = time.time()


@dataclass
class ValidationRun:
    id: str
    kind: str  # unit | integration | contract | static | security | lint | typecheck | build | custom
    build_id: str | None = None
    changeset_id: str | None = None
    status: ValidationStatus = "NOT_RUN"
    command: str | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    duration_seconds: float = 0.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PipelineStep:
    id: str
    type: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    risk: RiskLevel = "low"
    timeout_seconds: int = 120
    max_retries: int = 1
    evidence_requirements: list[str] = field(default_factory=list)
    gate: str | None = None
    requires_human: bool = False
    executor_kind: str = "validator"  # agent | validator | human

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Pipeline:
    id: str
    name: str
    steps: list[PipelineStep] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "steps": [s.to_dict() for s in self.steps],
            "notes": self.notes,
        }

    def ordered_steps(self) -> list[PipelineStep]:
        """Topological-ish order by depends_on (stable, no cycles assumed)."""
        by_id = {s.id: s for s in self.steps}
        seen: list[str] = []
        visiting: set[str] = set()

        def visit(sid: str) -> None:
            if sid in seen:
                return
            if sid in visiting:
                raise ValueError(f"pipeline cycle at {sid}")
            visiting.add(sid)
            step = by_id[sid]
            for dep in step.depends_on:
                if dep in by_id:
                    visit(dep)
            visiting.remove(sid)
            seen.append(sid)

        for s in self.steps:
            visit(s.id)
        return [by_id[i] for i in seen]


@dataclass
class Environment:
    name: EnvironmentName
    risk_level: RiskLevel
    allowed_actions: list[str] = field(default_factory=list)
    required_gates: list[str] = field(default_factory=list)
    approval_policy: str = "none"  # none | optional | required

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_ENVIRONMENTS: dict[str, Environment] = {
    "local": Environment("local", "low", ["build", "test", "package"], ["tests"], "none"),
    "development": Environment("development", "low", ["build", "test", "package"], ["tests"], "none"),
    "test": Environment("test", "medium", ["build", "test", "package"], ["tests", "security"], "optional"),
    "staging": Environment(
        "staging", "medium", ["build", "test", "package", "release"], ["tests", "security", "artifact"], "optional"
    ),
    "production": Environment(
        "production",
        "critical",
        ["build", "test", "package", "release"],
        ["tests", "security", "artifact", "approval"],
        "required",
    ),
}


@dataclass
class ReleaseCandidate:
    id: str
    version: str
    changeset_id: str
    artifact_ids: list[str] = field(default_factory=list)
    validation_ids: list[str] = field(default_factory=list)
    gate_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    target_environment: EnvironmentName = "local"
    status: str = "draft"
    decisions: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DeliveryRecord:
    id: str
    project_id: str
    changeset_id: str
    status: DeliveryStatus = "draft"
    build_id: str | None = None
    artifact_ids: list[str] = field(default_factory=list)
    validation_ids: list[str] = field(default_factory=list)
    release_candidate_id: str | None = None
    environment: EnvironmentName = "local"
    risk: RiskLevel = "low"
    readiness: str = "READY_FOR_BUILD"
    evidence: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)
    approvals: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def new_delivery_id(project_id: str) -> str:
    return _id("delivery")


def new_build_id() -> str:
    return _id("build")


def new_artifact_id(kind: str) -> str:
    return f"eos.dartifact.{kind}.{uuid.uuid4().hex[:10]}"


def new_validation_id(kind: str) -> str:
    return f"eos.validation.{kind}.{uuid.uuid4().hex[:10]}"


def new_rc_id() -> str:
    return _id("rc")


def default_pipeline() -> Pipeline:
    return Pipeline(
        id="eos.pipeline.default",
        name="source-build-test-security-artifact-readiness",
        steps=[
            PipelineStep("source", "source", outputs=["changeset"], permissions=["DELIVERY_READ"], risk="low"),
            PipelineStep(
                "build",
                "build",
                inputs=["changeset"],
                outputs=["build"],
                depends_on=["source"],
                permissions=["BUILD_EXECUTE"],
                risk="low",
                gate="build",
            ),
            PipelineStep(
                "test",
                "test",
                inputs=["build"],
                outputs=["validation"],
                depends_on=["build"],
                permissions=["BUILD_EXECUTE"],
                risk="low",
                gate="tests",
                evidence_requirements=["tests"],
            ),
            PipelineStep(
                "security",
                "security",
                inputs=["changeset"],
                outputs=["validation"],
                depends_on=["source"],
                permissions=["DELIVERY_READ"],
                risk="medium",
                gate="security",
                evidence_requirements=["security"],
            ),
            PipelineStep(
                "artifact",
                "artifact",
                inputs=["build", "validation"],
                outputs=["artifact"],
                depends_on=["build", "test"],
                permissions=["ARTIFACT_CREATE"],
                risk="low",
                gate="artifact",
            ),
            PipelineStep(
                "release_readiness",
                "release_readiness",
                inputs=["artifact", "validation"],
                outputs=["release_candidate"],
                depends_on=["artifact", "test", "security"],
                permissions=["RELEASE_CREATE"],
                risk="medium",
                gate="release",
                requires_human=False,
            ),
        ],
        notes=["Declarative default pipeline; order derived from depends_on."],
    )
