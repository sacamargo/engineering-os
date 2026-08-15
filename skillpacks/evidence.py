"""Skill evidence — claim ≠ evidence; no hidden chain-of-thought."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SkillEvidence:
    skill_id: str
    skill_version: str
    provenance: dict[str, Any]
    input_refs: list[str] = field(default_factory=list)
    output_refs: list[str] = field(default_factory=list)
    reasoning_summary: str = ""
    findings: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    uncertainty: list[str] = field(default_factory=list)
    reviewer: str | None = None
    timestamp: float = field(default_factory=time.time)
    is_claim_only: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def record_skill_evidence(**kwargs: Any) -> SkillEvidence:
    ev = SkillEvidence(**kwargs)
    if ev.is_claim_only and not ev.findings and not ev.output_refs:
        raise ValueError("claim-only skill statements are not evidence")
    # "Skill says correct" without findings/outputs is invalid evidence
    if "skill says this is correct" in ev.reasoning_summary.lower() and not ev.findings:
        raise ValueError("Skill authority is not evidence")
    return ev
