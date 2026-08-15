"""Map Codebase Intelligence outputs onto the Evidence Model.

Produces evidence records (not Knowledge Units). Finding ≠ decision.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from codebase.findings import CodebaseFinding
from codebase.snapshot import CodebaseSnapshot, utc_now_iso

EvidenceKind = Literal[
    "artifact",
    "test",
    "approval",
    "commit",
    "log",
    "external",
    "file",
    "symbol",
    "dependency",
    "configuration",
    "other",
]


@dataclass
class CodebaseEvidence:
    """Evidence aligned with foundation/EVIDENCE-MODEL.md fields."""

    id: str
    claim: str
    kind: EvidenceKind
    pointer: str
    certainty: str
    produced_by: str = "codebase_intelligence"
    project_id: str | None = None
    related_gate_ids: list[str] = field(default_factory=list)
    related_finding_ids: list[str] = field(default_factory=list)
    timestamp: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evidence_from_finding(
    finding: CodebaseFinding,
    *,
    snapshot_id: str,
    git_revision: str | None = None,
    project_id: str | None = None,
) -> CodebaseEvidence:
    pointers = list(finding.evidence)
    if finding.location:
        pointers.insert(0, finding.location)
    if git_revision:
        pointers.append(f"commit:{git_revision}")
    return CodebaseEvidence(
        id=f"eos.evidence.codebase.{finding.id.split('.')[-1]}",
        claim=finding.explanation,
        kind="other",
        pointer=";".join(pointers),
        certainty=finding.confidence,
        project_id=project_id,
        related_finding_ids=[finding.id],
        timestamp=utc_now_iso(),
        details={
            "snapshot_id": snapshot_id,
            "finding_kind": finding.kind,
            "severity": finding.severity,
            "location": finding.location,
        },
    )


def evidence_from_snapshot_meta(snapshot: CodebaseSnapshot) -> list[CodebaseEvidence]:
    """Baseline evidence: analysis provenance."""
    meta = snapshot.meta
    records = [
        CodebaseEvidence(
            id=f"eos.evidence.snapshot.{snapshot.id.split('.')[-1]}",
            claim=f"Codebase snapshot {snapshot.id} produced for root {meta.root}",
            kind="log",
            pointer=meta.root,
            certainty="observed",
            timestamp=meta.analyzed_at,
            details={
                "git_revision": meta.git_revision,
                "git_branch": meta.git_branch,
                "included_file_count": meta.included_file_count,
                "parsers_used": meta.parsers_used,
                "content_fingerprint": meta.content_fingerprint,
            },
        )
    ]
    if meta.git_revision:
        records.append(
            CodebaseEvidence(
                id=f"eos.evidence.commit.{meta.git_revision[:12]}",
                claim=f"Analysis bound to git revision {meta.git_revision}",
                kind="commit",
                pointer=meta.git_revision,
                certainty="observed",
                timestamp=meta.analyzed_at,
            )
        )
    return records


def collect_evidence(
    snapshot: CodebaseSnapshot,
    findings: list[CodebaseFinding],
    *,
    project_id: str | None = None,
) -> list[CodebaseEvidence]:
    records = evidence_from_snapshot_meta(snapshot)
    for f in findings:
        records.append(
            evidence_from_finding(
                f,
                snapshot_id=snapshot.id,
                git_revision=snapshot.meta.git_revision,
                project_id=project_id,
            )
        )
    # Reject orphan claims: every finding evidence must have a pointer
    for r in records:
        if not r.pointer:
            raise ValueError(f"evidence without pointer: {r.id}")
    return records
