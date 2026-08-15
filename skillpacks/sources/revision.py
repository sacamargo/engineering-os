"""Immutable source revisions — never silent overwrite."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from skillpacks.sources.model import SkillSource


def load_revisions(revisions_dir: Path, source_id: str) -> list[dict[str, Any]]:
    path = revisions_dir / f"{source_id}.json"
    if not path.is_file():
        return []
    return list(json.loads(path.read_text(encoding="utf-8")).get("revisions") or [])


def append_revision(
    source: SkillSource,
    digest: str,
    revisions_dir: Path,
    *,
    create_new: bool = True,
) -> SkillSource:
    revisions_dir.mkdir(parents=True, exist_ok=True)
    path = revisions_dir / f"{source.source_id}.json"
    history = load_revisions(revisions_dir, source.source_id)
    if create_new and history:
        parent = source.source_id
        source.revision = int(history[-1].get("revision", 1)) + 1
        source.parent_source_id = parent
        # Keep same source_id family; revision number tracks history
    source.content_hash = digest
    source.retrieved_at = time.time()
    if source.status not in {"ingested", "normalized", "active"}:
        source.status = "ingested"
    entry = {
        "revision": source.revision,
        "content_hash": digest,
        "version": source.version,
        "retrieved_at": source.retrieved_at,
        "locator": source.locator,
        "parent_source_id": source.parent_source_id,
    }
    # Avoid duplicate consecutive identical hashes
    if history and history[-1].get("content_hash") == digest:
        return source
    history.append(entry)
    path.write_text(json.dumps({"source_id": source.source_id, "revisions": history}, indent=2), encoding="utf-8")
    return source
