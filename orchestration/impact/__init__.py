"""Change Impact analysis for material decision/artifact changes."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ImpactReport:
    changed_id: str
    impacted_artifact_ids: list[str] = field(default_factory=list)
    impacted_task_ids: list[str] = field(default_factory=list)
    impacted_gate_ids: list[str] = field(default_factory=list)
    not_impacted: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def analyze_change_impact(
    changed_artifact_id: str,
    artifacts: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    gates: list[dict[str, Any]],
) -> ImpactReport:
    impacted_arts = {changed_artifact_id}
    changed = True
    while changed:
        changed = False
        for a in artifacts:
            deps = set(a.get("depends_on_artifacts") or [])
            if deps & impacted_arts and a["id"] not in impacted_arts:
                impacted_arts.add(a["id"])
                changed = True
    impacted_tasks = [
        t["id"]
        for t in tasks
        if changed_artifact_id in (t.get("input_artifact_ids") or [])
        or changed_artifact_id in (t.get("output_artifact_ids") or [])
        or set(t.get("input_artifact_ids") or []) & impacted_arts
    ]
    impacted_gates = [
        g["id"]
        for g in gates
        if set(g.get("required_evidence") or []) & impacted_arts
    ]
    unrelated = [
        a["id"]
        for a in artifacts
        if a["id"] not in impacted_arts and a.get("type") in {"ui_copy", "logo", "branding"}
    ]
    return ImpactReport(
        changed_id=changed_artifact_id,
        impacted_artifact_ids=sorted(impacted_arts),
        impacted_task_ids=sorted(set(impacted_tasks)),
        impacted_gate_ids=sorted(impacted_gates),
        not_impacted=unrelated,
        notes=["Impact walks execution artifact dependencies, not knowledge references."],
    )
