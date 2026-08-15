"""Abstract deployment strategies — no vendor implementation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Strategy = Literal["canary", "staged", "blue_green", "full"]


@dataclass
class DeploymentStrategy:
    name: Strategy
    description: str
    requires_human_for_production: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


STRATEGIES: dict[str, DeploymentStrategy] = {
    "full": DeploymentStrategy("full", "Full cutover", requires_human_for_production=True),
    "staged": DeploymentStrategy("staged", "Staged rollout", requires_human_for_production=True),
    "canary": DeploymentStrategy("canary", "Canary subset", requires_human_for_production=True),
    "blue_green": DeploymentStrategy("blue_green", "Blue/green swap", requires_human_for_production=True),
}


def select_strategy(*, risk: str, environment: str) -> dict[str, Any]:
    """Policy helper — vendor-neutral. High risk prefers staged/canary representation."""
    if environment == "production" or risk in {"high", "critical"}:
        chosen = "canary" if risk == "critical" else "staged"
        return {
            "strategy": chosen,
            "reason": f"risk={risk} environment={environment}",
            "human_approval": True,
            "representation_only": True,
            "notes": ["strategy is abstract — no cloud provider wired"],
        }
    return {
        "strategy": "full",
        "reason": f"risk={risk} environment={environment}",
        "human_approval": environment in {"staging", "production"},
        "representation_only": True,
    }
