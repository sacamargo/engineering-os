"""Staleness detection — active Skill whose source changed becomes stale (no silent update)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from skillpacks.sources.model import content_hash
from skillpacks.sources.revision import load_revisions


def detect_staleness(
    *,
    source_id: str,
    locator: str,
    pinned_hash: str,
    repo_root: Path,
    revisions_dir: Path | None = None,
) -> dict[str, Any]:
    path = Path(locator)
    if not path.is_absolute():
        path = repo_root / locator
    if not path.is_file():
        return {"stale": True, "reason": "locator_missing", "action": "reverify"}
    current = content_hash(path.read_bytes())
    if current != pinned_hash:
        return {
            "stale": True,
            "reason": "content_hash_mismatch",
            "pinned_hash": pinned_hash,
            "current_hash": current,
            "action": "stale→reverify→reingest→reactivate",
        }
    return {"stale": False, "reason": "hash_matches", "content_hash": current}
