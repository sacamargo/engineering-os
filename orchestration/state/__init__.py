"""Project state transition validation against Phase 3 EXECUTION-STATE-MACHINE."""

from __future__ import annotations

ALLOWED = {
    "discovered": {"planned", "cancelled"},
    "planned": {"ready", "blocked", "cancelled"},
    "ready": {"executing", "blocked", "cancelled"},
    "executing": {"blocked", "validating", "failed", "cancelled"},
    "blocked": {"ready", "executing", "planned", "failed", "cancelled"},
    "validating": {"completed", "blocked", "failed", "executing"},
    "completed": set(),
    "failed": {"planned", "cancelled"},
    "cancelled": set(),
}

# Planning vocabulary aliases → Phase 3 statuses
ALIASES = {
    "draft": "discovered",
    "running": "executing",
    "waiting_human": "blocked",
    "replanning": "planned",
}


def normalize_status(status: str) -> str:
    return ALIASES.get(status, status)


def can_transition(current: str, new: str) -> bool:
    cur = normalize_status(current)
    nxt = normalize_status(new)
    if cur == nxt:
        return True
    return nxt in ALLOWED.get(cur, set())


def assert_transition(current: str, new: str) -> None:
    if not can_transition(current, new):
        raise ValueError(f"invalid project transition {current} -> {new}")
