"""Incident → orchestration work items (Incident ≠ Capability ≠ Skill)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from production.incident import Incident, SEVERITY_POLICY


@dataclass
class OpsWorkItem:
    kind: str  # investigation | rollback | remediation | human_escalation | replan
    title: str
    incident_id: str
    priority: str
    requires_human: bool
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def incident_to_orchestration(incident: Incident) -> list[OpsWorkItem]:
    policy = SEVERITY_POLICY.get(incident.severity, {})
    items: list[OpsWorkItem] = [
        OpsWorkItem(
            "investigation",
            f"Investigate {incident.id}",
            incident.id,
            incident.severity,
            bool(policy.get("human_required")),
            {"symptoms": incident.symptoms, "source": incident.source},
        )
    ]
    if incident.deployment_reference:
        items.append(
            OpsWorkItem(
                "rollback",
                f"Evaluate rollback for {incident.deployment_reference}",
                incident.id,
                incident.severity,
                True,
                {"deployment_reference": incident.deployment_reference},
            )
        )
    items.append(
        OpsWorkItem(
            "remediation",
            f"Remediate {incident.affected_service}",
            incident.id,
            incident.severity,
            bool(policy.get("human_required")),
        )
    )
    if policy.get("human_required") or incident.status == "needs_human":
        items.append(
            OpsWorkItem(
                "human_escalation",
                f"Escalate {incident.severity} incident",
                incident.id,
                incident.severity,
                True,
                {"escalation": policy.get("escalation")},
            )
        )
    items.append(
        OpsWorkItem(
            "replan",
            f"Replan after incident {incident.id}",
            incident.id,
            incident.severity,
            False,
            {"note": "Incident ≠ Capability; structured ops work only"},
        )
    )
    return items
