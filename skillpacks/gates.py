"""Generic Skill quality gates."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from skillpacks.model import SkillPack


@dataclass
class GateResult:
    gate_id: str
    status: str  # passed | failed | blocked | not_run
    reason: str
    evidence_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_skill_gates(
    pack: SkillPack,
    *,
    inputs_present: bool,
    outputs_present: bool,
    evidence_attached: bool,
    tools_available: bool = True,
    knowledge_available: bool = True,
    source_valid: bool | None = None,
    provenance_valid: bool | None = None,
    context_bounded: bool = True,
    conflict_resolved: bool = True,
    version_pinned: bool = True,
    negative_triggers_checked: bool = True,
) -> list[GateResult]:
    results: list[GateResult] = []
    results.append(
        GateResult(
            "provenance_known",
            "passed" if pack.provenance.origin else "failed",
            "provenance.origin present" if pack.provenance.origin else "missing provenance",
        )
    )
    if pack.status == "unavailable" or pack.provenance.unavailable_source_content:
        results.append(
            GateResult("skill_applicable", "blocked", "skill source unavailable", [])
        )
        results.append(GateResult("SKILL_SOURCE_VALID", "failed", "source unavailable"))
        return results
    if source_valid is not None:
        results.append(
            GateResult(
                "SKILL_SOURCE_VALID",
                "passed" if source_valid else "failed",
                "source valid" if source_valid else "source invalid",
            )
        )
    if provenance_valid is not None:
        results.append(
            GateResult(
                "SKILL_PROVENANCE_VALID",
                "passed" if provenance_valid else "failed",
                "provenance valid" if provenance_valid else "provenance invalid",
            )
        )
    results.append(
        GateResult(
            "SKILL_CONTEXT_BOUNDED",
            "passed" if context_bounded else "failed",
            "context bounded" if context_bounded else "context dump detected",
        )
    )
    results.append(
        GateResult(
            "SKILL_CONFLICT_RESOLVED",
            "passed" if conflict_resolved else "failed",
            "conflicts resolved" if conflict_resolved else "SKILL_CONFLICT unresolved",
        )
    )
    results.append(
        GateResult(
            "SKILL_VERSION_PINNED",
            "passed" if version_pinned and bool(pack.version) else "failed",
            "version pinned" if version_pinned else "version missing",
        )
    )
    results.append(
        GateResult(
            "SKILL_NEGATIVE_TRIGGERS_CHECKED",
            "passed" if negative_triggers_checked else "not_run",
            "negative triggers checked" if negative_triggers_checked else "NOT_RUN — cannot declare success",
        )
    )
    results.append(
        GateResult(
            "required_inputs_present",
            "passed" if inputs_present else "failed",
            "inputs ok" if inputs_present else "missing inputs",
        )
    )
    results.append(
        GateResult(
            "required_tools_available",
            "passed" if tools_available else "failed",
            "tools ok" if tools_available else "missing tools",
        )
    )
    results.append(
        GateResult(
            "required_knowledge_available",
            "passed" if knowledge_available else "failed",
            "knowledge ok" if knowledge_available else "missing knowledge",
        )
    )
    results.append(
        GateResult(
            "output_artifact_produced",
            "passed" if outputs_present else "failed",
            "outputs ok" if outputs_present else "missing outputs",
        )
    )
    results.append(
        GateResult(
            "evidence_attached",
            "passed" if evidence_attached else "failed",
            "evidence ok" if evidence_attached else "missing evidence",
        )
    )
    if pack.id.endswith("stop-slop"):
        results.append(
            GateResult(
                "skill_review_performed",
                "passed" if evidence_attached else "not_run",
                "review evidence present; does NOT mean product is correct",
            )
        )
    # Agent cannot declare success if required gate NOT_RUN
    if any(r.status == "not_run" and r.gate_id.startswith("SKILL_") for r in results):
        results.append(
            GateResult("agent_success_allowed", "failed", "required skill gate NOT_RUN")
        )
    return results
