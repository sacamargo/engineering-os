#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codebase.config_intel import analyze_configuration
from codebase.fs_index import index_filesystem


class ConfigIntelTests(unittest.TestCase):
    def test_detects_manifests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text("{}", encoding="utf-8")
            (root / "Dockerfile").write_text("FROM alpine\n", encoding="utf-8")
            (root / ".env.example").write_text("A=1\n", encoding="utf-8")
            cfg = analyze_configuration(root, index_filesystem(root))
            types = {c.config_type for c in cfg.configurations}
            self.assertIn("npm_manifest", types)
            self.assertIn("docker", types)
            self.assertIn("env_template", types)
            self.assertTrue(all(c.detection in {"detected", "inferred"} for c in cfg.configurations))


if __name__ == "__main__":
    unittest.main()
