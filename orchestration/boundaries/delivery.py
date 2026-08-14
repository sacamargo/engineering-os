"""Delivery boundary — plan toward delivery without CI/CD runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DeliveryPlanStub:
    project_id: str
    stages: list[str] = field(
        default_factory=lambda: ["plan", "delivery_plan", "deployment", "release", "production"]
    )
    status: str = "not_started"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def delivery_boundary(project_id: str) -> DeliveryPlanStub:
    return DeliveryPlanStub(
        project_id=project_id,
        notes=["Delivery runtime not implemented in Phase 4; boundary only."],
    )
