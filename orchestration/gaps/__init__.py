"""Gap Detection integration for planning results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Gap:
    kind: str
    area: str
    severity: str
    blocking: bool
    reason: str
    affected_tasks: list[str] = field(default_factory=list)
    possible_resolution: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_gaps(
    project: dict[str, Any],
    tasks: list[dict[str, Any]],
    roles: list[dict[str, Any]],
    knowledge_ids: list[str],
) -> list[Gap]:
    gaps: list[Gap] = []
    for item in project.get("insufficient_coverage") or []:
        area = item.get("area", "unknown")
        affected = [
            t["id"]
            for t in tasks
            if area.replace("_", "-") in t["id"] or t.get("block_reason")
        ]
        gaps.append(
            Gap(
                kind="MISSING_CAPABILITY",
                area=area,
                severity=item.get("severity", "high"),
                blocking=bool(item.get("blocking")),
                reason=item.get("reason", ""),
                affected_tasks=affected,
                possible_resolution="Add Capability to catalog or escalate to human specialist",
            )
        )
    if not knowledge_ids and project.get("capability_ids"):
        gaps.append(
            Gap(
                kind="MISSING_KNOWLEDGE",
                area="fulfillment",
                severity="medium",
                blocking=False,
                reason="Selected Capabilities lack bound knowledge units",
                possible_resolution="Bind playbooks/frameworks to Capabilities",
            )
        )
    if any(t.get("requires_professional_approval") for t in tasks) and not any(
        r.get("human_required") for r in roles
    ):
        gaps.append(
            Gap(
                kind="MISSING_ROLE",
                area="professional",
                severity="high",
                blocking=True,
                reason="Professional tasks present without human-required role assignment",
                possible_resolution="Assign professional role / escalation",
            )
        )
    for q in project.get("clarifying_questions") or []:
        gaps.append(
            Gap(
                kind="MISSING_INPUT",
                area="clarification",
                severity="medium",
                blocking=False,
                reason=q,
                possible_resolution="Ask human",
            )
        )
    return gaps
