"""Load live Capability and Knowledge Unit metadata from the repository catalog.

Discovery is filesystem-based. Adding a Capability markdown file extends resolution
without editing orchestrator switches.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT_DEFAULT = Path(__file__).resolve().parents[2]

ID_RE = re.compile(r"^eos\.[a-z]+\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")


@dataclass
class CatalogUnit:
    id: str
    type: str
    title: str
    summary: str = ""
    purpose: str = ""
    applicability: str = ""
    limits: str = ""
    status: str = "active"
    domain: str = ""
    tags: list[str] = field(default_factory=list)
    entry_signals: list[str] = field(default_factory=list)
    relationships: list[dict[str, str]] = field(default_factory=list)
    path: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


def _parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1]
    if raw in {"true", "false"}:
        return raw == "true"
    return raw


def _parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    header = text[3:end]
    meta: dict[str, Any] = {}
    current_list_key: str | None = None
    current_rel: dict[str, str] | None = None
    relationships: list[dict[str, str]] = []

    for line in header.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - type:"):
            if current_rel:
                relationships.append(current_rel)
            current_rel = {"type": line.split(":", 1)[1].strip()}
            current_list_key = "relationships"
            continue
        if current_rel is not None and line.startswith("    target:"):
            current_rel["target"] = line.split(":", 1)[1].strip()
            continue
        if re.match(r"^[a-z_]+:\s*$", line):
            key = line.split(":", 1)[0]
            meta[key] = []
            current_list_key = key
            if current_rel:
                relationships.append(current_rel)
                current_rel = None
            continue
        if current_list_key and line.startswith("  - ") and current_list_key != "relationships":
            meta.setdefault(current_list_key, []).append(line[4:].strip())
            continue
        if ":" in line and not line.startswith(" "):
            if current_rel:
                relationships.append(current_rel)
                current_rel = None
            key, value = line.split(":", 1)
            meta[key.strip()] = _parse_scalar(value)
            current_list_key = None
            continue
    if current_rel:
        relationships.append(current_rel)
    if relationships:
        meta["relationships"] = relationships
    return meta


def load_catalog(repo_root: Path | None = None) -> dict[str, CatalogUnit]:
    root = repo_root or ROOT_DEFAULT
    units: dict[str, CatalogUnit] = {}
    for dirname in ("capabilities", "playbooks", "frameworks", "skills", "standards", "checklists", "workflows", "templates"):
        base = root / dirname
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            meta = _parse_frontmatter(text)
            unit_id = meta.get("id")
            if not isinstance(unit_id, str):
                continue
            unit = CatalogUnit(
                id=unit_id,
                type=str(meta.get("type", "")),
                title=str(meta.get("title", "")),
                summary=str(meta.get("summary", "")),
                purpose=str(meta.get("purpose", "")),
                applicability=str(meta.get("applicability", "")),
                limits=str(meta.get("limits", "")),
                status=str(meta.get("status", "active")),
                domain=str(meta.get("domain", "")),
                tags=list(meta.get("tags") or []),
                entry_signals=list(meta.get("entry_signals") or []),
                relationships=list(meta.get("relationships") or []),
                path=str(path.relative_to(root)),
                meta=meta,
            )
            units[unit_id] = unit
    return units


def load_capabilities(repo_root: Path | None = None) -> dict[str, CatalogUnit]:
    units = load_catalog(repo_root)
    return {
        uid: unit
        for uid, unit in units.items()
        if unit.type == "capability" and unit.status == "active"
    }
