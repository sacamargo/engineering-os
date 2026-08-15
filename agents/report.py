"""Human-readable execution report."""

from __future__ import annotations

from agents.loop import ExecutionResult


def render_execution_report(result: ExecutionResult) -> str:
    lines = [
        "# Agent Execution Report",
        "",
        f"- Execution: `{result.execution_id}`",
        f"- Status: **{result.status}**",
        f"- Task: `{result.task.get('id')}` — {result.task.get('title')}",
        f"- Agent: `{result.agent.get('definition_id')}` ({result.agent.get('executor_kind')})",
        "",
        "## Evidence",
    ]
    for e in result.evidence[:40]:
        lines.append(f"- [{e.get('kind')}] {e.get('claim')} → `{e.get('pointer')}`")
    if not result.evidence:
        lines.append("- none")
    lines.append("")
    lines.append("## Changes")
    if result.changeset:
        lines.append(f"- ChangeSet: `{result.changeset.get('id')}`")
        for p in result.changeset.get("modified_files") or []:
            lines.append(f"- modified: `{p}`")
        for p in result.changeset.get("created_files") or []:
            lines.append(f"- created: `{p}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Failures / Escalations")
    for f in result.failures:
        lines.append(f"- failure: {f}")
    for e in result.escalations:
        lines.append(f"- escalation: {e}")
    if not result.failures and not result.escalations:
        lines.append("- none")
    lines.append("")
    lines.append("## Metrics")
    for k, v in (result.metrics or {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    return "\n".join(lines)
