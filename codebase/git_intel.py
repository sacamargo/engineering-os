"""Basic Git intelligence for snapshot provenance (not full history analytics)."""

from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class GitInfo:
    available: bool
    root: str
    branch: str | None = None
    commit: str | None = None
    author: str | None = None
    committed_at: str | None = None
    changed_files: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _run(root: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def inspect_git(root: str | Path) -> GitInfo:
    root_path = Path(root).resolve()
    inside = _run(root_path, "rev-parse", "--is-inside-work-tree")
    if inside != "true":
        return GitInfo(
            available=False,
            root=str(root_path),
            notes=["Not a git work tree; snapshot will use git_revision=None."],
        )
    branch = _run(root_path, "rev-parse", "--abbrev-ref", "HEAD")
    commit = _run(root_path, "rev-parse", "HEAD")
    author = _run(root_path, "log", "-1", "--format=%an <%ae>")
    committed_at = _run(root_path, "log", "-1", "--format=%cI")
    changed = _run(root_path, "diff", "--name-only", "HEAD")
    changed_files = [c for c in (changed or "").splitlines() if c][:200]
    return GitInfo(
        available=True,
        root=str(root_path),
        branch=branch,
        commit=commit,
        author=author,
        committed_at=committed_at,
        changed_files=changed_files,
        notes=["Basic git metadata only; not a full historical analysis."],
    )
