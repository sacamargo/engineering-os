"""Workspace sandbox — agents cannot escape the authorized root."""

from __future__ import annotations

import os
from pathlib import Path

from codebase.boundary import is_sensitive_path, may_read_content


class WorkspaceEscapeError(PermissionError):
    pass


class Workspace:
    def __init__(self, root: str | Path, *, allow_sensitive_read: bool = False) -> None:
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise NotADirectoryError(str(self.root))
        self.allow_sensitive_read = allow_sensitive_read

    def resolve(self, rel: str) -> Path:
        if rel is None:
            raise WorkspaceEscapeError("path required")
        # Block absolute paths and null bytes
        raw = str(rel)
        if "\x00" in raw:
            raise WorkspaceEscapeError("null byte in path")
        if os.path.isabs(raw):
            raise WorkspaceEscapeError("absolute paths forbidden")
        candidate = (self.root / raw).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise WorkspaceEscapeError(f"path escapes workspace: {rel}") from exc
        return candidate

    def relpath(self, path: Path) -> str:
        return str(path.resolve().relative_to(self.root)).replace("\\", "/")

    def may_read(self, rel: str) -> bool:
        if is_sensitive_path(rel) and not self.allow_sensitive_read:
            return False
        return may_read_content(rel)

    def may_write(self, rel: str) -> bool:
        if is_sensitive_path(rel):
            return False
        # never write outside — resolve enforces
        self.resolve(rel)
        return True
