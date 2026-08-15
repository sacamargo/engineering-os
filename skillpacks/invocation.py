"""Skill invocation evidence + bounded skill context for Agents."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any

from skillpacks.context_engineering import assemble_context
from skillpacks.evidence import record_skill_evidence
from skillpacks.registry import load_registry
from skillpacks.security import check_skill_security
from skillpacks.sources.registry import load_source_registry


@dataclass
class SkillInvocationEvidence:
    skillpack_id: str
    skill_version: str
    source_versions: list[dict[str, str]]
    invocation_mode: str
    relevant_knowledge: list[str]
    constraints_applied: list[str]
    agent_type: str
    task_id: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_bounded_skill_context(
    skill_ids: list[str],
    *,
    task: dict[str, Any],
    max_chars: int = 12_000,
) -> dict[str, Any]:
    """Agent does NOT receive the entire Skill — only bounded slices."""
    reg = load_registry()
    sources = load_source_registry()
    slices: list[dict[str, Any]] = []
    for sid in skill_ids:
        pack = reg.get(sid)
        if pack is None or not pack.is_selectable():
            continue
        srcs = sources.sources_for_skill(sid)
        slices.append(
            {
                "skill_id": sid,
                "version": pack.version,
                "purpose": pack.purpose[:500],
                "constraints": pack.constraints[:20],
                "limitations": pack.limitations[:20],
                "negative_notes": [t.notes for t in pack.triggers if t.polarity == "negative"][:10],
                "workflows": [{"id": w.id, "mode": w.mode, "name": w.name} for w in pack.workflows[:5]],
                "provenance": pack.provenance.to_dict(),
                "source_refs": [
                    {"source_id": s.source_id, "version": s.version, "hash": s.content_hash, "status": s.status}
                    for s in srcs
                ],
            }
        )
    ctx = assemble_context(
        task=task,
        skill_ids=skill_ids,
        max_chars=max_chars,
        skill_version="bounded",
    )
    return {
        "skill_slices": slices,
        "assembled": ctx.to_dict(),
        "budget_chars": max_chars,
        "full_skill_dumped": False,
        "notes": ["Bounded Skill Context only — not entire SkillPack bodies"],
    }


def record_invocation(
    *,
    skillpack_id: str,
    invocation_mode: str,
    task_id: str,
    agent_type: str,
) -> SkillInvocationEvidence:
    reg = load_registry()
    sources = load_source_registry()
    pack = reg.get(skillpack_id)
    version = pack.version if pack else "unknown"
    src_versions = [
        {"source_id": s.source_id, "version": s.version, "hash": s.content_hash or ""}
        for s in sources.sources_for_skill(skillpack_id)
    ]
    constraints = list(pack.constraints) if pack else []
    return SkillInvocationEvidence(
        skillpack_id=skillpack_id,
        skill_version=version,
        source_versions=src_versions,
        invocation_mode=invocation_mode,
        relevant_knowledge=[f"constraints:{len(constraints)}"],
        constraints_applied=constraints,
        agent_type=agent_type,
        task_id=task_id,
    )
