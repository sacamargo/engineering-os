"""Registry discovery tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skillpacks.registry import discover_skills, load_registry


class SkillRegistryTests(unittest.TestCase):
    def test_load_default_registry(self) -> None:
        reg = load_registry()
        self.assertIn("eos.skillpack.quality.fixture-review", reg.list_ids())
        pack = reg.get("eos.skillpack.quality.fixture-review")
        assert pack is not None
        self.assertEqual(pack.status, "experimental")
        self.assertTrue(pack.is_selectable())

    def test_discover_api(self) -> None:
        entries = discover_skills()
        ids = {e["id"] for e in entries}
        self.assertIn("eos.skillpack.quality.fixture-review", ids)

    def test_new_pack_without_core_code_change(self) -> None:
        """Skill #N registers via data only (scalability invariant)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packs = root / "packs" / "extra-skill"
            packs.mkdir(parents=True)
            manifest = {
                "id": "eos.skillpack.test.extra-skill",
                "name": "Extra",
                "version": "1.0.0",
                "purpose": "Scalability fixture",
                "category": "test",
                "source": "tmp",
                "status": "experimental",
                "provenance": {
                    "origin": "test",
                    "source": "tmp",
                    "version": "1.0.0",
                    "unavailable_source_content": False,
                    "adaptation_status": "eos-native",
                },
            }
            (packs / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / "registry.json").write_text(
                json.dumps(
                    {
                        "schema": "eos.skillpack.registry.v1",
                        "skills": [
                            {
                                "id": "eos.skillpack.test.extra-skill",
                                "status": "experimental",
                                "path": "packs/extra-skill/manifest.json",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            reg = load_registry(root)
            self.assertIn("eos.skillpack.test.extra-skill", reg.list_ids())
            # No orchestration module imported or modified


if __name__ == "__main__":
    unittest.main()
