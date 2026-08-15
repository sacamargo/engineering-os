"""Stop Slop integration — fail closed without source; structural bounds only."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from skillpacks.registry import load_registry

STOP_SLOP_ID = "eos.skillpack.quality.stop-slop"


@dataclass
class StopSlopReview:
    skill_id: str
    skill_version: str
    status: str  # performed | rejected | unavailable | blocked
    findings: list[str] = field(default_factory=list)
    claims_correctness: bool = False
    replaces_domain_review: bool = False
    evidence: list[dict[str, Any]] = field(default_factory=list)
    uncertainty: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def review_artifact(artifact: dict[str, Any] | None) -> StopSlopReview:
    """Review an artifact with Stop Slop bounds.

    Without source: returns unavailable (does not invent methodology).
    With empty artifact: can reject structurally without claiming domain truth.
    """
    reg = load_registry()
    pack = reg.get(STOP_SLOP_ID)
    version = pack.version if pack else "unknown"
    if pack is None or not pack.is_selectable():
        return StopSlopReview(
            skill_id=STOP_SLOP_ID,
            skill_version=version,
            status="unavailable",
            findings=[],
            claims_correctness=False,
            replaces_domain_review=False,
            uncertainty=["Stop Slop source missing; methodology not fabricated"],
            evidence=[
                {
                    "kind": "skill_unavailable",
                    "skill_id": STOP_SLOP_ID,
                    "action": "NEEDS_SOURCE",
                }
            ],
        )
    if not artifact or not (artifact.get("content") or artifact.get("body") or artifact.get("text")):
        return StopSlopReview(
            skill_id=STOP_SLOP_ID,
            skill_version=version,
            status="rejected",
            findings=["empty_or_missing_artifact"],
            claims_correctness=False,
            replaces_domain_review=False,
            evidence=[{"kind": "structural_reject", "reason": "no inspectable content"}],
            uncertainty=["Structural emptiness only; not a domain correctness verdict"],
        )
    return StopSlopReview(
        skill_id=STOP_SLOP_ID,
        skill_version=version,
        status="performed",
        findings=["review_slot_only"],
        claims_correctness=False,
        replaces_domain_review=False,
        evidence=[{"kind": "review_performed", "note": "does not assert product correctness"}],
        uncertainty=["Domain specialist review still required where applicable"],
    )
