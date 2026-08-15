#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codebase.architecture import detect_architecture_signals
from codebase.dependencies import build_dependency_graph
from codebase.fs_index import index_filesystem
from codebase.symbols import build_symbol_index


class ArchitectureSignalTests(unittest.TestCase):
    def test_layer_and_entry_inferred(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "services").mkdir()
            (root / "services" / "booking.py").write_text("def run():\n    pass\n", encoding="utf-8")
            (root / "main.py").write_text("print('x')\n", encoding="utf-8")
            fs = index_filesystem(root)
            sym = build_symbol_index(root, fs)
            deps = build_dependency_graph(root, sym)
            signals = detect_architecture_signals(fs, sym, deps)
            kinds = {s.kind for s in signals}
            self.assertIn("layer_directory", kinds)
            self.assertIn("entry_point", kinds)
            self.assertTrue(all(s.certainty in {"observed", "inferred", "unknown"} for s in signals))


if __name__ == "__main__":
    unittest.main()
