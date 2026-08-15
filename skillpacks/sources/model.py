"""Skill Source model — distinct from SkillPack, Knowledge Unit, and Evidence.

SOURCE ≠ SKILLPACK ≠ KNOWLEDGE ≠ EVIDENCE
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

SourceStatus = Literal[
    "discovered",
    "verified",
    "ingested",
    "normalized",
    "active",
    "unavailable",
    "rejected",
    "stale",
]

SourceType = Literal[
    "file",
    "directory",
    "url",
    "eos_native",
    "fixture",
    "unavailable_placeholder",
]

TrustLevel = Literal[
    "untrusted",
    "verified_primary",
    "verified_official",
    "validated_internal",
    "experimental_inference",
]

SOURCE_ID_PREFIX = "eos.skillsource."


def is_source_id(value: str) -> bool:
    if not value.startswith(SOURCE_ID_PREFIX):
        return False
    rest = value[len(SOURCE_ID_PREFIX) :]
    parts = rest.split(".")
    if len(parts) < 2:
        return False
    return all(p and p[0].islower() and all(c.isalnum() or c == "-" for c in p) for p in parts)


def content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class SkillSource:
    """First-class source that may underpin one or more SkillPacks."""

    source_id: str
    skillpack_id: str
    source_type: SourceType
    title: str
    origin: str
    locator: str
    version: str
    content_hash: str | None = None
    retrieved_at: float | None = None
    license: str = "unknown"
    trust_level: TrustLevel = "untrusted"
    extraction_method: str = "none"
    status: SourceStatus = "discovered"
    allowed_usage: list[str] = field(default_factory=lambda: ["methodology_reference"])
    notes: list[str] = field(default_factory=list)
    revision: int = 1
    parent_source_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate_shape(self) -> list[str]:
        errors: list[str] = []
        if not is_source_id(self.source_id):
            errors.append(f"invalid source_id: {self.source_id}")
        if not self.skillpack_id.startswith("eos.skillpack."):
            errors.append(f"invalid skillpack_id: {self.skillpack_id}")
        if not self.title.strip():
            errors.append("title required")
        if not self.origin.strip():
            errors.append("origin / provenance required")
        if not self.locator.strip():
            errors.append("locator required")
        if not self.version.strip():
            errors.append("version required")
        valid_status = {
            "discovered",
            "verified",
            "ingested",
            "normalized",
            "active",
            "unavailable",
            "rejected",
            "stale",
        }
        if self.status not in valid_status:
            errors.append(f"invalid status: {self.status}")
        if self.status in {"ingested", "normalized", "active"} and not self.content_hash:
            errors.append("content_hash required for ingested/normalized/active sources")
        if self.status == "active" and self.trust_level == "untrusted":
            errors.append("active source cannot remain untrusted")
        if self.source_type == "unavailable_placeholder" and self.status not in {
            "unavailable",
            "discovered",
            "rejected",
        }:
            errors.append("unavailable_placeholder cannot be active/normalized")
        for key in ("grants_permissions", "grants_tools", "bypass_gates", "auto_approve"):
            if key in self.metadata:
                errors.append(f"forbidden privilege field: {key}")
        return errors


def source_from_dict(data: dict[str, Any]) -> SkillSource:
    return SkillSource(
        source_id=str(data["source_id"]),
        skillpack_id=str(data["skillpack_id"]),
        source_type=str(data.get("source_type", "file")),  # type: ignore[arg-type]
        title=str(data.get("title", "")),
        origin=str(data.get("origin", "")),
        locator=str(data.get("locator", "")),
        version=str(data.get("version", "")),
        content_hash=data.get("content_hash"),
        retrieved_at=data.get("retrieved_at", time.time()),
        license=str(data.get("license", "unknown")),
        trust_level=str(data.get("trust_level", "untrusted")),  # type: ignore[arg-type]
        extraction_method=str(data.get("extraction_method", "none")),
        status=str(data.get("status", "discovered")),  # type: ignore[arg-type]
        allowed_usage=list(data.get("allowed_usage") or ["methodology_reference"]),
        notes=list(data.get("notes") or []),
        revision=int(data.get("revision", 1)),
        parent_source_id=data.get("parent_source_id"),
        metadata=dict(data.get("metadata") or {}),
    )
