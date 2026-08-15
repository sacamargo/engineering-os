"""Source ingestion pipeline with stage evidence.

discover → verify → ingest → normalize → provenance → validate → activate
Invalid sources never reach active.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from skillpacks.sources.model import SkillSource, content_hash, source_from_dict
from skillpacks.sources.revision import append_revision, load_revisions
from skillpacks.sources.extraction import extract_knowledge
from skillpacks.sources.activation import can_activate_skill
from skillpacks.sources.status import can_transition_skillpack_status

STAGES = (
    "discover",
    "verify",
    "ingest",
    "normalize",
    "provenance",
    "validate",
    "activate",
)


@dataclass
class StageEvidence:
    stage: str
    status: str  # passed | failed | skipped | blocked
    message: str
    timestamp: float = field(default_factory=time.time)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PipelineResult:
    source: SkillSource
    stages: list[StageEvidence]
    extraction: dict[str, Any] | None = None
    activation: dict[str, Any] | None = None
    stopped_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.to_dict(),
            "stages": [s.to_dict() for s in self.stages],
            "extraction": self.extraction,
            "activation": self.activation,
            "stopped_at": self.stopped_at,
        }


def _read_bytes(locator: str, repo_root: Path) -> bytes | None:
    if locator in {"NEEDS_SOURCE", "unavailable"}:
        return None
    path = Path(locator)
    if not path.is_absolute():
        path = repo_root / locator
    if path.is_file():
        return path.read_bytes()
    return None


def run_ingestion_pipeline(
    source: SkillSource,
    *,
    repo_root: Path,
    stop_after: str | None = None,
    revisions_dir: Path | None = None,
) -> PipelineResult:
    """Run pipeline stages; stop_after allows early exit. Invalid never becomes active."""
    stages: list[StageEvidence] = []
    result = PipelineResult(source=source, stages=stages)
    rev_dir = revisions_dir or (repo_root / "skillpacks" / "sources" / "revisions")

    # discover
    stages.append(
        StageEvidence("discover", "passed", f"discovered {source.source_id}", details={"status": source.status})
    )
    if stop_after == "discover":
        result.stopped_at = "discover"
        return result

    # verify
    if source.source_type == "unavailable_placeholder" or source.locator == "NEEDS_SOURCE":
        stages.append(
            StageEvidence(
                "verify",
                "blocked",
                "NEEDS_SOURCE — no verifiable material",
                details={"action": "NEEDS_SOURCE"},
            )
        )
        source.status = "unavailable"
        result.stopped_at = "verify"
        return result
    shape_errs = source.validate_shape()
    # discovered sources may lack hash — OK before ingest
    shape_errs = [e for e in shape_errs if "content_hash" not in e]
    if shape_errs:
        stages.append(StageEvidence("verify", "failed", "; ".join(shape_errs)))
        source.status = "rejected"
        result.stopped_at = "verify"
        return result
    source.status = "verified"
    stages.append(StageEvidence("verify", "passed", "source metadata verified"))
    if stop_after == "verify":
        result.stopped_at = "verify"
        return result

    # ingest
    raw = _read_bytes(source.locator, repo_root)
    if raw is None:
        stages.append(StageEvidence("ingest", "failed", f"cannot read locator {source.locator}"))
        source.status = "rejected"
        result.stopped_at = "ingest"
        return result
    digest = content_hash(raw)
    # Immutability: if hash differs from prior revision, create new revision
    prior = load_revisions(rev_dir, source.source_id)
    if prior and prior[-1].get("content_hash") and prior[-1]["content_hash"] != digest:
        source = append_revision(source, digest, rev_dir)
        stages.append(
            StageEvidence(
                "ingest",
                "passed",
                "content changed — new revision created (no silent overwrite)",
                details={"content_hash": digest, "revision": source.revision},
            )
        )
    else:
        source.content_hash = digest
        source.retrieved_at = time.time()
        source.status = "ingested"
        append_revision(source, digest, rev_dir, create_new=False)
        stages.append(
            StageEvidence("ingest", "passed", "content ingested", details={"content_hash": digest})
        )
    if stop_after == "ingest":
        result.stopped_at = "ingest"
        return result

    # normalize / extract
    extraction = extract_knowledge(source, raw)
    result.extraction = extraction
    if not extraction.get("ok"):
        stages.append(StageEvidence("normalize", "failed", extraction.get("error", "extract failed")))
        result.stopped_at = "normalize"
        return result
    source.status = "normalized"
    source.extraction_method = str(extraction.get("method", source.extraction_method))
    stages.append(StageEvidence("normalize", "passed", "knowledge extracted with source refs"))
    if stop_after == "normalize":
        result.stopped_at = "normalize"
        return result

    # provenance
    if not source.origin or not source.content_hash:
        stages.append(StageEvidence("provenance", "failed", "incomplete provenance"))
        result.stopped_at = "provenance"
        return result
    stages.append(
        StageEvidence(
            "provenance",
            "passed",
            "provenance chain Source→Extraction recorded",
            details={"origin": source.origin, "hash": source.content_hash},
        )
    )
    if stop_after == "provenance":
        result.stopped_at = "provenance"
        return result

    # validate (contracts shape)
    v_errs = source.validate_shape()
    if v_errs:
        stages.append(StageEvidence("validate", "failed", "; ".join(v_errs)))
        result.stopped_at = "validate"
        return result
    stages.append(StageEvidence("validate", "passed", "source contracts OK"))
    if stop_after == "validate":
        result.stopped_at = "validate"
        return result

    # activate (source-level active ≠ skillpack active — gate decides)
    gate = can_activate_skill(source, extraction)
    result.activation = gate
    if not gate.get("allowed"):
        stages.append(StageEvidence("activate", "blocked", gate.get("reason", "activation denied")))
        # keep normalized; do not force source.active if gate fails
        result.stopped_at = "activate"
        return result
    source.status = "active"
    if source.trust_level == "untrusted":
        source.trust_level = "validated_internal"
    stages.append(StageEvidence("activate", "passed", "CAN_ACTIVATE_SKILL passed for source"))
    return result
