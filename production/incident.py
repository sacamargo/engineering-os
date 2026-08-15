"""Incident and Alert models — distinct concepts."""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

IncidentStatus = Literal["detected", "triaging", "mitigating", "monitoring", "resolved", "needs_human"]
Severity = Literal["SEV1", "SEV2", "SEV3", "SEV4"]


SEVERITY_POLICY: dict[str, dict[str, Any]] = {
    "SEV1": {
        "response": "immediate",
        "escalation": "page_oncall",
        "automation_limits": ["no_auto_close"],
        "human_required": True,
    },
    "SEV2": {
        "response": "urgent",
        "escalation": "notify_oncall",
        "automation_limits": ["limited_auto_rollback_if_policy"],
        "human_required": True,
    },
    "SEV3": {
        "response": "normal",
        "escalation": "ticket",
        "automation_limits": [],
        "human_required": False,
    },
    "SEV4": {
        "response": "low",
        "escalation": "backlog",
        "automation_limits": [],
        "human_required": False,
    },
}


INCIDENT_TRANSITIONS: dict[str, set[str]] = {
    "detected": {"triaging", "needs_human"},
    "triaging": {"mitigating", "needs_human", "monitoring"},
    "mitigating": {"monitoring", "needs_human"},
    "monitoring": {"resolved", "mitigating", "needs_human"},
    "needs_human": {"triaging", "mitigating"},
    "resolved": set(),
}


@dataclass
class Alert:
    id: str
    title: str
    severity: Severity
    environment: str
    status: str = "open"  # open | resolved | discarded | promoted_incident
    evidence: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Incident:
    id: str
    severity: Severity
    environment: str
    affected_service: str
    detected_at: float
    source: str
    symptoms: list[str] = field(default_factory=list)
    deployment_reference: str | None = None
    status: IncidentStatus = "detected"
    owner: str | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    resolution: str | None = None
    timeline: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def new_incident(**kwargs: Any) -> Incident:
    return Incident(
        id=kwargs.get("id") or f"eos.incident.{uuid.uuid4().hex[:10]}",
        severity=kwargs.get("severity", "SEV3"),
        environment=kwargs["environment"],
        affected_service=kwargs["affected_service"],
        detected_at=kwargs.get("detected_at", time.time()),
        source=kwargs.get("source", "health"),
        symptoms=list(kwargs.get("symptoms") or []),
        deployment_reference=kwargs.get("deployment_reference"),
    )


def transition_incident(inc: Incident, new_status: IncidentStatus) -> None:
    if new_status not in INCIDENT_TRANSITIONS.get(inc.status, set()):
        raise ValueError(f"illegal incident transition {inc.status} → {new_status}")
    if new_status == "resolved" and not inc.resolution and not inc.evidence:
        raise ValueError("cannot resolve incident without resolution evidence")
    inc.timeline.append({"from": inc.status, "to": new_status, "ts": time.time()})
    inc.status = new_status


def alert_to_incident(alert: Alert, *, service: str) -> Incident:
    alert.status = "promoted_incident"
    return new_incident(
        severity=alert.severity,
        environment=alert.environment,
        affected_service=service,
        source="alert",
        symptoms=[alert.title],
    )
