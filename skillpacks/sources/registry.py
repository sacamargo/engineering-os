"""Data-driven Skill Source registry."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from skillpacks.sources.model import SkillSource, source_from_dict

DEFAULT_ROOT = Path(__file__).resolve().parent


@dataclass
class SourceRegistry:
    root: Path
    sources: dict[str, SkillSource] = field(default_factory=dict)
    by_skill: dict[str, list[str]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def get(self, source_id: str) -> SkillSource | None:
        return self.sources.get(source_id)

    def sources_for_skill(self, skillpack_id: str) -> list[SkillSource]:
        return [self.sources[sid] for sid in self.by_skill.get(skillpack_id, []) if sid in self.sources]

    def skills_for_source(self, source_id: str) -> list[str]:
        src = self.sources.get(source_id)
        return [src.skillpack_id] if src else []

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "source_ids": sorted(self.sources),
            "by_skill": {k: list(v) for k, v in self.by_skill.items()},
            "errors": list(self.errors),
        }


def load_source_registry(root: Path | None = None) -> SourceRegistry:
    root = root or DEFAULT_ROOT
    reg = SourceRegistry(root=root)
    index_path = root / "registry.json"
    if not index_path.is_file():
        reg.errors.append(f"missing {index_path}")
        return reg
    index = json.loads(index_path.read_text(encoding="utf-8"))
    for entry in index.get("sources") or []:
        rel = entry.get("path")
        if not rel:
            reg.errors.append(f"registry entry missing path: {entry}")
            continue
        path = root / str(rel)
        if not path.is_file():
            reg.errors.append(f"missing sources file: {path}")
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for raw in payload.get("sources") or []:
            try:
                src = source_from_dict(raw)
            except Exception as exc:  # noqa: BLE001
                reg.errors.append(f"{path}: {exc}")
                continue
            errs = src.validate_shape()
            if errs:
                reg.errors.extend(f"{src.source_id}: {e}" for e in errs)
            if src.source_id in reg.sources:
                reg.errors.append(f"duplicate source_id: {src.source_id}")
                continue
            reg.sources[src.source_id] = src
            reg.by_skill.setdefault(src.skillpack_id, []).append(src.source_id)
    return reg
