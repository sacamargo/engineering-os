"""Observability consumption — reuse existing evidence; no new metrics system."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ObservabilityBundle:
    logs: list[dict[str, Any]] = field(default_factory=list)
    metrics: list[dict[str, Any]] = field(default_factory=list)
    traces: list[dict[str, Any]] = field(default_factory=list)
    health_checks: list[dict[str, Any]] = field(default_factory=list)
    alerts: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def consume_observability(sources: dict[str, Any] | None) -> ObservabilityBundle:
    """Accept whatever Phase 7/8 already produced; do not invent metrics."""
    if not sources:
        return ObservabilityBundle(evidence=[{"kind": "observability_absent"}])
    return ObservabilityBundle(
        logs=list(sources.get("logs") or []),
        metrics=list(sources.get("metrics") or []),
        traces=list(sources.get("traces") or []),
        health_checks=list(sources.get("health_checks") or []),
        alerts=list(sources.get("alerts") or []),
        evidence=list(sources.get("evidence") or [{"kind": "observability_consumed"}]),
    )
