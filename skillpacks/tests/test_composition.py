"""Composition tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skillpacks.composition import compose_skills
from skillpacks.registry import load_registry


class SkillCompositionTests(unittest.TestCase):
    def test_design_plus_quality_not_dag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packs = [
                {
                    "id": "eos.skillpack.design.ui-ux-pro-max",
                    "name": "UI",
                    "version": "1.0.0",
                    "purpose": "UX",
                    "category": "design",
                    "source": "t",
                    "status": "experimental",
                    "provenance": {
                        "origin": "t",
                        "source": "t",
                        "version": "1.0.0",
                        "unavailable_source_content": False,
                        "adaptation_status": "eos-native",
                    },
                    "composition_rules": [
                        {
                            "kind": "primary",
                            "with_skill_ids": ["eos.skillpack.quality.stop-slop"],
                            "implies_task_dependency": False,
                        }
                    ],
                },
                {
                    "id": "eos.skillpack.quality.stop-slop",
                    "name": "Stop Slop",
                    "version": "1.0.0",
                    "purpose": "Review",
                    "category": "quality",
                    "source": "t",
                    "status": "experimental",
                    "provenance": {
                        "origin": "t",
                        "source": "t",
                        "version": "1.0.0",
                        "unavailable_source_content": False,
                        "adaptation_status": "eos-native",
                    },
                    "composition_rules": [
                        {
                            "kind": "transversal",
                            "with_skill_ids": ["eos.skillpack.design.ui-ux-pro-max"],
                            "implies_task_dependency": False,
                        }
                    ],
                },
            ]
            skills = []
            for p in packs:
                folder = p["id"].split(".")[-1]
                d = root / "packs" / folder
                d.mkdir(parents=True)
                (d / "manifest.json").write_text(json.dumps(p), encoding="utf-8")
                skills.append({"id": p["id"], "status": "experimental"})
            (root / "registry.json").write_text(json.dumps({"skills": skills}), encoding="utf-8")
            reg = load_registry(root)
            composed = compose_skills(
                ["eos.skillpack.design.ui-ux-pro-max", "eos.skillpack.quality.stop-slop"],
                reg,
            )
            self.assertIn("eos.skillpack.design.ui-ux-pro-max", composed.primary)
            self.assertIn("eos.skillpack.quality.stop-slop", composed.transversal)
            self.assertFalse(composed.errors)
            self.assertTrue(any("pipeline" in n.lower() or "dag" not in n.lower() for n in composed.notes))

    def test_implies_task_dependency_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = {
                "id": "eos.skillpack.test.bad-compose",
                "name": "Bad",
                "version": "1.0.0",
                "purpose": "x",
                "category": "test",
                "source": "t",
                "status": "experimental",
                "provenance": {
                    "origin": "t",
                    "source": "t",
                    "version": "1.0.0",
                    "unavailable_source_content": False,
                    "adaptation_status": "eos-native",
                },
                "composition_rules": [
                    {
                        "kind": "supporting",
                        "with_skill_ids": [],
                        "implies_task_dependency": True,
                    }
                ],
            }
            d = root / "packs" / "bad-compose"
            d.mkdir(parents=True)
            (d / "manifest.json").write_text(json.dumps(p), encoding="utf-8")
            (root / "registry.json").write_text(
                json.dumps({"skills": [{"id": p["id"], "status": "experimental"}]}),
                encoding="utf-8",
            )
            reg = load_registry(root)
            composed = compose_skills([p["id"]], reg)
            self.assertTrue(any("task dependency" in e for e in composed.errors))


if __name__ == "__main__":
    unittest.main()
