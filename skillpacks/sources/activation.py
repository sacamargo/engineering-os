"""CAN_ACTIVATE_SKILL gate — SkillPack becomes active only with verified source evidence."""

from __future__ import annotations

from typing import Any

from skillpacks.sources.model import SkillSource


def can_activate_skill(source: SkillSource, extraction: dict[str, Any] | None = None) -> dict[str, Any]:
    reasons: list[str] = []
    if source.source_type == "unavailable_placeholder":
        reasons.append("placeholder source")
    if source.locator in {"NEEDS_SOURCE", "unavailable"}:
        reasons.append("NEEDS_SOURCE")
    if not source.content_hash:
        reasons.append("missing content_hash")
    if not source.origin:
        reasons.append("missing provenance origin")
    if source.status not in {"normalized", "ingested", "active", "verified"}:
        # verified alone insufficient without ingest
        if source.status not in {"normalized", "active"}:
            reasons.append(f"source status {source.status} insufficient")
    if source.trust_level == "untrusted":
        reasons.append("untrusted trust_level")
    if extraction is not None and not extraction.get("ok"):
        reasons.append("extraction invalid")
    if extraction is not None and extraction.get("raw_included"):
        reasons.append("raw dump not allowed in extraction")
    # Critical conflicts flag
    if (source.metadata or {}).get("critical_conflict"):
        reasons.append("critical conflict unresolved")
    allowed = not reasons and source.status in {"normalized", "active"} and bool(source.content_hash)
    # For freshly normalized in pipeline, status is normalized
    if source.status == "normalized" and source.content_hash and source.trust_level != "untrusted":
        if extraction is None or extraction.get("ok"):
            allowed = not any(
                r in reasons
                for r in (
                    "placeholder source",
                    "NEEDS_SOURCE",
                    "missing content_hash",
                    "missing provenance origin",
                    "extraction invalid",
                    "raw dump not allowed in extraction",
                    "critical conflict unresolved",
                    "untrusted trust_level",
                )
            )
            reasons = [r for r in reasons if r not in {"source status normalized insufficient"}]
    return {
        "gate": "CAN_ACTIVATE_SKILL",
        "allowed": allowed,
        "reason": "OK" if allowed else "; ".join(reasons) or "denied",
        "source_id": source.source_id,
        "skillpack_id": source.skillpack_id,
    }
