#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codebase.fs_index import index_filesystem
from codebase.symbols import build_symbol_index


class SymbolIndexTests(unittest.TestCase):
    def test_python_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "mod.py").write_text(
                "def create_booking():\n    return 1\n\nclass Service:\n    pass\n",
                encoding="utf-8",
            )
            idx = build_symbol_index(root, index_filesystem(root))
            names = {s.name for s in idx.symbols}
            self.assertIn("create_booking", names)
            self.assertIn("Service", names)
            self.assertTrue(all(s.id.startswith("eos.symbol.") for s in idx.symbols))
            self.assertTrue(idx.modules)


if __name__ == "__main__":
    unittest.main()
