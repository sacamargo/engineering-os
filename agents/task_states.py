"""Map Agent lifecycle onto Task execution states (no parallel mega-enum)."""

from __future__ import annotations

from typing import Final

from agents.lifecycle import can_transition as agent_can_transition

# Task states from foundation/TASK-MODEL.md + validating for gate phase
TASK_STATES: Final[frozenset[str]] = frozenset(
    {
        "pending",
        "ready",
        "assigned",
        "in_progress",
        "validating",
        "blocked",
        "completed",
        "failed",
        "cancelled",
    }
)

TASK_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "pending": frozenset({"ready", "cancelled"}),
    "ready": frozenset({"assigned", "blocked", "cancelled"}),
    "assigned": frozenset({"in_progress", "blocked", "cancelled"}),
    "in_progress": frozenset({"validating", "blocked", "failed", "cancelled"}),
    "validating": frozenset({"completed", "failed", "in_progress", "blocked"}),
    "blocked": frozenset({"ready", "assigned", "cancelled", "failed"}),
    "completed": frozenset(),
    "failed": frozenset({"ready"}),  # retry path only via explicit re-ready
    "cancelled": frozenset(),
}


class InvalidTaskTransition(ValueError):
    pass


def can_task_transition(from_state: str, to_state: str) -> bool:
    if from_state not in TASK_STATES or to_state not in TASK_STATES:
        return False
    return to_state in TASK_TRANSITIONS.get(from_state, frozenset())


def transition_task(from_state: str, to_state: str) -> str:
    if not can_task_transition(from_state, to_state):
        raise InvalidTaskTransition(f"invalid task transition {from_state!r} → {to_state!r}")
    return to_state


# Agent status → suggested task status (coordination hints, not automatic)
AGENT_TO_TASK: Final[dict[str, str]] = {
    "created": "assigned",
    "ready": "assigned",
    "running": "in_progress",
    "waiting": "in_progress",
    "blocked": "blocked",
    "succeeded": "validating",  # still needs gate — not auto-completed
    "failed": "failed",
    "cancelled": "cancelled",
    "escalated": "blocked",
}


def task_status_for_agent(agent_status: str) -> str:
    return AGENT_TO_TASK.get(agent_status, "in_progress")


def assert_agent_task_pair_legal(agent_from: str, agent_to: str, task_from: str, task_to: str) -> None:
    """Both machines must independently allow their transitions."""
    if not agent_can_transition(agent_from, agent_to):
        raise InvalidTaskTransition(f"agent transition illegal: {agent_from}→{agent_to}")
    if not can_task_transition(task_from, task_to):
        raise InvalidTaskTransition(f"task transition illegal: {task_from}→{task_to}")
