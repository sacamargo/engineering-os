"""Skill candidate routing — after Capability resolution; never replaces Capabilities.

Uses structured signals + trigger polarity. Avoid keyword-only false positives
(e.g. payment gateway ≠ physical access gate).
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from skillpacks.model import SkillPack
from skillpacks.registry import SkillRegistry, load_registry

Confidence = str  # high | medium | low | none


@dataclass
class SkillCandidate:
    skill_id: str
    version: str
    status: str
    confidence: Confidence
    score: float
    reason: str
    trigger_evidence: list[str] = field(default_factory=list)
    negative_evidence: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    role: str = "supporting"  # primary | supporting | transversal | unavailable
    selectable: bool = False
    fallback: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SkillResolution:
    candidates: list[SkillCandidate]
    selected: list[str]
    unavailable: list[str]
    rejected: list[dict[str, Any]]
    arbitration_notes: list[str]
    why: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidates": [c.to_dict() for c in self.candidates],
            "selected": list(self.selected),
            "unavailable": list(self.unavailable),
            "rejected": list(self.rejected),
            "arbitration_notes": list(self.arbitration_notes),
            "why": list(self.why),
        }


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _has_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    """Match phrases with word boundaries for short tokens to avoid 'ui' in 'ingestion'."""
    for p in phrases:
        if len(p) <= 3:
            if re.search(rf"(?<![a-z0-9]){re.escape(p)}(?![a-z0-9])", text):
                return True
        elif p in text:
            return True
    return False


def _intent_signal_values(intent: dict[str, Any]) -> set[tuple[str, str]]:
    values: set[tuple[str, str]] = set()
    for item in intent.get("possible_intents") or []:
        values.add(("intent_class", str(item)))
    for sig in intent.get("signals") or []:
        values.add((str(sig.get("kind") or sig.get("type") or ""), str(sig.get("value") or "")))
    for d in intent.get("domains") or []:
        values.add(("domain", str(d)))
    utterance = _norm(str(intent.get("utterance") or intent.get("raw_utterance") or ""))
    if _has_phrase(utterance, ("landing", "conversion", "positioning", "marketing", "growth")):
        values.add(("domain", "marketing"))
    if _has_phrase(
        utterance,
        (
            "ux",
            "ui",
            "wireframe",
            "user flow",
            "user experience",
            "interface",
            "checkout ux",
            "landing page",
            "mobile app",
            "ios",
            "android",
            "responsive",
            "design a",
            "diseñ",
        ),
    ):
        values.add(("domain", "ux_ui"))
    if _has_phrase(utterance, ("slop", "quality review", "copy review", "design review")):
        values.add(("domain", "quality_review"))
    if _has_phrase(utterance, ("context engineering", "assemble context", "prompt context")):
        values.add(("domain", "context_engineering"))
    if _has_phrase(utterance, ("payment gateway", "pasarela", "billing", "stripe", "checkout payment")):
        values.add(("domain", "payments"))
        values.add(("negative", "physical_access"))
    if _has_phrase(
        utterance, ("physical gate", "access control", "torniquete", "control de acceso físico")
    ):
        values.add(("domain", "physical_access"))
    if _has_phrase(utterance, ("database migration", "schema migration", "pure database")):
        values.add(("domain", "database"))
        values.add(("negative", "ux_ui_primary"))
        values.add(("negative", "marketing"))
    if _has_phrase(utterance, ("backend bug", "fix bug", "null pointer", "stack trace")):
        values.add(("domain", "backend_bugfix"))
        values.add(("negative", "marketing"))
        values.add(("negative", "ux_ui_primary"))
    if _has_phrase(utterance, ("system architecture", "architecture decision", "threat model only")):
        values.add(("negative", "stop_slop_as_architecture"))
    if _has_phrase(utterance, ("build an api", "rest api", "grpc", "api only")) and not _has_phrase(
        utterance, ("ux", "ui", "mobile app", "landing page", "interface")
    ):
        values.add(("domain", "api"))
        values.add(("negative", "ux_ui_primary"))
    return {(k, v) for k, v in values if k and v}


def score_pack(
    pack: SkillPack,
    *,
    intent: dict[str, Any],
    capability_ids: set[str],
) -> SkillCandidate:
    signals = _intent_signal_values(intent)
    score = 0.0
    evidence: list[str] = []
    negative: list[str] = []
    conflicts: list[str] = []

    for trig in pack.triggers:
        key = (trig.signal_type, trig.value)
        matched = key in signals or any(
            trig.signal_type == s[0] and trig.value in s[1] for s in signals
        )
        # Also match domain triggers against derived domains
        if not matched and trig.signal_type == "domain":
            matched = ("domain", trig.value) in signals
        if trig.polarity == "negative":
            if matched:
                score -= abs(trig.weight) * 2
                negative.append(f"negative trigger hit: {trig.signal_type}={trig.value}")
            continue
        if matched:
            score += abs(trig.weight)
            evidence.append(f"trigger:{trig.signal_type}={trig.value}")

    # Capability association boost (association, not identity)
    cap_hits = [c for c in pack.capability_relationships if c in capability_ids]
    if cap_hits:
        score += 0.5 * len(cap_hits)
        evidence.append(f"capability_affinity:{','.join(cap_hits)}")

    # Explicit global negatives from intent
    if ("negative", "physical_access") in signals and "physical" in pack.category:
        score -= 5
        negative.append("payment/gateway context rejects physical_access skill category")
    if ("negative", "ux_ui_primary") in signals and pack.category in {"design", "ux", "ui"}:
        score -= 2
        negative.append("API/DB/bugfix intent reduces UX primary selection")
    if ("negative", "marketing") in signals and pack.category == "marketing":
        score -= 5
        negative.append("pure technical/bugfix intent rejects marketing skill")
    if ("negative", "stop_slop_as_architecture") in signals and "stop-slop" in pack.id:
        score -= 5
        negative.append("Stop Slop is not architecture authority")

    selectable = pack.is_selectable()
    if pack.status == "unavailable" or pack.provenance.unavailable_source_content:
        return SkillCandidate(
            skill_id=pack.id,
            version=pack.version,
            status=pack.status,
            confidence="none",
            score=score,
            reason="Skill source unavailable — fail closed; do not fabricate content",
            trigger_evidence=evidence,
            negative_evidence=negative,
            conflicts=conflicts,
            role="unavailable",
            selectable=False,
            fallback="NEEDS_SOURCE",
        )

    if score <= 0:
        return SkillCandidate(
            skill_id=pack.id,
            version=pack.version,
            status=pack.status,
            confidence="none",
            score=score,
            reason="No positive structured applicability",
            trigger_evidence=evidence,
            negative_evidence=negative or ["no matching triggers"],
            conflicts=conflicts,
            role="supporting",
            selectable=False,
        )

    if score >= 2.0:
        confidence: Confidence = "high"
        role = "primary" if pack.category != "quality" else "transversal"
    elif score >= 1.0:
        confidence = "medium"
        role = "supporting" if pack.category != "quality" else "transversal"
    else:
        confidence = "low"
        role = "supporting"

    if "transversal" in {r.kind for r in pack.composition_rules} or pack.category == "quality":
        role = "transversal"

    return SkillCandidate(
        skill_id=pack.id,
        version=pack.version,
        status=pack.status,
        confidence=confidence,
        score=score,
        reason=f"Structured signal score={score:.2f}",
        trigger_evidence=evidence,
        negative_evidence=negative,
        conflicts=conflicts,
        role=role,
        selectable=selectable and confidence != "none",
    )


def resolve_skills(
    intent: dict[str, Any],
    capability_ids: list[str] | set[str],
    *,
    registry: SkillRegistry | None = None,
    registry_root: Path | None = None,
    min_score: float = 0.75,
) -> SkillResolution:
    """Resolve Skill candidates from registry data (not Orchestrator hardcoding)."""
    reg = registry or load_registry(registry_root)
    caps = set(capability_ids)
    candidates = [score_pack(p, intent=intent, capability_ids=caps) for p in reg.packs.values()]
    candidates.sort(key=lambda c: c.score, reverse=True)

    selected: list[str] = []
    unavailable: list[str] = []
    rejected: list[dict[str, Any]] = []
    why: list[str] = []
    notes: list[str] = [
        "Skills are selected after Capabilities; Skills do not replace Capabilities.",
        "Selection is registry-driven; adding a Skill does not require Orchestrator core edits.",
    ]

    for c in candidates:
        if c.role == "unavailable" or c.status == "unavailable":
            unavailable.append(c.skill_id)
            why.append(f"{c.skill_id}: unavailable — {c.reason}")
            continue
        if c.selectable and c.score >= min_score:
            selected.append(c.skill_id)
            why.append(
                f"{c.skill_id}: selected ({c.confidence}) because {'; '.join(c.trigger_evidence) or c.reason}"
            )
        else:
            rejected.append(
                {
                    "skill_id": c.skill_id,
                    "reason": c.reason,
                    "negative_evidence": c.negative_evidence,
                }
            )

    # Arbitration: do not select every pack; cap primary-like selections
    if len(selected) > 4:
        notes.append("Too many skills matched; keeping top-scoring four")
        selected = selected[:4]

    return SkillResolution(
        candidates=candidates,
        selected=selected,
        unavailable=unavailable,
        rejected=rejected,
        arbitration_notes=notes,
        why=why,
    )
