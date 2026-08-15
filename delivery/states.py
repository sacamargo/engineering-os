"""Delivery state machine — strict transitions."""

from __future__ import annotations

from typing import Final

DELIVERY_STATES: Final[frozenset[str]] = frozenset(
    {
        "draft",
        "building",
        "validating",
        "ready",
        "blocked",
        "needs_human",
        "released",
        "failed",
        "cancelled",
    }
)

ALLOWED: Final[dict[str, frozenset[str]]] = {
    "draft": frozenset({"building", "cancelled", "blocked"}),
    "building": frozenset({"validating", "failed", "cancelled", "blocked"}),
    "validating": frozenset({"ready", "failed", "blocked", "needs_human", "cancelled"}),
    "ready": frozenset({"released", "needs_human", "blocked", "cancelled"}),
    "blocked": frozenset({"draft", "building", "cancelled", "failed"}),
    "needs_human": frozenset({"ready", "blocked", "cancelled", "failed"}),
    "released": frozenset(),
    "failed": frozenset({"draft", "cancelled"}),
    "cancelled": frozenset(),
}


class InvalidDeliveryTransition(ValueError):
    pass


def can_transition(frm: str, to: str) -> bool:
    return to in ALLOWED.get(frm, frozenset())


def transition(frm: str, to: str, *, reason: str = "") -> str:
    # Explicit prohibitions called out in Phase 7 spec
    if frm == "failed" and to == "released":
        raise InvalidDeliveryTransition("failed → released forbidden")
    if frm == "validating" and to == "released":
        raise InvalidDeliveryTransition("validating → released forbidden without gates")
    if frm == "needs_human" and to == "released":
        raise InvalidDeliveryTransition("needs_human → released forbidden without approval path via ready")
    if not can_transition(frm, to):
        raise InvalidDeliveryTransition(f"invalid delivery transition {frm!r} → {to!r} ({reason})")
    return to
