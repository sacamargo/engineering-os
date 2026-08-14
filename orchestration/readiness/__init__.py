"""Readiness Engine — can this plan start?"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Status = Literal[
    "ready",
    "blocked",
    "needs_input",
    "needs_human",
    "missing_capability",
    "invalid",
    "partially_ready",
]


@dataclass
class ReadinessResult:
    status: Status
    reasons: list[str] = field(default_factory=list)
    automatable_task_ids: list[str] = field(default_factory=list)
    human_task_ids: list[str] = field(default_factory=list)
    blocked_task_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_readiness(
    project: dict[str, Any],
    tasks: list[dict[str, Any]],
    dependency_ok: bool,
    escalations: list[dict[str, Any]],
) -> ReadinessResult:
    if not dependency_ok:
        return ReadinessResult(status="invalid", reasons=["dependency graph invalid"])

    gaps = project.get("insufficient_coverage") or []
    blocking_gaps = [g for g in gaps if g.get("blocking")]
    questions = project.get("clarifying_questions") or []
    open_escalations = [
        e for e in escalations if e.get("status") == "required" and e.get("blocking", True)
    ]

    automatable = [
        t["id"]
        for t in tasks
        if t.get("status") in {"ready", "pending"}
        and not t.get("requires_professional_approval")
    ]
    human_tasks = [
        t["id"]
        for t in tasks
        if t.get("requires_professional_approval")
        or t.get("block_reason") == "professional_validation_required"
    ]
    blocked = [t["id"] for t in tasks if t.get("status") == "blocked"]

    if open_escalations or human_tasks:
        reasons = ["professional/human approval required for some scopes"]
        if automatable:
            return ReadinessResult(
                status="partially_ready",
                reasons=reasons
                + ["software planning tasks may proceed; physical scopes blocked"],
                automatable_task_ids=automatable,
                human_task_ids=human_tasks,
                blocked_task_ids=blocked,
            )
        return ReadinessResult(
            status="needs_human",
            reasons=reasons,
            human_task_ids=human_tasks,
            blocked_task_ids=blocked,
        )

    if blocking_gaps:
        return ReadinessResult(
            status="missing_capability",
            reasons=[g.get("reason", g.get("area", "gap")) for g in blocking_gaps],
            blocked_task_ids=blocked,
        )

    if questions and any(
        u.get("certainty") == "required" for u in project.get("uncertainties") or []
    ):
        return ReadinessResult(
            status="needs_input", reasons=list(questions), automatable_task_ids=automatable
        )

    if blocked and automatable:
        return ReadinessResult(
            status="partially_ready",
            reasons=["some tasks blocked on coverage gaps; others can be planned"],
            automatable_task_ids=automatable,
            blocked_task_ids=blocked,
        )

    if blocked and not automatable:
        return ReadinessResult(
            status="blocked",
            reasons=["all actionable tasks blocked"],
            blocked_task_ids=blocked,
        )

    return ReadinessResult(
        status="ready",
        reasons=["plan dependencies valid; no blocking human gate"],
        automatable_task_ids=automatable,
    )
