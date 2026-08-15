"""ChangeSet — tracked workspace mutations from an Agent run."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ChangeSet:
    id: str
    agent_id: str
    task_id: str
    created_files: list[str] = field(default_factory=list)
    modified_files: list[str] = field(default_factory=list)
    deleted_files: list[str] = field(default_factory=list)
    diffs: dict[str, dict[str, str | None]] = field(default_factory=dict)
    tests_run: list[dict[str, Any]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    artifact_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def record_write(self, path: str, before: str | None, after: str) -> None:
        if before is None:
            if path not in self.created_files:
                self.created_files.append(path)
        else:
            if path not in self.modified_files:
                self.modified_files.append(path)
        self.diffs[path] = {"before": before, "after": after}
