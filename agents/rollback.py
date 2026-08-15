"""Workspace rollback from ChangeSet / write log."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.changeset import ChangeSet
from agents.sandbox import Workspace


def rollback_changeset(workspace: Workspace, changeset: ChangeSet) -> list[str]:
    restored: list[str] = []
    for path, diff in changeset.diffs.items():
        target = workspace.resolve(path)
        before = diff.get("before")
        if before is None:
            if target.exists():
                target.unlink()
                restored.append(f"deleted:{path}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(str(before), encoding="utf-8")
            restored.append(f"restored:{path}")
    return restored


def rollback_write_log(workspace: Workspace, write_log: list[dict[str, Any]]) -> list[str]:
    cs = ChangeSet(id="tmp", agent_id="", task_id="")
    for w in write_log:
        cs.record_write(w["path"], w.get("before"), w["after"])
    return rollback_changeset(workspace, cs)
