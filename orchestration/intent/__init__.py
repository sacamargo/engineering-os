"""Intent Intake — convert a human utterance into a structured Intent.

Does not invent facts. Distinguishes KNOWN / ASSUMED / UNKNOWN / REQUIRED.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Certainty = Literal["known", "assumed", "unknown", "required"]


@dataclass
class Fact:
    key: str
    value: str
    certainty: Certainty
    reason: str = ""


@dataclass
class IntentSignal:
    kind: str
    value: str
    weight: float = 1.0


@dataclass
class StructuredIntent:
    utterance: str
    language: str
    objective: str
    constraints: list[str] = field(default_factory=list)
    context: list[Fact] = field(default_factory=list)
    uncertainties: list[Fact] = field(default_factory=list)
    signals: list[IntentSignal] = field(default_factory=list)
    possible_intents: list[str] = field(default_factory=list)
    clarifying_questions: list[str] = field(default_factory=list)
    risk_signals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).strip().lower()
    return re.sub(r"\s+", " ", text)


def detect_language(utterance: str) -> str:
    """Heuristic language tag. Not a full detector."""
    lowered = utterance.lower()
    spanish_markers = (
        "quiero",
        "necesito",
        "construye",
        "construir",
        "analiza",
        "audita",
        "refactoriza",
        "diseña",
        "diseñar",
        "investiga",
        "cancha",
        "pádel",
        "padel",
        "debe ser",
        "aplicación",
        "repositorio",
    )
    hits = sum(1 for m in spanish_markers if m in lowered)
    if hits >= 1:
        return "es"
    return "en"


def _has_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(p in text for p in phrases)


def intake_intent(utterance: str, context: dict[str, Any] | None = None) -> StructuredIntent:
    """Frame a user utterance into a StructuredIntent without inventing product details."""
    if not isinstance(utterance, str) or not utterance.strip():
        raise ValueError("utterance must be a non-empty string")

    context = context or {}
    norm = _normalize(utterance)
    language = detect_language(utterance)

    signals: list[IntentSignal] = []
    possible: list[str] = []
    constraints: list[str] = []
    risks: list[str] = []
    uncertainties: list[Fact] = []
    clarifying: list[str] = []
    facts: list[Fact] = []

    # Known context passthrough only
    for key, value in context.items():
        if value is None or value == "":
            continue
        facts.append(
            Fact(key=str(key), value=str(value), certainty="known", reason="provided_context")
        )

    # Intent class signals
    build_phrases = (
        "build",
        "constru",
        "create",
        "crear",
        "implement",
        "saas",
        "aplicación",
        "application",
        "automatiz",
    )
    design_phrases = ("design", "diseñ", "architecture", "arquitectura", "structure", "estructura")
    audit_phrases = (
        "audit",
        "audita",
        "vulnerab",
        "security review",
        "revisión de seguridad",
        "problemas de seguridad",
        "security problems",
        "seguridad",
        "security",
    )
    analyze_phrases = ("analyze", "analiza", "analyse", "repository", "repositorio", "codebase")
    refactor_phrases = ("refactor", "refactoriza")
    incident_phrases = (
        "incident",
        "incidente",
        "500",
        "production",
        "producción",
        "outage",
        "error",
        "investigate",
        "investiga",
    )
    optimize_phrases = ("optimiz", "performance", "slow", "lento")
    migrate_phrases = ("migrat", "legacy", "legado")

    if _has_any(norm, build_phrases):
        signals.append(IntentSignal("intent_class", "build", 1.0))
        possible.append("build")
    if _has_any(norm, design_phrases):
        signals.append(IntentSignal("intent_class", "design", 1.0))
        possible.append("design")
    if _has_any(norm, audit_phrases):
        signals.append(IntentSignal("intent_class", "audit", 1.2))
        possible.append("audit")
    if _has_any(norm, analyze_phrases):
        signals.append(IntentSignal("intent_class", "analyze", 1.0))
        possible.append("analyze")
    if _has_any(norm, refactor_phrases):
        signals.append(IntentSignal("intent_class", "refactor", 1.1))
        possible.append("refactor")
    if _has_any(norm, incident_phrases):
        signals.append(IntentSignal("intent_class", "investigate_incident", 1.3))
        possible.append("investigate_incident")
    if _has_any(norm, optimize_phrases):
        signals.append(IntentSignal("intent_class", "optimize", 1.0))
        possible.append("optimize")
    if _has_any(norm, migrate_phrases):
        signals.append(IntentSignal("intent_class", "migrate", 1.0))
        possible.append("migrate")

    # Domain signals
    domain_map = {
        "security": ("secur", "segura", "seguro", "seguridad", "vulnerab", "threat", "amenaza"),
        "testing": ("test", "testeable", "qa", "quality", "calidad"),
        "observability": ("observab", "metric", "métric", "monitor", "slo", "telemetry"),
        "architecture": ("architect", "arquitect"),
        "iot": ("iot", "domótic", "domotic", "sensor", "actuador", "device"),
        "networking": ("network", "red ", "wifi", "wi-fi", "connectivity", "conectividad"),
        "cloud": ("cloud", "remote", "remoto", "celular", "mobile", "móvil"),
        "electrical": ("electric", "eléctric", "iluminación", "lighting", "power"),
        "physical_access": ("access control", "acceso", "puerta", "lock", "cerradura", "gate"),
        "payments": ("payment", "pago", "billing", "stripe", "psp"),
        "database": ("database", "base de datos", "postgres", "sql"),
        "frontend": ("frontend", "ui", "móvil", "mobile app"),
        "backend": ("backend", "api"),
        "delivery": ("deploy", "desplieg", "ci/cd", "release", "producción"),
    }
    for domain, phrases in domain_map.items():
        if _has_any(norm, phrases):
            signals.append(IntentSignal("domain", domain, 1.0))

    # Constraints
    if _has_any(norm, ("sin depender del wi-fi", "without depending on", "no local wifi", "sin wifi local")):
        constraints.append("Must not depend solely on local Wi-Fi")
    if _has_any(norm, ("segura", "secure", "security")):
        constraints.append("Must be secure")
    if _has_any(norm, ("testeable", "testable", "tested")):
        constraints.append("Must be testable")
    if _has_any(norm, ("observable", "observab")):
        constraints.append("Must be observable")

    # Object of work hints for objective
    objective = utterance.strip()
    if _has_any(norm, ("reserv", "booking", "cancha")) and _has_any(norm, ("saas", "aplicación", "application", "sistema", "system", "constru")):
        facts.append(
            Fact(
                key="product_class",
                value="court_booking_saas",
                certainty="assumed",
                reason="utterance mentions booking/courts and build/SaaS language",
            )
        )
    if _has_any(norm, ("pádel", "padel")) and _has_any(norm, ("automat", "ilumin", "puerta", "acceso", "iot", "domót")):
        facts.append(
            Fact(
                key="product_class",
                value="padel_court_automation",
                certainty="assumed",
                reason="utterance mentions padel automation domains",
            )
        )

    # Uncertainties / required clarifications — never invent payments/PSP
    mentions_booking = _has_any(norm, ("reserv", "booking"))
    mentions_payments = _has_any(norm, domain_map["payments"])
    if mentions_booking and not mentions_payments:
        uncertainties.append(
            Fact(
                key="payments_required",
                value="unknown",
                certainty="unknown",
                reason="booking systems often involve payments, but utterance does not state it",
            )
        )
        clarifying.append("Do bookings require online payments? If yes, which constraints apply to the payment provider?")
        uncertainties.append(
            Fact(
                key="payment_provider",
                value="unknown",
                certainty="required" if "payments" in {s.value for s in signals if s.kind == "domain"} else "unknown",
                reason="must not invent a PSP such as Stripe",
            )
        )

    if any(f.key == "product_class" and f.value == "padel_court_automation" for f in facts):
        risks.extend(["physical_safety", "electrical_regulation", "physical_access_security"])
        clarifying.append(
            "Which physical works (electrical, locks) already have a licensed professional engaged?"
        )

    # Explicit risk signals
    if _has_any(norm, ("production", "producción", "prod ")):
        risks.append("production_impact")
    if _has_any(norm, ("electric", "eléctric", "ilumin")):
        risks.append("electrical_regulation")
    if _has_any(norm, ("puerta", "acceso físico", "physical access", "lock")):
        risks.append("physical_access_security")

    # Deduplicate possible intents preserving order
    seen: set[str] = set()
    possible_intents = []
    for item in possible:
        if item not in seen:
            seen.add(item)
            possible_intents.append(item)

    if not possible_intents:
        possible_intents = ["unspecified"]
        clarifying.append("What outcome should be true when this work succeeds?")

    return StructuredIntent(
        utterance=utterance.strip(),
        language=language,
        objective=objective,
        constraints=constraints,
        context=facts,
        uncertainties=uncertainties,
        signals=signals,
        possible_intents=possible_intents,
        clarifying_questions=clarifying,
        risk_signals=sorted(set(risks)),
    )
