"""Deployment boundary — READY_FOR_DEPLOYMENT only; no real deploy in core."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


@dataclass
class DeploymentRequest:
    release_candidate_id: str
    environment: str
    artifact_ids: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DeploymentBoundaryResult:
    status: str  # READY_FOR_DEPLOYMENT | NOT_READY | UNSUPPORTED
    reason: str
    adapter: str = "none"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DeploymentAdapter(Protocol):
    def status(self, request: DeploymentRequest) -> DeploymentBoundaryResult: ...

    def deploy(self, request: DeploymentRequest) -> DeploymentBoundaryResult: ...


class NullDeploymentAdapter:
    """Core-safe stub — never deploys."""

    def status(self, request: DeploymentRequest) -> DeploymentBoundaryResult:
        return DeploymentBoundaryResult(
            "READY_FOR_DEPLOYMENT",
            "Candidate marked ready; no deployment executed (boundary).",
            adapter="null",
        )

    def deploy(self, request: DeploymentRequest) -> DeploymentBoundaryResult:
        return DeploymentBoundaryResult(
            "UNSUPPORTED",
            "Core forbids real deployment; bind an external DeploymentAdapter.",
            adapter="null",
        )
