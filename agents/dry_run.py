"""Dry-run projection of what an execution would do."""

from __future__ import annotations

from typing import Any

from agents.assignment import assign_agent
from agents.coding import DeterministicPlan
from agents.tools import get_tool


def project_dry_run(task: dict[str, Any], plan: DeterministicPlan | None = None) -> dict[str, Any]:
    assignment = assign_agent(task)
    tools = []
    files = []
    gates = []
    for step in (plan.steps if plan else []):
        tool = get_tool(step["tool"])
        tools.append(step["tool"])
        if step["tool"] == "write_file":
            files.append(step.get("arguments", {}).get("path"))
        if tool.requires_approval or tool.risk_level in {"HIGH", "CRITICAL"}:
            gates.append(f"approval:{tool.id}")
    return {
        "dry_run": True,
        "task_id": task.get("id"),
        "agent": assignment.definition.id,
        "tools": tools,
        "files_possibly_modified": [f for f in files if f],
        "permissions_needed": list(assignment.definition.permissions),
        "gates": gates,
        "notes": ["No mutations performed."],
    }
