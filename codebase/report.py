"""Human-readable report from an analysis bundle."""

from __future__ import annotations

from typing import Any

from codebase.analyze import AnalysisBundle


def render_human_report(bundle: AnalysisBundle) -> str:
    snap = bundle.snapshot
    meta = snap.meta
    metrics = snap.metrics or {}
    lines: list[str] = []

    def section(title: str) -> None:
        lines.append("")
        lines.append(f"## {title}")
        lines.append("")

    lines.append("# Codebase Intelligence Report")
    lines.append("")
    lines.append(f"- Snapshot: `{snap.id}`")
    lines.append(f"- Analyzed at: {meta.analyzed_at}")
    lines.append(f"- Root: `{meta.root}`")
    lines.append(f"- Git: {meta.git_branch or 'unknown'} @ {meta.git_revision or 'none'}")
    lines.append(f"- Fingerprint: `{meta.content_fingerprint or snap.fingerprint()}`")
    lines.append(f"- Duration: {metrics.get('duration_seconds', 'unknown')}s")

    section("1. Repository summary")
    lines.append(f"- Files indexed: {meta.included_file_count}")
    lines.append(f"- Files excluded: {meta.excluded_file_count}")
    lines.append(f"- Symbols: {metrics.get('symbols_count', len(snap.symbols))}")
    lines.append(f"- Dependency edges: {metrics.get('dependency_edges', len(snap.dependencies))}")
    lines.append(f"- Findings: {metrics.get('findings_count', len(snap.findings))}")

    section("2. Languages")
    langs = metrics.get("languages") or sorted({m.get("language") for m in snap.modules if m.get("language")})
    if langs:
        for lang in langs:
            lines.append(f"- {lang} (observed via parsers)")
    else:
        lines.append("- unknown")
    lines.append(f"- Parsers used: {', '.join(meta.parsers_used) or 'none'}")

    section("3. Architecture signals")
    if snap.architecture_signals:
        for s in snap.architecture_signals[:30]:
            lines.append(
                f"- [{s.get('certainty', 'unknown')}] {s.get('kind')}: {s.get('summary')}"
            )
    else:
        lines.append("- unknown")

    section("4. Modules")
    for m in snap.modules[:40]:
        lines.append(f"- {m.get('path')} ({m.get('language')}) symbols={len(m.get('symbol_ids') or [])}")
    if len(snap.modules) > 40:
        lines.append(f"- … {len(snap.modules) - 40} more")

    section("5. Dependencies")
    internal = [d for d in snap.dependencies if not d.get("external") and d.get("kind") == "import"]
    external = [d for d in snap.dependencies if d.get("external")]
    lines.append(f"- Internal import edges: {len(internal)}")
    lines.append(f"- External edges: {len(external)}")
    for d in (internal + external)[:25]:
        lines.append(
            f"- [{d.get('certainty')}] {d.get('source_path')} → {d.get('target')} ({d.get('kind')})"
        )

    section("6. Tests")
    if snap.tests:
        for t in snap.tests[:30]:
            lines.append(
                f"- {t.get('path')} framework={t.get('framework') or 'unknown'} "
                f"coverage={t.get('coverage')} link={t.get('link_certainty')}"
            )
    else:
        lines.append("- unknown / none detected")

    section("7. Configuration")
    if snap.configurations:
        for c in snap.configurations:
            lines.append(
                f"- [{c.get('detection')}/{c.get('certainty')}] {c.get('path')} ({c.get('config_type')})"
            )
    else:
        lines.append("- unknown / none detected")

    section("8. Findings")
    if snap.findings:
        for f in snap.findings[:40]:
            lines.append(
                f"- [{f.get('severity')}|{f.get('confidence')}] {f.get('kind')}: {f.get('explanation')}"
            )
            lines.append(f"  evidence: {', '.join(f.get('evidence') or [])}")
    else:
        lines.append("- none")

    section("9. Unknowns")
    for u in snap.unknowns or ["none declared"]:
        lines.append(f"- {u}")

    section("10. Evidence")
    for e in (snap.evidence or [])[:30]:
        lines.append(f"- [{e.get('certainty')}|{e.get('kind')}] {e.get('claim')}")
        lines.append(f"  pointer: {e.get('pointer')}")

    section("11. Suggested next investigation")
    lines.append("- Inspect high-severity findings with observed evidence first.")
    lines.append("- Confirm inferred architecture signals against human knowledge.")
    lines.append("- Run targeted tests before any refactor/migrate plan.")
    if bundle.security_signals:
        lines.append("- Review security signals (observed vs inferred) with a security review.")
    if bundle.performance_signals:
        lines.append("- Treat performance signals as static heuristics only — measure runtime next.")

    section("Security signals")
    for s in bundle.security_signals[:20]:
        lines.append(f"- [{s.get('certainty')}] {s.get('kind')}: {s.get('summary')}")
    if not bundle.security_signals:
        lines.append("- none detected by static heuristics")

    section("Performance signals")
    for s in bundle.performance_signals[:20]:
        lines.append(f"- [{s.get('certainty')}] {s.get('kind')}: {s.get('summary')}")
    if not bundle.performance_signals:
        lines.append("- none detected by static heuristics")

    lines.append("")
    return "\n".join(lines)


def bundle_to_machine_json(bundle: AnalysisBundle) -> dict[str, Any]:
    """Orchestrator-consumable JSON (vendor-neutral)."""
    return {
        "schema": "eos.codebase.analysis.v1",
        "snapshot": bundle.snapshot.to_dict(),
        "git": bundle.git,
        "security_signals": bundle.security_signals,
        "performance_signals": bundle.performance_signals,
        "epistemic_levels": ["observed", "inferred", "unknown"],
        "notes": bundle.impact_notes
        + [
            "Codebase Intelligence is evidence infrastructure, not a Capability.",
            "Do not treat findings as decisions.",
        ],
    }
