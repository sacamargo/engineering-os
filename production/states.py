"""ProductionOperation state machine — no ambiguous transitions."""

from __future__ import annotations

ALLOWED: dict[str, set[str]] = {
    "planned": {"validating", "cancelled"},
    "validating": {"awaiting_approval", "failed", "needs_human", "cancelled"},
    "awaiting_approval": {"deploying", "failed", "cancelled", "needs_human"},
    "deploying": {"verifying", "failed", "needs_human"},
    "verifying": {"succeeded", "degraded", "rollback_required", "needs_human", "failed"},
    "succeeded": set(),
    "failed": {"rollback_required", "needs_human", "cancelled"},
    "degraded": {"rollback_required", "needs_human", "verifying"},
    "rollback_required": {"rolling_back", "needs_human"},
    "rolling_back": {"rolled_back", "failed", "needs_human"},
    "rolled_back": set(),
    "needs_human": {"awaiting_approval", "rolling_back", "cancelled"},
    "cancelled": set(),
}

# Explicit prohibitions
FORBIDDEN = {
    ("failed", "succeeded"),
    ("planned", "succeeded"),
    ("deploying", "succeeded"),  # must verify
    ("verifying", "succeeded"),  # only if health known healthy — enforced in loop, not raw transition alone
}


def can_transition(current: str, new: str) -> bool:
    if (current, new) in FORBIDDEN and new == "succeeded" and current != "verifying":
        return False
    return new in ALLOWED.get(current, set())


def assert_transition(current: str, new: str) -> None:
    if not can_transition(current, new):
        raise ValueError(f"illegal ProductionOperation transition: {current} → {new}")


def mark_succeeded_allowed(*, health: str) -> bool:
    """UNKNOWN/degraded/unhealthy must never become succeeded."""
    return health == "healthy"
