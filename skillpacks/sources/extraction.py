"""Raw Source → Extracted Knowledge → SkillPack boundary.

SkillPack does not embed entire raw documents; extractions keep source refs.
"""

from __future__ import annotations

from typing import Any

from skillpacks.sources.model import SkillSource, content_hash


def extract_knowledge(source: SkillSource, raw: bytes) -> dict[str, Any]:
    """Extract structured slices without dumping the full document into SkillPack."""
    text = raw.decode("utf-8", errors="replace")
    # Security: reject obvious injection/privilege payloads in sources
    lowered = text.lower()
    for bad in ("grants_permissions", "bypass_gates", "auto_approve", "rm -rf /", "<|tool"):
        if bad in lowered:
            return {
                "ok": False,
                "error": f"malicious_or_forbidden_source_content:{bad}",
                "source_id": source.source_id,
            }
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    principles = [ln for ln in lines if ln.lower().startswith(("principle", "- principle", "* principle"))][:20]
    constraints = [ln for ln in lines if "must not" in ln.lower() or "cannot" in ln.lower()][:20]
    # Bounded extraction — never return full raw as primary payload
    return {
        "ok": True,
        "method": source.extraction_method or "text_slice",
        "source_id": source.source_id,
        "source_hash": content_hash(raw),
        "principles": principles,
        "methods": [],
        "heuristics": [],
        "constraints": constraints,
        "anti_patterns": [],
        "examples": [],
        "triggers": [],
        "negative_triggers": [],
        "composition_rules": [],
        "raw_bytes": len(raw),
        "raw_included": False,
        "notes": ["Extraction keeps source reference; full document not embedded"],
    }
