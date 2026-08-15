"""Orchestration boundary for Skill resolution — thin wrapper over skillpacks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from skillpacks.routing import SkillResolution, resolve_skills


def resolve_skill_candidates(
    intent: dict[str, Any],
    capability_ids: list[str],
    *,
    registry_root: Path | None = None,
) -> SkillResolution:
    return resolve_skills(intent, capability_ids, registry_root=registry_root)
