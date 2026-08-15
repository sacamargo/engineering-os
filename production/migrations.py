"""Database migration safety policy."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

MigrationClass = Literal["backward_compatible", "destructive", "irreversible", "unknown"]


@dataclass
class MigrationPolicyDecision:
    classification: MigrationClass
    human_required: bool
    deploy_allowed: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_migration(
    *,
    classification: MigrationClass,
    environment: str,
) -> MigrationPolicyDecision:
    if classification == "unknown":
        return MigrationPolicyDecision(
            classification,
            human_required=True,
            deploy_allowed=False,
            notes=["UNKNOWN migration ≠ safe"],
        )
    if classification in {"destructive", "irreversible"} and environment == "production":
        return MigrationPolicyDecision(
            classification,
            human_required=True,
            deploy_allowed=False,
            notes=["HUMAN_REQUIRED for destructive/irreversible production migrations"],
        )
    if classification in {"destructive", "irreversible"}:
        return MigrationPolicyDecision(
            classification,
            human_required=True,
            deploy_allowed=environment in {"local", "development", "test"},
            notes=["destructive migration requires human"],
        )
    return MigrationPolicyDecision(classification, human_required=False, deploy_allowed=True)
