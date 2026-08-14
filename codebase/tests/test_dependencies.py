#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codebase.dependencies import build_dependency_graph
from codebase.fs_index import index_filesystem
from codebase.symbols import build_symbol_index


class DependencyGraphTests(unittest.TestCase):
    def test_import_and_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("import os\nfrom b import x\n", encoding="utf-8")
            (root / "b.py").write_text("x = 1\n", encoding="utf-8")
            (root / "package.json").write_text(
                '{"dependencies":{"express":"^4.0.0"}}', encoding="utf-8"
            )
            sym = build_symbol_index(root, index_filesystem(root))
            graph = build_dependency_graph(root, sym)
            kinds = {e.kind for e in graph.edges}
            self.assertIn("import", kinds)
            self.assertIn("package", kinds)
            self.assertTrue(any(e.target == "os" and e.external for e in graph.edges))
            self.assertTrue(any(p["name"] == "express" for p in graph.external_packages))
            self.assertFalse(any(e.kind == "inferred_runtime" for e in graph.edges))


if __name__ == "__main__":
    unittest.main()
