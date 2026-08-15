"""Repository analysis pipeline — observation only; no autonomous mutation."""

from __future__ import annotations

import resource
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codebase.architecture import detect_architecture_signals
from codebase.config_intel import analyze_configuration
from codebase.dependencies import build_dependency_graph
from codebase.evidence import collect_evidence
from codebase.findings import build_findings
from codebase.fs_index import index_filesystem
from codebase.git_intel import inspect_git
from codebase.performance import detect_performance_signals
from codebase.security import detect_security_signals
from codebase.snapshot import (
    AnalysisError,
    CodebaseSnapshot,
    SnapshotMeta,
    new_snapshot_id,
    utc_now_iso,
)
from codebase.symbols import build_symbol_index
from codebase.tests_intel import analyze_tests


@dataclass
class AnalysisBundle:
    snapshot: CodebaseSnapshot
    git: dict[str, Any] = field(default_factory=dict)
    security_signals: list[dict[str, Any]] = field(default_factory=list)
    performance_signals: list[dict[str, Any]] = field(default_factory=list)
    impact_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot": self.snapshot.to_dict(),
            "git": self.git,
            "security_signals": self.security_signals,
            "performance_signals": self.performance_signals,
            "impact_notes": self.impact_notes,
        }


def _rss_mb() -> float | None:
    try:
        # ru_maxrss is bytes on macOS, kilobytes on Linux — report as raw/1024 for rough MB on macOS
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # Heuristic: if value is large, treat as bytes (darwin)
        if usage > 10_000_000:
            return round(usage / (1024 * 1024), 2)
        return round(usage / 1024, 2)
    except Exception:
        return None


def analyze_repository(root: str | Path) -> AnalysisBundle:
    """
    repository → snapshot → index → symbols → dependencies → tests →
    configuration → architecture signals → findings → evidence
    """
    t0 = time.perf_counter()
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {root_path}")

    errors: list[AnalysisError] = []
    unknowns: list[str] = [
        "Runtime behavior is unknown without execution evidence.",
        "Coverage is unknown unless a measured report is supplied.",
        "Architecture signals are not authoritative architecture.",
    ]

    git = inspect_git(root_path)
    fs = index_filesystem(root_path)
    symbols = build_symbol_index(root_path, fs)

    for err in symbols.errors:
        errors.append(AnalysisError(stage="parser", message=err))

    deps = build_dependency_graph(root_path, symbols)
    tests = analyze_tests(root_path, fs)
    configs = analyze_configuration(root_path, fs)
    arch = detect_architecture_signals(fs, symbols, deps)
    findings = build_findings(fs, symbols, deps, tests, configs, arch)

    sec_signals, sec_findings = detect_security_signals(root_path, fs)
    findings.extend(sec_findings)
    perf_signals = detect_performance_signals(root_path, fs)

    if not any(s.kind == "entry_point" for s in arch):
        unknowns.append("No entry points confidently identified.")
    if not tests.tests:
        unknowns.append("No tests detected.")
    if not configs.configurations:
        unknowns.append("No configuration manifests detected.")

    languages = sorted({m.language for m in symbols.modules if m.language})
    if not languages:
        unknowns.append("No parseable languages detected with current parsers.")

    meta = SnapshotMeta(
        analyzed_at=utc_now_iso(),
        git_revision=git.commit,
        git_branch=git.branch,
        root=str(root_path),
        included_file_count=fs.included_count or len([f for f in fs.files if not f.ignored]),
        excluded_file_count=fs.excluded_count,
        parsers_used=list(symbols.parsers_used),
    )

    snapshot = CodebaseSnapshot(
        id=new_snapshot_id(str(root_path), git.commit),
        meta=meta,
        files=[f.to_dict() for f in fs.files],
        directories=[d.to_dict() for d in fs.directories],
        symbols=[s.to_dict() for s in symbols.symbols],
        modules=[m.to_dict() for m in symbols.modules],
        dependencies=[e.to_dict() for e in deps.edges],
        tests=[t.to_dict() for t in tests.tests],
        configurations=[c.to_dict() for c in configs.configurations],
        architecture_signals=[s.to_dict() for s in arch],
        findings=[f.to_dict() for f in findings],
        errors=errors,
        unknowns=unknowns,
        metrics={
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "files_processed": len(fs.files),
            "symbols_count": len(symbols.symbols),
            "dependency_edges": len(deps.edges),
            "findings_count": len(findings),
            "languages": languages,
            "approx_max_rss_mb": _rss_mb(),
            "error_count": len(errors),
        },
    )
    evidence = collect_evidence(snapshot, findings)
    snapshot.evidence = [e.to_dict() for e in evidence]
    snapshot.meta.content_fingerprint = snapshot.fingerprint()

    return AnalysisBundle(
        snapshot=snapshot,
        git=git.to_dict(),
        security_signals=[s.to_dict() for s in sec_signals],
        performance_signals=[p.to_dict() for p in perf_signals],
        impact_notes=[
            "Use codebase.impact.analyze_module_impact for module blast-radius queries.",
        ],
    )


def analyze_repository_safe(root: str | Path) -> AnalysisBundle:
    """Analyze and capture unexpected failures into snapshot errors when possible."""
    try:
        return analyze_repository(root)
    except Exception as exc:  # noqa: BLE001
        root_path = Path(root).resolve()
        git = inspect_git(root_path)
        snap = CodebaseSnapshot(
            id=new_snapshot_id(str(root_path), git.commit),
            meta=SnapshotMeta(
                analyzed_at=utc_now_iso(),
                git_revision=git.commit,
                git_branch=git.branch,
                root=str(root_path),
            ),
            errors=[AnalysisError(stage="analyze", message=f"{exc}\n{traceback.format_exc()}")],
            unknowns=["Analysis failed before full inventory."],
        )
        return AnalysisBundle(snapshot=snap, git=git.to_dict())
