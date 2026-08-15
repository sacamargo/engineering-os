"""Cancellation — stop agent/task without leaving inconsistent claims of success."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from agents.lifecycle import is_terminal, transition


@dataclass
class CancelResult:
    agent_status: str
    task_status: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def cancel_agent(current_status: str, *, reason: str = "cancelled by operator") -> str:
    if is_terminal(current_status):
        return current_status
    if current_status in {"created", "ready", "running", "waiting", "blocked"}:
        return transition(current_status, "cancelled", reason=reason)
    return current_status


def cancel_execution(agent_status: str, task_status: str, *, reason: str = "cancelled") -> CancelResult:
    new_agent = cancel_agent(agent_status, reason=reason)
    new_task = task_status
    if task_status in {"pending", "ready", "assigned", "in_progress", "validating", "blocked"}:
        from agents.task_states import transition_task

        try:
            new_task = transition_task(task_status, "cancelled")
        except Exception:
            if task_status != "cancelled":
                # force via allowed edges
                if task_status == "blocked":
                    new_task = transition_task("blocked", "cancelled")
                else:
                    new_task = "cancelled"
    return CancelResult(new_agent, new_task, reason)
