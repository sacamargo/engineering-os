"""Human Escalation logic for planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Escalation:
    id: str
    project_id: str
    domain: str
    reason: str
    risk: str
    human_must_provide: str
    blocked: list[str] = field(default_factory=list)
    can_continue_parallel: list[str] = field(default_factory=list)
    status: str = "required"
    blocking: bool = True
    can_reason: bool = True
    can_execute: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_escalations(
    project: dict[str, Any], tasks: list[dict[str, Any]]
) -> list[Escalation]:
    esc: list[Escalation] = []
    pid = project["id"]
    slug = pid.split(".")[-1]
    parallel = [
        t["id"]
        for t in tasks
        if not t.get("requires_professional_approval") and t.get("status") != "blocked"
    ]

    for t in tasks:
        if not t.get("requires_professional_approval"):
            continue
        if "electrical" in t["id"]:
            domain = "electrical_engineering"
        elif "physical" in t["id"]:
            domain = "physical_access_control"
        else:
            domain = "professional"
        esc.append(
            Escalation(
                id=f"eos.escalation.{slug}.{domain.replace('_', '-')}",
                project_id=pid,
                domain=domain,
                reason=t.get("description") or "Professional validation required",
                risk=t.get("risk", "critical"),
                human_must_provide="Licensed/qualified approval before physical execution",
                blocked=[t["id"]],
                can_continue_parallel=parallel,
                status="required",
                blocking=True,
                can_reason=True,
                can_execute=False,
            )
        )

    risks = set(project.get("risk_signals") or [])
    if "production_impact" in risks:
        esc.append(
            Escalation(
                id=f"eos.escalation.{slug}.production-access",
                project_id=pid,
                domain="production_access",
                reason="Production impact signaled; system lacks production authority",
                risk="high",
                human_must_provide="Production access / change approval",
                blocked=[],
                can_continue_parallel=parallel,
                status="required",
                blocking=False,
            )
        )
    return esc
