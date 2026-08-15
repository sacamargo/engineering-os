"""Vendor-neutral DeploymentAdapter contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


@dataclass
class AdapterRequest:
    operation_id: str
    target: dict[str, Any]
    environment: str
    artifact_id: str
    dry_run: bool = False
    previous_version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AdapterResult:
    status: str
    message: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    health_hint: str | None = None
    adapter: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DeploymentAdapter(Protocol):
    name: str

    def validate(self, request: AdapterRequest) -> AdapterResult: ...

    def deploy(self, request: AdapterRequest) -> AdapterResult: ...

    def status(self, request: AdapterRequest) -> AdapterResult: ...

    def health(self, request: AdapterRequest) -> AdapterResult: ...

    def rollback(self, request: AdapterRequest) -> AdapterResult: ...
