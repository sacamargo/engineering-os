"""Controlled Skill composition — not a hidden task DAG.

Skill composition ≠ Task dependency ≠ Capability relationship ≠ Artifact dependency.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from skillpacks.model import SkillPack
from skillpacks.registry import SkillRegistry


@dataclass
class ComposedSkillSet:
    primary: list[str] = field(default_factory=list)
    supporting: list[str] = field(default_factory=list)
    transversal: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def all_ids(self) -> list[str]:
        return list(dict.fromkeys([*self.primary, *self.supporting, *self.transversal]))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compose_skills(
    selected_ids: list[str],
    registry: SkillRegistry,
    *,
    allow_unavailable: bool = False,
) -> ComposedSkillSet:
    """Compose selected Skills into primary/supporting/transversal buckets.

    Does not create task dependency edges.
    """
    result = ComposedSkillSet(
        notes=[
            "Composition assigns contribution roles to the same task/artifact facet.",
            "Composition does not imply Agent pipeline order or task DAG edges.",
        ]
    )
    packs: list[SkillPack] = []
    for sid in selected_ids:
        pack = registry.get(sid)
        if pack is None:
            result.errors.append(f"unknown skill: {sid}")
            continue
        if not pack.is_selectable() and not allow_unavailable:
            result.errors.append(f"skill not selectable: {sid}")
            continue
        packs.append(pack)

    # Detect prohibited circular primary composition (would smuggle execution order)
    primary_edges: dict[str, set[str]] = {}
    for pack in packs:
        for rule in pack.composition_rules:
            if rule.implies_task_dependency:
                result.errors.append(f"{pack.id}: composition must not imply task dependency")
            if rule.kind == "primary":
                primary_edges.setdefault(pack.id, set()).update(rule.with_skill_ids)
    for a, targets in primary_edges.items():
        for b in targets:
            if a in primary_edges.get(b, set()) and a != b:
                result.errors.append(f"circular primary composition prohibited: {a} <-> {b}")

    for pack in packs:
        kinds = {r.kind for r in pack.composition_rules} or {"supporting"}
        if pack.category in {"quality", "context"} or "transversal" in kinds:
            result.transversal.append(pack.id)
        elif "primary" in kinds:
            result.primary.append(pack.id)
        else:
            result.supporting.append(pack.id)

    # Example validated composition: design primary + quality transversal
    if any(p.category == "design" for p in packs) and any(p.category == "quality" for p in packs):
        result.notes.append(
            "UI/design Skill + quality review Skill may compose without becoming a pipeline"
        )
    return result
