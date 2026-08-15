"""SkillPack status transitions formalized for Phase 8.1."""

from __future__ import annotations

from typing import Literal

SkillPackStatus = Literal["unavailable", "discovered", "verified", "experimental", "active", "stale", "deprecated", "rejected"]

# Allowed edges (from → to)
ALLOWED: dict[str, set[str]] = {
    "unavailable": {"discovered", "unavailable"},
    "discovered": {"verified", "rejected", "unavailable"},
    "verified": {"experimental", "rejected", "unavailable"},
    "experimental": {"active", "stale", "deprecated", "unavailable"},
    "active": {"stale", "deprecated"},
    "stale": {"verified", "experimental", "deprecated", "unavailable"},  # reverify path
    "deprecated": {"unavailable"},
    "rejected": {"unavailable", "discovered"},
}


def can_transition_skillpack_status(current: str, new: str) -> bool:
    return new in ALLOWED.get(current, set())


def assert_transition(current: str, new: str) -> None:
    if not can_transition_skillpack_status(current, new):
        raise ValueError(f"illegal SkillPack status transition: {current} → {new}")
