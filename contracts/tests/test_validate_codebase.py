#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from codebase.analyze import analyze_repository
from codebase.report import bundle_to_machine_json
from contracts.validate_codebase import validate_analysis_payload, validate_snapshot


class CodebaseContractTests(unittest.TestCase):
    def test_live_analysis_satisfies_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
            payload = bundle_to_machine_json(analyze_repository(root))
            findings = validate_analysis_payload(payload)
            self.assertEqual(findings, [], msg=[f.format() for f in findings])

    def test_finding_without_evidence_fails(self) -> None:
        snap = {
            "id": "eos.snapshot.abc123def456",
            "meta": {"root": "/x", "analyzed_at": "t"},
            "findings": [
                {"id": "eos.finding.dead_module.1", "confidence": "inferred", "evidence": []}
            ],
        }
        findings = validate_snapshot(snap)
        self.assertTrue(any(f.code == "missing_evidence" for f in findings))


if __name__ == "__main__":
    unittest.main()
