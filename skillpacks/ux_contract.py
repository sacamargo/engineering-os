"""UX/UI conceptual output contract — structured artifacts, not images."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


UX_ARTIFACT_KINDS = [
    "personas_actors",
    "journeys",
    "information_architecture",
    "navigation_model",
    "screen_inventory",
    "interaction_flows",
    "states",
    "empty_states",
    "loading_states",
    "error_states",
    "permission_states",
    "responsive_behavior",
    "accessibility_requirements",
    "design_tokens",
    "component_inventory",
    "design_system_requirements",
    "ux_acceptance_criteria",
    "platform_targets",
]


@dataclass
class PlatformTargets:
    ios: str = "UNKNOWN"  # REQUIRED | OPTIONAL | NOT_REQUIRED | UNKNOWN
    android: str = "UNKNOWN"
    web: str = "UNKNOWN"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def ux_output_skeleton(utterance: str) -> dict[str, Any]:
    """Produce structured UX artifact slots; do not invent filled product details."""
    u = utterance.lower()
    platforms = PlatformTargets(
        ios="REQUIRED" if "ios" in u else "UNKNOWN",
        android="REQUIRED" if "android" in u else "UNKNOWN",
        web="REQUIRED" if "web" in u else "UNKNOWN",
        notes=[
            "Responsive web ≠ native mobile app",
            "Shared design language UNKNOWN until decided",
            "Platform-specific permissions/notifications UNKNOWN until product requires them",
        ],
    )
    artifacts = {
        kind: {"status": "UNKNOWN", "content": None, "notes": ["Not invented — NEEDS_INPUT or discovery"]}
        for kind in UX_ARTIFACT_KINDS
    }
    artifacts["platform_targets"] = {"status": "PARTIAL", "content": platforms.to_dict()}
    return {
        "skill_id": "eos.skillpack.design.ui-ux-pro-max",
        "skill_status": "unavailable",
        "mode": "DESIGN",
        "artifacts": artifacts,
        "epistemic": {
            "KNOWN": ["iOS/Android/Web mentioned in acceptance criteria"] if ("ios" in u or "android" in u or "web" in u) else [],
            "INFERRED": [],
            "UNKNOWN": ["users", "journeys", "payments", "hardware", "branding", "stack"],
            "NEEDS_INPUT": ["primary user jobs", "must-have flows"],
            "NEEDS_HUMAN": [],
        },
        "notes": [
            "UI UX PRO MAX source unavailable — skeleton only, no fabricated methodology",
            "Artifacts are contracts for Agents to fill with evidence",
        ],
    }
