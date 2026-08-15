"""Codebase Intelligence boundary — Orchestrator consumes evidence; does not own indexing."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


@dataclass
class RepositorySnapshot:
    root: str
    files: list[str] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    conventions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    snapshot_id: str | None = None
    findings_count: int = 0
    unknowns: list[str] = field(default_factory=list)
    analysis_status: str = "not_run"  # not_run | deferred | complete | failed
    epistemic: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def has_usable_evidence(self) -> bool:
        return self.analysis_status == "complete" and bool(self.snapshot_id)


class CodebaseIntelligence(Protocol):
    def inspect(self, root: str) -> RepositorySnapshot: ...

    def analyze(self, root: str) -> dict[str, Any]: ...


class NullCodebaseIntelligence:
    """Stub: returns empty snapshot and explicit limitation."""

    def inspect(self, root: str) -> RepositorySnapshot:
        return RepositorySnapshot(
            root=root,
            analysis_status="not_run",
            notes=["Codebase Intelligence runtime not implemented; boundary only."],
        )

    def analyze(self, root: str) -> dict[str, Any]:
        return {
            "schema": "eos.codebase.analysis.v1",
            "notes": ["NullCodebaseIntelligence cannot analyze."],
            "snapshot": self.inspect(root).to_dict(),
        }


class LocalCodebaseIntelligence:
    """Phase 5 adapter — delegates to codebase package (not a Capability)."""

    def inspect(self, root: str) -> RepositorySnapshot:
        """Lightweight presence check; does not index the whole tree."""
        return RepositorySnapshot(
            root=root,
            analysis_status="deferred",
            notes=[
                "Full analysis deferred until codebase_analysis task or analyze() is invoked.",
                "Codebase Intelligence is evidence infrastructure, not a Capability.",
            ],
            unknowns=["Repository structure unknown until analysis runs."],
        )

    def analyze(self, root: str) -> dict[str, Any]:
        from codebase.analyze import analyze_repository
        from codebase.report import bundle_to_machine_json

        bundle = analyze_repository(root)
        payload = bundle_to_machine_json(bundle)
        snap = bundle.snapshot
        payload["summary"] = RepositorySnapshot(
            root=root,
            files=[f.get("path", "") for f in snap.files[:200]],
            modules=[m.get("path", "") for m in snap.modules[:200]],
            dependencies=[
                f"{d.get('source_path')}->{d.get('target')}" for d in snap.dependencies[:200]
            ],
            notes=list(snap.unknowns)[:20],
            snapshot_id=snap.id,
            findings_count=len(snap.findings),
            unknowns=list(snap.unknowns),
            analysis_status="complete",
            epistemic={"levels": ["observed", "inferred", "unknown"]},
        ).to_dict()
        return payload

    def summarize_analysis(self, payload: dict[str, Any]) -> RepositorySnapshot:
        summary = payload.get("summary") or {}
        if summary:
            return RepositorySnapshot(**{k: summary[k] for k in RepositorySnapshot.__dataclass_fields__ if k in summary})
        snap = payload.get("snapshot") or {}
        meta = snap.get("meta") or {}
        return RepositorySnapshot(
            root=meta.get("root") or "",
            snapshot_id=snap.get("id"),
            findings_count=len(snap.get("findings") or []),
            unknowns=list(snap.get("unknowns") or []),
            analysis_status="complete" if snap.get("id") else "failed",
            files=[f.get("path", "") for f in (snap.get("files") or [])[:200]],
            modules=[m.get("path", "") for m in (snap.get("modules") or [])[:200]],
            notes=["Summarized from analysis payload."],
        )


CODEBASE_REQUIRED_INTENTS = frozenset(
    {
        "analyze",
        "refactor",
        "migrate",
        "audit",
        "investigate_incident",
        "optimize",
    }
)


def intent_requires_codebase(possible_intents: list[str], context: dict[str, Any] | None = None) -> bool:
    context = context or {}
    if context.get("codebase_snapshot_id") or context.get("codebase_analyzed"):
        return False
    return any(i in CODEBASE_REQUIRED_INTENTS for i in possible_intents)
