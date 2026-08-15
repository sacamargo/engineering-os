"""Skill conflict arbitration — composition ≠ priority; record decisions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SkillConflict:
    skill_ids: list[str]
    topic: str
    positions: dict[str, str]
    authority: str
    resolution: str
    escalated: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def arbitrate_conflicts(positions: list[dict[str, str]]) -> list[SkillConflict]:
    """positions: [{skill_id, topic, stance, kind}] kind in method|constraint|review."""
    by_topic: dict[str, list[dict[str, str]]] = {}
    for p in positions:
        by_topic.setdefault(p["topic"], []).append(p)
    out: list[SkillConflict] = []
    for topic, items in by_topic.items():
        if len(items) < 2:
            continue
        kinds = {i.get("kind", "method") for i in items}
        # Constraints outrank methods; review does not auto-win product decisions
        if "constraint" in kinds and "method" in kinds:
            authority = "constraint"
            resolution = "apply_constraints_over_methods"
            escalated = False
        elif "review" in kinds and "method" in kinds:
            authority = "human_or_domain"
            resolution = "record_review_findings_do_not_auto_override"
            escalated = True
        else:
            authority = "human"
            resolution = "escalate_arbitrary_skill_order_forbidden"
            escalated = True
        out.append(
            SkillConflict(
                skill_ids=[i["skill_id"] for i in items],
                topic=topic,
                positions={i["skill_id"]: i.get("stance", "") for i in items},
                authority=authority,
                resolution=resolution,
                escalated=escalated,
                notes=["Skill composition ≠ Skill priority"],
            )
        )
    return out
