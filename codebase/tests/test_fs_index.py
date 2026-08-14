#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codebase.fs_index import index_filesystem


class FsIndexTests(unittest.TestCase):
    def test_indexes_and_blocks_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text("print('hi')\n", encoding="utf-8")
            (root / ".env").write_text("SECRET=1\n", encoding="utf-8")
            (root / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
            (root / "ignored.txt").write_text("x\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "x.js").write_text("1\n", encoding="utf-8")

            idx = index_filesystem(root)
            paths = {f.path for f in idx.files}
            self.assertIn("app.py", paths)
            self.assertIn(".env", paths)
            env = next(f for f in idx.files if f.path == ".env")
            self.assertTrue(env.sensitive)
            self.assertFalse(env.content_readable)
            self.assertNotIn("ignored.txt", paths)
            self.assertTrue(all(not p.startswith("node_modules") for p in paths))


if __name__ == "__main__":
    unittest.main()
