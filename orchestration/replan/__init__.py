"""Replanning — partial plan revision without silent history rewrite."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ReplanResult:
    plan: dict[str, Any]
    invalidated_artifact_ids: list[str] = field(default_factory=list)
    affected_task_ids: list[str] = field(default_factory=list)
    requires_approval: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def replan_after_task_failure(
    plan: dict[str, Any],
    tasks: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    failed_task_id: str,
) -> ReplanResult:
    new_plan = deepcopy(plan)
    new_plan["revision"] = int(plan.get("revision", 1)) + 1
    failed = next((t for t in tasks if t["id"] == failed_task_id), None)
    invalidated = list(failed.get("output_artifact_ids") or []) if failed else []
    affected = [failed_task_id] if failed else []
    for t in tasks:
        if any(dep == failed_task_id for dep in t.get("depends_on_task_ids") or []):
            affected.append(t["id"])
            invalidated.extend(t.get("output_artifact_ids") or [])
        if any(a in invalidated for a in t.get("input_artifact_ids") or []):
            affected.append(t["id"])
    notes = [
        "Partial replan: increment revision; supersede invalidated artifacts explicitly in later runtime.",
        "Do not silently rewrite accepted decisions.",
    ]
    return ReplanResult(
        plan=new_plan,
        invalidated_artifact_ids=sorted(set(invalidated)),
        affected_task_ids=sorted(set(affected)),
        requires_approval=True,
        notes=notes,
    )
