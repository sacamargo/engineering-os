"""Evidence recording — distinguish CLAIM from EVIDENCE."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Kind = Literal["claim", "evidence"]


@dataclass
class EvidenceRecord:
    id: str
    kind: Kind
    summary: str
    related_task_id: str | None = None
    related_artifact_id: str | None = None
    source: str = ""
    payload_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def task_completion_allowed(claims: list[EvidenceRecord], evidences: list[EvidenceRecord]) -> bool:
    """A task is not complete on claims alone when evidence is required."""
    if claims and not evidences:
        return False
    return True


def record_claim(id_: str, summary: str, task_id: str | None = None) -> EvidenceRecord:
    return EvidenceRecord(id=id_, kind="claim", summary=summary, related_task_id=task_id)


def record_evidence(
    id_: str, summary: str, source: str, task_id: str | None = None, artifact_id: str | None = None
) -> EvidenceRecord:
    return EvidenceRecord(
        id=id_,
        kind="evidence",
        summary=summary,
        source=source,
        related_task_id=task_id,
        related_artifact_id=artifact_id,
    )
