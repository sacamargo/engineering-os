#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from codebase.analyze import analyze_repository
from codebase.cli import main
from codebase.incremental import diff_snapshots
from codebase.report import bundle_to_machine_json, render_human_report


class AnalyzePipelineTests(unittest.TestCase):
    def test_analyze_produces_snapshot_report_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "services").mkdir()
            (root / "services" / "app.py").write_text(
                "def create_booking():\n    return 1\n",
                encoding="utf-8",
            )
            (root / "main.py").write_text("from services import app\n", encoding="utf-8")
            (root / "requirements.txt").write_text("flask==2.0.0\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_app.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
            bundle = analyze_repository(root)
            snap = bundle.snapshot
            self.assertTrue(snap.id.startswith("eos.snapshot."))
            self.assertGreater(len(snap.files), 0)
            self.assertTrue(any(m.get("path") == "main.py" for m in snap.modules))
            self.assertTrue(snap.evidence)
            self.assertIn("Runtime behavior is unknown", " ".join(snap.unknowns))
            self.assertIn("duration_seconds", snap.metrics)
            report = render_human_report(bundle)
            self.assertIn("Repository summary", report)
            self.assertIn("Unknowns", report)
            payload = bundle_to_machine_json(bundle)
            self.assertEqual(payload["schema"], "eos.codebase.analysis.v1")
            # second run comparable fingerprint structure
            bundle2 = analyze_repository(root)
            diff = diff_snapshots(bundle.snapshot, bundle2.snapshot)
            self.assertEqual(diff.files_added, [])
            self.assertEqual(diff.files_removed, [])

    def test_cli_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "x.py").write_text("x = 1\n", encoding="utf-8")
            out = Path(tmp) / "out.json"
            code = main(["analyze", str(root), "--format", "json", "--out", str(out)])
            self.assertEqual(code, 0)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertIn("snapshot", data)


if __name__ == "__main__":
    unittest.main()
