"""Codebase Intelligence boundary — interfaces only, no indexer."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


@dataclass
class RepositorySnapshot:
    root: str
    files: list[str] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    conventions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CodebaseIntelligence(Protocol):
    def inspect(self, root: str) -> RepositorySnapshot: ...


class NullCodebaseIntelligence:
    """Phase 4 stub: returns an empty snapshot and explicit limitation."""

    def inspect(self, root: str) -> RepositorySnapshot:
        return RepositorySnapshot(
            root=root,
            notes=["Codebase Intelligence runtime not implemented; boundary only."],
        )
