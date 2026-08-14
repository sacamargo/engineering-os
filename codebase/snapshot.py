"""Immutable Codebase Snapshot model."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

Certainty = Literal["observed", "inferred", "unknown"]


@dataclass
class AnalysisError:
    stage: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SnapshotMeta:
    analyzed_at: str
    git_revision: str | None
    git_branch: str | None
    root: str
    included_file_count: int = 0
    excluded_file_count: int = 0
    parsers_used: list[str] = field(default_factory=list)
    tool_version: str = "0.1.0"
    content_fingerprint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CodebaseSnapshot:
    """Immutable analysis result for one repository revision."""

    id: str
    meta: SnapshotMeta
    files: list[dict[str, Any]] = field(default_factory=list)
    directories: list[dict[str, Any]] = field(default_factory=list)
    symbols: list[dict[str, Any]] = field(default_factory=list)
    modules: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[dict[str, Any]] = field(default_factory=list)
    tests: list[dict[str, Any]] = field(default_factory=list)
    configurations: list[dict[str, Any]] = field(default_factory=list)
    architecture_signals: list[dict[str, Any]] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    errors: list[AnalysisError] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    unknowns: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data

    def fingerprint(self) -> str:
        """Stable-ish fingerprint of structural payload (excluding analyzed_at)."""
        payload = {
            "git_revision": self.meta.git_revision,
            "files": sorted(f.get("path", "") for f in self.files),
            "symbols": sorted(s.get("id", "") for s in self.symbols),
            "dependencies": sorted(
                f"{d.get('from')}->{d.get('to')}:{d.get('kind')}" for d in self.dependencies
            ),
            "findings": sorted(f.get("id", "") for f in self.findings),
        }
        blob = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def new_snapshot_id(root: str, revision: str | None) -> str:
    raw = f"{root}|{revision or 'nogit'}|{datetime.now(timezone.utc).isoformat()}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"eos.snapshot.{digest}"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
