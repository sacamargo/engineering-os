#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codebase.architecture import detect_architecture_signals
from codebase.config_intel import analyze_configuration
from codebase.dependencies import build_dependency_graph
from codebase.findings import build_findings
from codebase.fs_index import index_filesystem
from codebase.symbols import build_symbol_index
from codebase.tests_intel import analyze_tests


class FindingsTests(unittest.TestCase):
    def test_findings_require_evidence_and_epistemic_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text("def main():\n    return 1\n", encoding="utf-8")
            (root / ".env").write_text("SECRET=x\n", encoding="utf-8")
            fs = index_filesystem(root)
            sym = build_symbol_index(root, fs)
            deps = build_dependency_graph(root, sym)
            tests = analyze_tests(root, fs)
            configs = analyze_configuration(root, fs)
            signals = detect_architecture_signals(fs, sym, deps)
            findings = build_findings(fs, sym, deps, tests, configs, signals)
            self.assertTrue(any(f.kind == "sensitive_path" for f in findings))
            self.assertTrue(any(f.kind == "missing_tests" for f in findings))
            for f in findings:
                self.assertTrue(f.evidence, msg=f.id)
                self.assertIn(f.confidence, {"observed", "inferred", "unknown"})
                self.assertNotEqual(f.status, "decision")


if __name__ == "__main__":
    unittest.main()
