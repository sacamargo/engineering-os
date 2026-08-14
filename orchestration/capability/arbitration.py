"""Multi-capability arbitration.

Separates selection marks from execution ordering.

related_capability => RELATED adjacency only
Artifact prerequisites => execution dependencies (handled by plan/dependency modules)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from orchestration.capability import CapabilityCandidate, CapabilityResolution, MissingCapability
from orchestration.catalog import CatalogUnit
from orchestration.intent import StructuredIntent


@dataclass
class ArbitrationResult:
    primary: str | None
    secondary: list[str]
    related: list[str]
    conflicting: list[str]
    insufficient: list[dict[str, Any]]
    selected: list[str]
    notes: list[str] = field(default_factory=list)
    candidates: list[CapabilityCandidate] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data


def arbitrate_capabilities(
    intent: StructuredIntent,
    resolution: CapabilityResolution,
    catalog: dict[str, CatalogUnit] | None = None,
) -> ArbitrationResult:
    """Assign PRIMARY/SECONDARY/RELATED/CONFLICTING/INSUFFICIENT without inventing an execution DAG."""
    notes = [
        "Arbitration selects Capabilities only.",
        "Execution order must come from artifact/task dependencies, not related_capability edges.",
    ]

    candidates = list(resolution.candidates)
    primary = resolution.primary

    # For product build/design, prefer system-architecture as primary when present —
    # unless audit/incident intents dominate.
    intents = set(intent.possible_intents)
    if intents & {"build", "design"} and not (intents & {"audit", "investigate_incident"}):
        arch = "eos.capability.design.system-architecture"
        if any(c.capability_id == arch for c in candidates):
            primary = arch
            notes.append(
                "Build/design arbitration prefers system-architecture as PRIMARY when selected; "
                "security/testing/observability remain SECONDARY."
            )
    if "audit" in intents and any(
        c.capability_id == "eos.capability.security.review" for c in candidates
    ):
        primary = "eos.capability.security.review"
        notes.append("Audit intents prefer security.review as PRIMARY.")

    secondary = [
        c.capability_id
        for c in candidates
        if c.capability_id != primary and c.confidence in {"high", "medium"}
    ]
    related = [r for r in resolution.related if r not in secondary and r != primary]

    # Ensure related suggested from catalog are marked related if not selected secondary
    for c in candidates:
        if c.capability_id == primary:
            c.mark = "primary"
        elif c.capability_id in secondary:
            c.mark = "secondary"
        elif c.capability_id in related:
            c.mark = "related"

    conflicting = list(resolution.conflicting)
    # Competing intents: audit-only vs build-heavy
    if "audit" in intents and "build" in intents:
        conflicting.append("audit_and_build_bundled")
        notes.append("Bundled audit+build: keep both Capabilities selectable; do not collapse into one.")

    insufficient = [
        {
            "kind": "MISSING_CAPABILITY",
            "area": m.area,
            "reason": m.reason,
            "severity": m.severity,
            "blocking": m.blocking,
            "mark": "insufficient",
        }
        for m in resolution.missing
    ]

    # If only missing and no candidates
    if not candidates and insufficient:
        notes.append("No selectable Capability; continue only with gap/escalation handling.")

    selected = []
    if primary:
        selected.append(primary)
    for sid in secondary:
        if sid not in selected:
            selected.append(sid)

    # Soft-add high-value related only when already scored as candidate with medium+ — do not auto-chain
    for rid in related:
        if rid in {c.capability_id for c in candidates} and rid not in selected:
            # keep as related suggestion, not selected for plan unless secondary
            pass

    return ArbitrationResult(
        primary=primary,
        secondary=secondary,
        related=related,
        conflicting=conflicting,
        insufficient=insufficient,
        selected=selected,
        notes=notes,
        candidates=candidates,
    )
