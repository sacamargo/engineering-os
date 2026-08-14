"""Agent boundary — assignment hints only, no agent fleet."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

ExecutorType = Literal["human", "ai_agent", "automation", "external_system"]


@dataclass
class AgentAssignment:
    task_id: str
    executor_type: ExecutorType
    role_ids: list[str]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def suggest_executor(task: dict[str, Any]) -> AgentAssignment:
    if task.get("requires_professional_approval"):
        return AgentAssignment(
            task_id=task["id"],
            executor_type="human",
            role_ids=list(task.get("role_ids") or []),
            reason="professional validation required",
        )
    if task.get("status") == "blocked":
        return AgentAssignment(
            task_id=task["id"],
            executor_type="human",
            role_ids=list(task.get("role_ids") or []),
            reason="blocked on coverage/escalation",
        )
    return AgentAssignment(
        task_id=task["id"],
        executor_type="ai_agent",
        role_ids=list(task.get("role_ids") or []),
        reason="planning-time suggestion only; no agent runtime in Phase 4",
    )
