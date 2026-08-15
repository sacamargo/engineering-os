"""Agent lifecycle state machine — strict transitions only."""

from __future__ import annotations

from typing import Final

# created → ready → running ⇄ waiting
#                          ↘ blocked → escalated
#                          ↘ succeeded | failed | cancelled

AGENT_STATES: Final[frozenset[str]] = frozenset(
    {
        "created",
        "ready",
        "running",
        "waiting",
        "blocked",
        "succeeded",
        "failed",
        "cancelled",
        "escalated",
    }
)

ALLOWED_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "created": frozenset({"ready", "cancelled"}),
    "ready": frozenset({"running", "cancelled", "blocked"}),
    "running": frozenset({"waiting", "blocked", "succeeded", "failed", "cancelled"}),
    "waiting": frozenset({"running", "blocked", "cancelled", "failed"}),
    "blocked": frozenset({"ready", "escalated", "cancelled", "failed"}),
    "succeeded": frozenset(),
    "failed": frozenset(),
    "cancelled": frozenset(),
    "escalated": frozenset(),
}

TERMINAL: Final[frozenset[str]] = frozenset({"succeeded", "failed", "cancelled", "escalated"})


class InvalidAgentTransition(ValueError):
    pass


def can_transition(from_state: str, to_state: str) -> bool:
    if from_state not in AGENT_STATES or to_state not in AGENT_STATES:
        return False
    return to_state in ALLOWED_TRANSITIONS.get(from_state, frozenset())


def transition(from_state: str, to_state: str, *, reason: str = "") -> str:
    if not can_transition(from_state, to_state):
        raise InvalidAgentTransition(
            f"invalid agent transition {from_state!r} → {to_state!r}"
            + (f" ({reason})" if reason else "")
        )
    return to_state


def is_terminal(state: str) -> bool:
    return state in TERMINAL
