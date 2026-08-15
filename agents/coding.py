"""Deterministic coding agent — no LLM required."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from agents.invocation import ToolInvocation, ToolResult
from agents.runtime import LocalToolRuntime


InstructionHandler = Callable[[LocalToolRuntime, dict[str, Any]], list[ToolResult]]


@dataclass
class DeterministicPlan:
    """Explicit steps the coding agent executes without an LLM."""

    steps: list[dict[str, Any]]


def run_deterministic(runtime: LocalToolRuntime, plan: DeterministicPlan) -> list[ToolResult]:
    results: list[ToolResult] = []
    task_id = runtime.instance.task_id or "unknown"
    agent_id = runtime.instance.id
    for step in plan.steps:
        inv = ToolInvocation(
            tool_id=step["tool"],
            arguments=dict(step.get("arguments") or {}),
            task_id=task_id,
            agent_id=agent_id,
        )
        result = runtime.invoke(inv)
        results.append(result)
        if not result.success and not step.get("continue_on_error"):
            break
    return results
