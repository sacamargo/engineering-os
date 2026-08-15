"""Skill ↔ Capability / Role binding loaders — associations, not identity."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BINDINGS_DIR = Path(__file__).resolve().parent / "bindings"


def load_capability_bindings(path: Path | None = None) -> dict[str, Any]:
    p = path or (BINDINGS_DIR / "capability_bindings.json")
    return json.loads(p.read_text(encoding="utf-8"))


def skills_for_capability(capability_id: str, data: dict[str, Any] | None = None) -> list[str]:
    data = data or load_capability_bindings()
    for b in data.get("bindings") or []:
        if b.get("capability_id") == capability_id:
            return list(b.get("skill_ids") or [])
    return []


def capabilities_for_skill(skill_id: str, data: dict[str, Any] | None = None) -> list[str]:
    data = data or load_capability_bindings()
    return list((data.get("skill_to_capabilities") or {}).get(skill_id) or [])
