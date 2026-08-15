#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codebase.architecture import detect_architecture_signals
from codebase.config_intel import analyze_configuration
from codebase.dependencies import build_dependency_graph
from codebase.evidence import collect_evidence
from codebase.findings import build_findings
from codebase.fs_index import index_filesystem
from codebase.impact import analyze_module_impact
from codebase.snapshot import CodebaseSnapshot, SnapshotMeta, new_snapshot_id, utc_now_iso
from codebase.symbols import build_symbol_index
from codebase.tests_intel import analyze_tests


class EvidenceImpactTests(unittest.TestCase):
    def test_evidence_and_impact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("import b\n\ndef fa():\n    pass\n", encoding="utf-8")
            (root / "b.py").write_text("def fb():\n    pass\n", encoding="utf-8")
            (root / "test_b.py").write_text("import b\n", encoding="utf-8")
            fs = index_filesystem(root)
            sym = build_symbol_index(root, fs)
            deps = build_dependency_graph(root, sym)
            tests = analyze_tests(root, fs)
            configs = analyze_configuration(root, fs)
            signals = detect_architecture_signals(fs, sym, deps)
            findings = build_findings(fs, sym, deps, tests, configs, signals)
            snap = CodebaseSnapshot(
                id=new_snapshot_id(str(root), None),
                meta=SnapshotMeta(
                    analyzed_at=utc_now_iso(),
                    git_revision=None,
                    git_branch=None,
                    root=str(root),
                    included_file_count=len(fs.files),
                ),
                findings=[f.to_dict() for f in findings],
            )
            evidence = collect_evidence(snap, findings)
            self.assertTrue(evidence)
            self.assertTrue(all(e.pointer for e in evidence))
            impact = analyze_module_impact(
                "b.py",
                deps,
                tests,
                configs,
                signals,
                module_paths={m.path for m in sym.modules},
            )
            self.assertIn("a.py", impact.direct_dependents)
            self.assertEqual(impact.certainty_notes["direct_dependents"], "observed")
            self.assertEqual(impact.certainty_notes["indirect_dependents"], "inferred")


if __name__ == "__main__":
    unittest.main()
