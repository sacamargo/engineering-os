"""PlanningResult DTO — kept out of facade module to preserve thin coordinator LOC."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlanningResult:
    intent: dict[str, Any]
    capability_resolution: dict[str, Any]
    arbitration: dict[str, Any]
    skill_resolution: dict[str, Any]
    roles: dict[str, Any]
    knowledge: dict[str, Any]
    generated: dict[str, Any]
    dependencies: dict[str, Any]
    gaps: list[dict[str, Any]]
    escalations: list[dict[str, Any]]
    gates: list[dict[str, Any]]
    readiness: dict[str, Any]
    decisions: list[dict[str, Any]]
    executor_suggestions: list[dict[str, Any]]
    delivery: dict[str, Any]
    adapter_policy: dict[str, Any]
    codebase: dict[str, Any]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "capability_resolution": self.capability_resolution,
            "arbitration": self.arbitration,
            "skill_resolution": self.skill_resolution,
            "roles": self.roles,
            "knowledge": self.knowledge,
            "generated": self.generated,
            "dependencies": self.dependencies,
            "gaps": self.gaps,
            "escalations": self.escalations,
            "gates": self.gates,
            "readiness": self.readiness,
            "decisions": self.decisions,
            "executor_suggestions": self.executor_suggestions,
            "delivery": self.delivery,
            "adapter_policy": self.adapter_policy,
            "codebase": self.codebase,
            "notes": self.notes,
        }
