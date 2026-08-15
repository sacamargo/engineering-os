"""Delivery permissions — deny by default."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

DELIVERY_PERMISSIONS = frozenset(
    {
        "DELIVERY_READ",
        "BUILD_EXECUTE",
        "ARTIFACT_CREATE",
        "RELEASE_CREATE",
        "RELEASE_APPROVE",
        "DEPLOY_EXECUTE",
        "ROLLBACK_EXECUTE",
    }
)


# Predefined actor profiles (not Agents with all perms)
PROFILES: dict[str, frozenset[str]] = {
    "analysis": frozenset({"DELIVERY_READ"}),
    "builder": frozenset({"DELIVERY_READ", "BUILD_EXECUTE", "ARTIFACT_CREATE"}),
    "release_engineer": frozenset(
        {"DELIVERY_READ", "BUILD_EXECUTE", "ARTIFACT_CREATE", "RELEASE_CREATE"}
    ),
    "human_approver": frozenset({"DELIVERY_READ", "RELEASE_APPROVE"}),
    # deploy/rollback never granted to automated agents in Phase 7
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
        return PermDecision(False, missing, f"missing delivery permissions: {missing}")
    return PermDecision(True, [], "ok")


def assert_authorized(granted: Iterable[str], required: Iterable[str]) -> None:
    d = authorize(granted, required)
    if not d.allowed:
        raise PermissionError(d.reason)
