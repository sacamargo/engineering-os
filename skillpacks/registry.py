"""Skill registry discovery — load manifests from disk; no hardcoded Skill lists."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from skillpacks.model import SkillPack, skillpack_from_dict

DEFAULT_ROOT = Path(__file__).resolve().parent


@dataclass
class RegistryEntry:
    id: str
    status: str
    version: str
    path: str
    category: str = ""
    availability: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status,
            "version": self.version,
            "path": self.path,
            "category": self.category,
            "availability": self.availability,
        }


@dataclass
class SkillRegistry:
    root: Path
    entries: list[RegistryEntry] = field(default_factory=list)
    packs: dict[str, SkillPack] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def get(self, skill_id: str) -> SkillPack | None:
        return self.packs.get(skill_id)

    def list_ids(self) -> list[str]:
        return sorted(self.packs.keys())

    def by_status(self, status: str) -> list[SkillPack]:
        return [p for p in self.packs.values() if p.status == status]

    def by_category(self, category: str) -> list[SkillPack]:
        return [p for p in self.packs.values() if p.category == category]

    def selectable(self) -> list[SkillPack]:
        return [p for p in self.packs.values() if p.is_selectable()]

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "entries": [e.to_dict() for e in self.entries],
            "pack_ids": self.list_ids(),
            "errors": list(self.errors),
        }


def load_registry(root: Path | None = None) -> SkillRegistry:
    """Discover skillpacks from registry.json + packs/*/manifest.json."""
    root = root or DEFAULT_ROOT
    registry_path = root / "registry.json"
    reg = SkillRegistry(root=root)
    if not registry_path.is_file():
        reg.errors.append(f"missing registry: {registry_path}")
        return reg
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    index = {str(e.get("id")): e for e in (data.get("skills") or [])}

    packs_dir = root / "packs"
    manifests: list[Path] = []
    if packs_dir.is_dir():
        manifests = sorted(packs_dir.glob("*/manifest.json"))

    seen: set[str] = set()
    for manifest_path in manifests:
        try:
            raw = json.loads(manifest_path.read_text(encoding="utf-8"))
            pack = skillpack_from_dict(raw)
        except Exception as exc:  # noqa: BLE001
            reg.errors.append(f"{manifest_path}: {exc}")
            continue
        if pack.id in seen:
            reg.errors.append(f"duplicate skill id: {pack.id}")
            continue
        seen.add(pack.id)
        shape_errs = pack.validate_shape()
        if shape_errs:
            reg.errors.extend(f"{pack.id}: {e}" for e in shape_errs)
            # still register for discovery of unavailable packs
        availability = "selectable" if pack.is_selectable() else pack.status
        entry = RegistryEntry(
            id=pack.id,
            status=pack.status,
            version=pack.version,
            path=str(manifest_path.relative_to(root)),
            category=pack.category,
            availability=availability,
        )
        reg.entries.append(entry)
        reg.packs[pack.id] = pack
        # Prefer registry index metadata when present
        if pack.id in index:
            idx = index[pack.id]
            if idx.get("status"):
                entry.status = str(idx["status"])

    # Registry entries without manifests
    for sid, idx in index.items():
        if sid not in reg.packs:
            reg.errors.append(f"registry lists {sid} but manifest missing")
            reg.entries.append(
                RegistryEntry(
                    id=sid,
                    status=str(idx.get("status", "unavailable")),
                    version=str(idx.get("version", "")),
                    path=str(idx.get("path", "")),
                    category=str(idx.get("category", "")),
                    availability="missing_manifest",
                )
            )
    return reg


def discover_skills(root: Path | None = None) -> list[dict[str, Any]]:
    """Public discovery API used by Orchestration — returns serializable entries."""
    reg = load_registry(root)
    return [e.to_dict() for e in reg.entries]
