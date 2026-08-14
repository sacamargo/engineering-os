"""Gate Evaluation — evaluate gate records for evaluability, not decoration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class GateEvaluation:
    gate_id: str
    evaluable: bool
    result: str
    missing_evidence: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_gates(
    gates: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
) -> list[GateEvaluation]:
    art_ids = {a["id"] for a in artifacts}
    task_ids = {t["id"] for t in tasks}
    out: list[GateEvaluation] = []
    for g in gates:
        evidence = g.get("required_evidence") or []
        missing = []
        for item in evidence:
            if isinstance(item, str) and item.startswith("eos.artifact.") and item not in art_ids:
                missing.append(item)
            if isinstance(item, str) and item.startswith("eos.task.") and item not in task_ids:
                missing.append(item)
        evaluable = bool(g.get("condition")) and bool(evidence) and not missing
        notes: list[str] = []
        if g.get("autonomous_pass_forbidden"):
            notes.append("autonomous pass forbidden; human/professional required")
        if not g.get("condition"):
            notes.append("gate lacks condition")
        out.append(
            GateEvaluation(
                gate_id=g["id"],
                evaluable=evaluable,
                result=g.get("result", "pending"),
                missing_evidence=missing,
                notes=notes,
            )
        )
    return out
