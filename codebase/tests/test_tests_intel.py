#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codebase.fs_index import index_filesystem
from codebase.tests_intel import analyze_tests


class TestIntelTests(unittest.TestCase):
    def test_detects_tests_unknown_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text("def f():\n    return 1\n", encoding="utf-8")
            (root / "test_app.py").write_text("def test_f():\n    assert True\n", encoding="utf-8")
            intel = analyze_tests(root, index_filesystem(root))
            self.assertEqual(len(intel.tests), 1)
            self.assertEqual(intel.tests[0].coverage, "unknown")
            self.assertNotEqual(intel.tests[0].coverage, 0)


if __name__ == "__main__":
    unittest.main()
