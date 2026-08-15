"""Health model — UNKNOWN never becomes HEALTHY automatically."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

HealthStatus = Literal["healthy", "degraded", "unhealthy", "unknown"]


@dataclass
class HealthCheck:
    id: str
    kind: str  # application | api | database | dependency | error_rate | latency | availability
    required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HealthResult:
    status: HealthStatus
    checks: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def aggregate_health(hints: list[str | None]) -> HealthStatus:
    normalized = [(h or "unknown").lower() for h in hints]
    if not normalized or any(h == "unknown" for h in normalized):
        return "unknown"
    if any(h == "unhealthy" for h in normalized):
        return "unhealthy"
    if any(h == "degraded" for h in normalized):
        return "degraded"
    if all(h == "healthy" for h in normalized):
        return "healthy"
    return "unknown"


def health_allows_success(status: HealthStatus) -> bool:
    return status == "healthy"
