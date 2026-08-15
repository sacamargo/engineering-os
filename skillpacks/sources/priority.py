"""Source trust priority — explicit and auditable."""

from __future__ import annotations

PRIORITY_ORDER = [
    "verified_primary",
    "verified_official",
    "validated_internal",
    "experimental_inference",
    "untrusted",
]


def trust_rank(level: str) -> int:
    try:
        return PRIORITY_ORDER.index(level)
    except ValueError:
        return len(PRIORITY_ORDER)


def preferred_source(sources: list) -> object | None:
    if not sources:
        return None
    return sorted(sources, key=lambda s: (trust_rank(getattr(s, "trust_level", "untrusted")), -getattr(s, "revision", 1)))[0]
