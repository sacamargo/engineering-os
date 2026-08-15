"""Context building with size bounds — avoid dumping entire repos."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from agents.sandbox import Workspace


@dataclass
class ExecutionContext:
    task: dict[str, Any]
    workspace_root: str
    relevant_files: list[str] = field(default_factory=list)
    snippets: dict[str, str] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    previous_evidence: list[dict[str, Any]] = field(default_factory=list)
    codebase_snapshot_id: str | None = None
    truncated: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_context(
    task: dict[str, Any],
    workspace: Workspace,
    *,
    paths: list[str] | None = None,
    max_bytes: int = 100_000,
    previous_evidence: list[dict[str, Any]] | None = None,
    codebase_snapshot_id: str | None = None,
) -> ExecutionContext:
    ctx = ExecutionContext(
        task=task,
        workspace_root=str(workspace.root),
        constraints=list(task.get("constraints") or []),
        previous_evidence=list(previous_evidence or []),
        codebase_snapshot_id=codebase_snapshot_id,
        notes=["Context is intentionally partial; full repo not loaded."],
    )
    candidates = list(paths or task.get("target_paths") or [])
    if not candidates:
        # minimal: prefer explicit instruction paths only
        ctx.notes.append("No target_paths provided; context limited to task metadata.")
        return ctx

    total = 0
    for rel in candidates[:30]:
        try:
            path = workspace.resolve(rel)
        except Exception:
            continue
        if not path.is_file() or not workspace.may_read(rel):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if total + len(text) > max_bytes:
            remain = max_bytes - total
            if remain <= 0:
                ctx.truncated = True
                break
            text = text[:remain]
            ctx.truncated = True
        ctx.relevant_files.append(rel)
        ctx.snippets[rel] = text
        total += len(text)
        if ctx.truncated:
            break
    return ctx
