"""Production permissions — deny by default."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

PRODUCTION_PERMISSIONS = frozenset(
    {
        "PRODUCTION_READ",
        "PRODUCTION_DEPLOY",
        "PRODUCTION_ROLLBACK",
        "PRODUCTION_CONFIG_READ",
        "PRODUCTION_CONFIG_WRITE",
        "PRODUCTION_INCIDENT_MANAGE",
    }
)

PROFILES: dict[str, frozenset[str]] = {
    "observer": frozenset({"PRODUCTION_READ"}),
    "deployer": frozenset({"PRODUCTION_READ", "PRODUCTION_DEPLOY"}),
    "responder": frozenset({"PRODUCTION_READ", "PRODUCTION_ROLLBACK", "PRODUCTION_INCIDENT_MANAGE"}),
    "human_approver": frozenset({"PRODUCTION_READ"}),
    "agent": frozenset({"PRODUCTION_READ"}),  # never deploy/rollback by default
}


@dataclass
class PermDecision:
    allowed: bool
    missing: list[str]
    reason: str


def authorize(granted: Iterable[str], required: Iterable[str]) -> PermDecision:
    g = set(granted)
    missing = [p for p in required if p not in g]
    if missing:
        return PermDecision(False, missing, "deny-by-default: missing permissions")
    return PermDecision(True, [], "authorized")
