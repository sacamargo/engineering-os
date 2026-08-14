"""Capability Resolution — map StructuredIntent to catalog Capability candidates.

Never invents Capability IDs. Emits MISSING_CAPABILITY gaps for uncovered domains.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from orchestration.catalog import CatalogUnit, load_capabilities
from orchestration.intent import StructuredIntent

Confidence = Literal["high", "medium", "low"]
RoleMark = Literal["primary", "secondary", "related", "conflicting", "insufficient"]


@dataclass
class CapabilityCandidate:
    capability_id: str
    confidence: Confidence
    reason: str
    evidence: list[str] = field(default_factory=list)
    mark: RoleMark = "secondary"
    possible_conflicts: list[str] = field(default_factory=list)
    required_clarification: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MissingCapability:
    area: str
    reason: str
    severity: str = "high"
    blocking: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CapabilityResolution:
    candidates: list[CapabilityCandidate]
    primary: str | None
    secondary: list[str]
    related: list[str]
    conflicting: list[str]
    missing: list[MissingCapability]
    catalog_size: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidates": [c.to_dict() for c in self.candidates],
            "primary": self.primary,
            "secondary": self.secondary,
            "related": self.related,
            "conflicting": self.conflicting,
            "missing": [m.to_dict() for m in self.missing],
            "catalog_size": self.catalog_size,
        }


# Domain / intent hints → areas that may lack Capabilities (not invented IDs)
DOMAIN_GAP_AREAS = {
    "iot": "iot_device_engineering",
    "networking": "networking",
    "cloud": "cloud_mobile",
    "electrical": "electrical_engineering",
    "physical_access": "physical_access_control",
    "payments": "payments_billing",
    "database": "database_engineering",
    "frontend": "frontend_implementation",
    "backend": "backend_implementation",
    "delivery": "devops_delivery",
}

CAPABILITY_DOMAIN_AFFINITY = {
    "eos.capability.design.system-architecture": {
        "domains": {"architecture", "iot", "cloud", "networking"},
        "intents": {"build", "design", "migrate", "refactor", "analyze"},
        "keywords": ("architect", "arquitect", "structure", "boundary", "saas", "system", "sistema", "build", "constru"),
    },
    "eos.capability.security.review": {
        "domains": {"security"},
        "intents": {"audit", "build", "design", "investigate_incident"},
        "keywords": ("secur", "segura", "audit", "vulnerab", "threat", "amenaza"),
    },
    "eos.capability.quality.test-planning": {
        "domains": {"testing"},
        "intents": {"build", "refactor", "migrate", "optimize"},
        "keywords": ("test", "testeable", "qa", "quality", "calidad", "regression"),
    },
    "eos.capability.operations.observability": {
        "domains": {"observability"},
        "intents": {"build", "investigate_incident", "optimize", "analyze"},
        "keywords": ("observab", "metric", "monitor", "slo", "telemetry", "500", "incident", "incidente"),
    },
}


def _score_capability(intent: StructuredIntent, cap: CatalogUnit) -> tuple[float, list[str]]:
    """Score using optional affinity hints plus live catalog metadata.

    Capabilities absent from affinity still score via entry_signals/tags/domain/summary.
    """
    evidence: list[str] = []
    score = 0.0
    domains = {s.value for s in intent.signals if s.kind == "domain"}
    intents = set(intent.possible_intents)
    utterance = intent.utterance.lower()

    affinity = CAPABILITY_DOMAIN_AFFINITY.get(cap.id, {})
    for d in affinity.get("domains", set()):
        if d in domains:
            score += 2.0
            evidence.append(f"domain:{d}")
    for i in affinity.get("intents", set()):
        if i in intents:
            score += 1.0
            evidence.append(f"intent:{i}")
    for kw in affinity.get("keywords", ()):
        if kw in utterance:
            score += 1.5
            evidence.append(f"keyword:{kw}")

    # Metadata path — enables new Capabilities without editing affinity map
    blob = " ".join(
        [
            cap.summary,
            cap.purpose,
            cap.applicability,
            cap.domain,
            " ".join(cap.tags),
            " ".join(cap.entry_signals),
        ]
    ).lower()
    for domain in domains:
        if domain and domain in blob:
            score += 1.5
            evidence.append(f"meta_domain:{domain}")
    for intent_name in intents:
        token = intent_name.replace("_", " ")
        if token and token in blob:
            score += 0.8
            evidence.append(f"meta_intent:{intent_name}")
    for signal in cap.entry_signals:
        words = [w for w in re_split_words(signal) if len(w) >= 4]
        if any(w in utterance for w in words):
            score += 1.2
            evidence.append("entry_signal_overlap")
            break
    for tag in cap.tags:
        if tag.lower() in utterance or tag.lower() in domains:
            score += 0.5
            evidence.append(f"tag:{tag}")

    limits = cap.limits.lower()
    if "audit" in intents and cap.id.endswith("system-architecture") and "security" in domains:
        if "build" not in intents and "design" not in intents:
            score -= 1.5

    if "incident" in limits and "investigate_incident" in intents and "observability" not in cap.id:
        if "does not" in limits or "incident response" in limits:
            score -= 0.5

    # Build/design product intents: architecture is typically the structural primary
    if cap.id.endswith("system-architecture") and intents & {"build", "design"}:
        if any(
            token in utterance
            for token in ("saas", "system", "sistema", "aplicación", "application", "constru", "build")
        ):
            score += 5.0
            evidence.append("build_design_architecture_primary_boost")

    return score, evidence


def re_split_words(text: str) -> list[str]:
    import re

    return re.findall(r"[a-z0-9]+", text.lower())


def _confidence(score: float) -> Confidence:
    if score >= 4.0:
        return "high"
    if score >= 2.0:
        return "medium"
    return "low"


def resolve_capabilities(
    intent: StructuredIntent,
    repo_root: Path | None = None,
    catalog: dict[str, CatalogUnit] | None = None,
) -> CapabilityResolution:
    caps = catalog if catalog is not None else load_capabilities(repo_root)
    scored: list[tuple[float, CapabilityCandidate]] = []

    for cap in caps.values():
        score, evidence = _score_capability(intent, cap)
        if score <= 0:
            continue
        scored.append(
            (
                score,
                CapabilityCandidate(
                    capability_id=cap.id,
                    confidence=_confidence(score),
                    reason=f"score={score:.1f} against live catalog metadata",
                    evidence=evidence,
                    mark="secondary",
                ),
            )
        )

    scored.sort(key=lambda item: item[0], reverse=True)
    candidates = [c for _, c in scored]

    primary = candidates[0].capability_id if candidates else None
    if primary:
        candidates[0].mark = "primary"

    # Soft related from catalog relationships of primary
    related: list[str] = []
    if primary and primary in caps:
        for rel in caps[primary].relationships:
            if rel.get("type") == "related_capability":
                target = rel.get("target")
                if target and target in caps and target != primary:
                    related.append(target)

    secondary = [c.capability_id for c in candidates[1:]]
    # Promote high-confidence non-primary into secondary even if also related
    for c in candidates[1:]:
        if c.confidence in {"high", "medium"}:
            c.mark = "secondary"

    for c in candidates:
        if c.capability_id in related and c.capability_id != primary:
            if c.mark == "secondary" and c.confidence == "low":
                c.mark = "related"

    # Missing capability areas from domains without matching Capability
    covered_domains: set[str] = set()
    for c in candidates:
        affinity = CAPABILITY_DOMAIN_AFFINITY.get(c.capability_id, {})
        covered_domains |= set(affinity.get("domains", set()))

    missing: list[MissingCapability] = []
    domains = {s.value for s in intent.signals if s.kind == "domain"}
    for domain in domains:
        if domain in covered_domains:
            continue
        area = DOMAIN_GAP_AREAS.get(domain)
        if not area:
            continue
        blocking = domain in {"electrical", "physical_access"}
        missing.append(
            MissingCapability(
                area=area,
                reason=f"Domain '{domain}' signaled but no active Capability covers it",
                severity="critical" if blocking else "high",
                blocking=blocking,
            )
        )

    # Build/booking without backend/db capabilities
    if "build" in intent.possible_intents:
        for area, reason in (
            ("backend_implementation", "Build intent typically needs backend implementation Capability"),
            ("database_engineering", "Build intent typically needs database Capability"),
            ("frontend_implementation", "Build intent typically needs frontend Capability"),
            ("devops_delivery", "Build intent typically needs delivery/DevOps Capability"),
        ):
            if not any(m.area == area for m in missing):
                missing.append(
                    MissingCapability(area=area, reason=reason, severity="medium", blocking=False)
                )

    conflicting: list[str] = []
    # Example conflict mark: pure incident vs pure greenfield architecture-only without ops
    if "investigate_incident" in intent.possible_intents and primary and primary.endswith("system-architecture"):
        if not any(c.capability_id.endswith("observability") for c in candidates):
            conflicting.append("incident_intent_with_architecture_primary")

    if not candidates:
        missing.append(
            MissingCapability(
                area="unmatched_intent",
                reason="No active Capability scored against the framed intent",
                severity="critical",
                blocking=True,
            )
        )

    return CapabilityResolution(
        candidates=candidates,
        primary=primary,
        secondary=secondary,
        related=related,
        conflicting=conflicting,
        missing=missing,
        catalog_size=len(caps),
    )
