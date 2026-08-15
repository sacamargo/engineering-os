"""Agent ↔ Skill boundary — Agent executes; Skill defines method; evidence required."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from skillpacks.evidence import record_skill_evidence
from skillpacks.invocation import build_bounded_skill_context, record_invocation
from skillpacks.registry import load_registry
from skillpacks.security import check_skill_security


@dataclass
class SkillAgentBinding:
    task_id: str
    capability_ids: list[str]
    skill_ids: list[str]
    role_ids: list[str]
    agent_type: str
    context: dict[str, Any]
    evidence: list[dict[str, Any]] = field(default_factory=list)
    invocations: list[dict[str, Any]] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def bind_skills_to_agent(
    *,
    task: dict[str, Any],
    capability_ids: list[str],
    skill_ids: list[str],
    role_ids: list[str],
    agent_type: str,
    tool_permissions: list[str],
) -> SkillAgentBinding:
    reg = load_registry()
    usable: list[str] = []
    rejected: list[str] = []
    evidence: list[dict[str, Any]] = []
    invocations: list[dict[str, Any]] = []
    for sid in skill_ids:
        pack = reg.get(sid)
        if pack is None:
            rejected.append(sid)
            continue
        sec = check_skill_security(pack.to_dict(), tool_permissions)
        if not sec.allowed:
            rejected.append(sid)
            continue
        if not pack.is_selectable():
            rejected.append(sid)
            evidence.append(
                record_skill_evidence(
                    skill_id=sid,
                    skill_version=pack.version,
                    provenance=pack.provenance.to_dict(),
                    reasoning_summary="Skill unavailable — not applied",
                    uncertainty=["source missing"],
                    findings=["SKILL_UNAVAILABLE"],
                ).to_dict()
            )
            continue
        usable.append(sid)
        inv = record_invocation(
            skillpack_id=sid,
            invocation_mode="bind",
            task_id=str(task.get("id", "")),
            agent_type=agent_type,
        )
        invocations.append(inv.to_dict())
        evidence.append(
            record_skill_evidence(
                skill_id=sid,
                skill_version=pack.version,
                provenance=pack.provenance.to_dict(),
                input_refs=[task.get("id", "")],
                reasoning_summary=f"Skill bound to agent type {agent_type}",
                findings=[f"bound:{sid}"],
                decisions=[f"use_skill:{sid}@{pack.version}"],
                output_refs=[f"invocation:{sid}"],
            ).to_dict()
        )
    bounded = build_bounded_skill_context(usable, task=task)
    return SkillAgentBinding(
        task_id=str(task.get("id", "")),
        capability_ids=capability_ids,
        skill_ids=usable,
        role_ids=role_ids,
        agent_type=agent_type,
        context=bounded,
        evidence=evidence,
        invocations=invocations,
        rejected=rejected,
        notes=[
            "Agent executes work; Skill defines expertise/method; Role defines responsibility",
            "Skill authority without evidence is rejected",
            "Agent receives bounded Skill Context — not entire SkillPack",
        ],
    )
