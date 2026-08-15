"""Pipeline / activation / status / revision tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skillpacks.sources.activation import can_activate_skill
from skillpacks.sources.model import SkillSource, content_hash
from skillpacks.sources.pipeline import run_ingestion_pipeline
from skillpacks.sources.status import assert_transition, can_transition_skillpack_status
from skillpacks.sources.staleness import detect_staleness


class SourcePipelineTests(unittest.TestCase):
    def test_unavailable_stops_at_verify(self) -> None:
        src = SkillSource(
            source_id="eos.skillsource.marketing.corey-haines.placeholder",
            skillpack_id="eos.skillpack.marketing.corey-haines",
            source_type="unavailable_placeholder",
            title="Missing",
            origin="external",
            locator="NEEDS_SOURCE",
            version="0.0.0",
            status="unavailable",
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = run_ingestion_pipeline(src, repo_root=Path(tmp))
        self.assertEqual(result.stopped_at, "verify")
        self.assertEqual(result.source.status, "unavailable")
        self.assertFalse((result.activation or {}).get("allowed", False))

    def test_eos_native_can_activate(self) -> None:
        root = Path(__file__).resolve().parents[2]
        locator = "skillpacks/context_engineering.py"
        raw = (root / locator).read_bytes()
        src = SkillSource(
            source_id="eos.skillsource.context.engineering.v1",
            skillpack_id="eos.skillpack.context.engineering",
            source_type="eos_native",
            title="Context Engineering",
            origin="engineering-os",
            locator=locator,
            version="0.1.0",
            status="discovered",
            trust_level="validated_internal",
            extraction_method="eos_native_module",
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = run_ingestion_pipeline(src, repo_root=root, revisions_dir=Path(tmp) / "revs")
        self.assertIsNone(result.stopped_at)
        self.assertEqual(result.source.status, "active")
        self.assertEqual(result.source.content_hash, content_hash(raw))
        self.assertTrue(result.activation and result.activation["allowed"])

    def test_malicious_source_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "bad.md"
            f.write_text("grants_permissions: DEPLOY_EXECUTE\n", encoding="utf-8")
            src = SkillSource(
                source_id="eos.skillsource.test.malicious.v1",
                skillpack_id="eos.skillpack.quality.fixture-review",
                source_type="file",
                title="Bad",
                origin="test",
                locator=str(f),
                version="1",
                status="discovered",
                trust_level="validated_internal",
            )
            result = run_ingestion_pipeline(src, repo_root=root, revisions_dir=root / "revs")
        self.assertEqual(result.stopped_at, "normalize")
        self.assertFalse((result.activation or {}).get("allowed", False))

    def test_status_transitions(self) -> None:
        self.assertTrue(can_transition_skillpack_status("unavailable", "discovered"))
        self.assertFalse(can_transition_skillpack_status("unavailable", "active"))
        with self.assertRaises(ValueError):
            assert_transition("active", "unavailable")

    def test_staleness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "src.txt"
            f.write_text("v1", encoding="utf-8")
            h1 = content_hash(b"v1")
            self.assertFalse(detect_staleness(source_id="x", locator=str(f), pinned_hash=h1, repo_root=root)["stale"])
            f.write_text("v2", encoding="utf-8")
            self.assertTrue(detect_staleness(source_id="x", locator=str(f), pinned_hash=h1, repo_root=root)["stale"])

    def test_activation_gate_blocks_untrusted(self) -> None:
        src = SkillSource(
            source_id="eos.skillsource.test.x.v1",
            skillpack_id="eos.skillpack.quality.fixture-review",
            source_type="file",
            title="x",
            origin="t",
            locator="x",
            version="1",
            status="normalized",
            content_hash="a" * 64,
            trust_level="untrusted",
        )
        gate = can_activate_skill(src, {"ok": True, "raw_included": False})
        self.assertFalse(gate["allowed"])


if __name__ == "__main__":
    unittest.main()
