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
        return results
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
    # Stop Slop: review performed ≠ product correct
    if pack.id.endswith("stop-slop"):
        results.append(
            GateResult(
                "skill_review_performed",
                "passed" if evidence_attached else "not_run",
                "review evidence present; does NOT mean product is correct",
            )
        )
    return results
