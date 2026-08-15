"""Change impact for production — UNKNOWN ≠ LOW RISK."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

ImpactLevel = Literal["low", "medium", "high", "critical", "unknown"]


@dataclass
class ChangeImpactAssessment:
    affected_modules: list[str] = field(default_factory=list)
    affected_services: list[str] = field(default_factory=list)
    affected_database: bool = False
    affected_api: bool = False
    affected_clients: list[str] = field(default_factory=list)
    affected_environments: list[str] = field(default_factory=list)
    level: ImpactLevel = "unknown"
    evidence: list[dict[str, Any]] = field(default_factory=list)
    source: str = "codebase_intelligence"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def assess_change_impact(codebase_evidence: dict[str, Any] | None) -> ChangeImpactAssessment:
    if not codebase_evidence:
        return ChangeImpactAssessment(
            level="unknown",
            evidence=[{"kind": "UNKNOWN", "note": "missing codebase evidence ≠ LOW RISK"}],
        )
    level = str(codebase_evidence.get("impact_level") or "unknown").lower()
    if level not in {"low", "medium", "high", "critical", "unknown"}:
        level = "unknown"
    return ChangeImpactAssessment(
        affected_modules=list(codebase_evidence.get("modules") or []),
        affected_services=list(codebase_evidence.get("services") or []),
        affected_database=bool(codebase_evidence.get("database")),
        affected_api=bool(codebase_evidence.get("api")),
        affected_clients=list(codebase_evidence.get("clients") or []),
        affected_environments=list(codebase_evidence.get("environments") or []),
        level=level,  # type: ignore[arg-type]
        evidence=list(codebase_evidence.get("evidence") or [{"kind": "codebase_impact"}]),
        source=str(codebase_evidence.get("source") or "codebase_intelligence"),
    )
