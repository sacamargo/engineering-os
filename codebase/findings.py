"""Codebase findings — suspicions with evidence; never decisions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from codebase.architecture import ArchitectureSignal
from codebase.config_intel import ConfigIntelligence
from codebase.dependencies import DependencyGraph
from codebase.fs_index import FilesystemIndex
from codebase.symbols import SymbolIndex
from codebase.tests_intel import TestIntelligence

Severity = Literal["info", "low", "medium", "high", "critical"]
Confidence = Literal["observed", "inferred", "unknown"]
FindingStatus = Literal["open", "acknowledged", "resolved", "false_positive"]


@dataclass
class CodebaseFinding:
    id: str
    kind: str
    severity: Severity
    confidence: Confidence
    explanation: str
    location: str
    potential_impact: str
    evidence: list[str] = field(default_factory=list)
    status: FindingStatus = "open"
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _finding(
    *,
    kind: str,
    severity: Severity,
    confidence: Confidence,
    explanation: str,
    location: str,
    potential_impact: str,
    evidence: list[str],
    details: dict[str, Any] | None = None,
) -> CodebaseFinding:
    digest = abs(hash((kind, location, explanation))) % 10**10
    return CodebaseFinding(
        id=f"eos.finding.{kind}.{digest}",
        kind=kind,
        severity=severity,
        confidence=confidence,
        explanation=explanation,
        location=location,
        potential_impact=potential_impact,
        evidence=evidence,
        details=details or {},
    )


def build_findings(
    fs: FilesystemIndex,
    symbols: SymbolIndex,
    deps: DependencyGraph,
    tests: TestIntelligence,
    configs: ConfigIntelligence,
    signals: list[ArchitectureSignal],
) -> list[CodebaseFinding]:
    """Derive findings from observations/signals. Finding ≠ decision."""
    findings: list[CodebaseFinding] = []

    for sig in signals:
        if sig.kind == "circular_dependency":
            findings.append(
                _finding(
                    kind="circular_dependency",
                    severity="medium",
                    confidence="inferred",
                    explanation=sig.summary,
                    location=",".join(sig.evidence) or "unknown",
                    potential_impact="Refactor/build order may be fragile; runtime cycles unproven.",
                    evidence=list(sig.evidence) + [f"signal:{sig.id}"],
                )
            )
        elif sig.kind == "orphan_module":
            findings.append(
                _finding(
                    kind="dead_module",
                    severity="low",
                    confidence="inferred",
                    explanation=sig.summary,
                    location=sig.evidence[0] if sig.evidence else "unknown",
                    potential_impact="May be unused or entry-point outside import graph.",
                    evidence=list(sig.evidence) + [f"signal:{sig.id}"],
                )
            )

    # Missing tests (heuristic): source modules with no approximate test link
    tested_targets = {t for rec in tests.tests for t in rec.linked_targets}
    source_modules = [
        m.path
        for m in symbols.modules
        if m.path.endswith(".py")
        and "test" not in m.path.lower()
        and not m.path.endswith("__init__.py")
    ]
    if source_modules and not tests.tests:
        findings.append(
            _finding(
                kind="missing_tests",
                severity="medium",
                confidence="observed",
                explanation="Source modules observed but no test files detected",
                location="repository",
                potential_impact="Refactor/migrate risk elevated without automated checks.",
                evidence=[f"source_modules:{len(source_modules)}", "tests:0"],
            )
        )
    elif source_modules and tests.tests:
        unlinked = [p for p in source_modules if p not in tested_targets]
        if len(unlinked) > len(source_modules) * 0.5:
            findings.append(
                _finding(
                    kind="missing_tests",
                    severity="low",
                    confidence="inferred",
                    explanation="Many source modules lack approximate test links",
                    location="repository",
                    potential_impact="Coverage unknown; links are approximate only.",
                    evidence=[
                        f"unlinked:{len(unlinked)}",
                        f"source:{len(source_modules)}",
                        "coverage:unknown",
                    ],
                )
            )

    # Sensitive inventory
    for f in fs.files:
        if f.sensitive:
            findings.append(
                _finding(
                    kind="sensitive_path",
                    severity="high",
                    confidence="observed",
                    explanation=f"Sensitive path inventoried without content read: {f.path}",
                    location=f.path,
                    potential_impact="Secret leakage risk if committed; content not analyzed.",
                    evidence=[f.path, f"content_readable:{f.content_readable}"],
                )
            )

    # High fan-in coupling (simple)
    fan_in: dict[str, int] = {}
    for e in deps.edges:
        if e.kind == "import" and not e.external:
            fan_in[e.target] = fan_in.get(e.target, 0) + 1
    for target, count in fan_in.items():
        if count >= 5:
            findings.append(
                _finding(
                    kind="suspicious_coupling",
                    severity="low",
                    confidence="inferred",
                    explanation=f"Module '{target}' has high observed import fan-in ({count})",
                    location=target,
                    potential_impact="Changes may ripple widely; semantic centrality unknown.",
                    evidence=[f"fan_in:{count}"],
                )
            )

    # Config detected without env template when .env sensitive exists
    has_env_template = any(c.config_type == "env_template" for c in configs.configurations)
    has_real_env = any(f.path.endswith(".env") or "/.env." in f.path for f in fs.files if f.sensitive)
    if has_real_env and not has_env_template:
        findings.append(
            _finding(
                kind="unsafe_configuration",
                severity="medium",
                confidence="inferred",
                explanation="Sensitive env file present without observed .env.example template",
                location=".env",
                potential_impact="Onboarding/secret hygiene may be weak.",
                evidence=["sensitive:.env", "env_template:absent"],
            )
        )

    return findings
