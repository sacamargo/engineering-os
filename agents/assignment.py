"""Task → Agent assignment (Role ≠ Agent)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from agents.model import (
    ANALYSIS_AGENT,
    CODING_AGENT,
    HUMAN_EXECUTOR,
    AgentDefinition,
)


@dataclass
class Assignment:
    task_id: str
    definition: AgentDefinition
    executor_kind: str  # ai_agent | human
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "definition_id": self.definition.id,
            "executor_kind": self.executor_kind,
            "reason": self.reason,
        }


INCOMPATIBLE = ValueError


def assign_agent(task: dict[str, Any]) -> Assignment:
    task_id = task["id"]
    if task.get("requires_professional_approval") or task.get("executor") == "human":
        return Assignment(task_id, HUMAN_EXECUTOR, "human", "professional/human executor required")
    kind = task.get("task_kind") or ""
    title = (task.get("title") or "").lower()
    if kind == "codebase_analysis" or "analy" in title:
        return Assignment(task_id, ANALYSIS_AGENT, "ai_agent", "read-only analysis task")
    if kind in {"coding", "bugfix", "implement"} or any(
        w in title for w in ("fix", "add", "implement", "refactor", "código", "code")
    ):
        return Assignment(task_id, CODING_AGENT, "ai_agent", "coding/modification task")
    # default: analysis (least privilege)
    return Assignment(task_id, ANALYSIS_AGENT, "ai_agent", "default least-privilege analysis agent")


def assert_compatible(task: dict[str, Any], definition: AgentDefinition) -> None:
    if task.get("requires_professional_approval") and definition.type != "human":
        raise ValueError("professional task cannot be assigned to non-human agent")
    needed = set(task.get("required_permissions") or [])
    if needed - set(definition.permissions):
        raise ValueError("agent lacks required permissions for task")
