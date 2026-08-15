"""Self-refutation attack tests for Phase 8 Skill layer."""

from __future__ import annotations

import unittest

from skillpacks.evidence import record_skill_evidence
from skillpacks.registry import load_registry
from skillpacks.routing import resolve_skills
from skillpacks.security import check_skill_security


class Phase8SelfRefutationTests(unittest.TestCase):
    def test_orchestrator_has_no_hardcoded_skill_list(self) -> None:
        from pathlib import Path

        facade = (Path(__file__).resolve().parents[2] / "orchestration" / "facade" / "__init__.py").read_text()
        self.assertNotIn("eos.skillpack.marketing.corey-haines", facade)
        self.assertNotIn("eos.skillpack.design.ui-ux-pro-max", facade)

    def test_skill_not_in_capability_namespace(self) -> None:
        for sid in load_registry().list_ids():
            self.assertTrue(sid.startswith("eos.skillpack."))
            self.assertFalse(sid.startswith("eos.capability."))

    def test_inject_commands_blocked(self) -> None:
        v = check_skill_security(
            {
                "workflows": [{"steps": ["!rm -rf /", "normal"]}],
            }
        )
        self.assertFalse(v.allowed)
        self.assertIn("inject_tool_commands", v.violations)

    def test_not_all_skills_selected_for_db_migration(self) -> None:
        result = resolve_skills(
            {
                "utterance": "Perform a database migration",
                "possible_intents": ["migrate"],
                "signals": [],
                "domains": [],
            },
            [],
            min_score=0.75,
        )
        self.assertNotIn("eos.skillpack.marketing.corey-haines", result.selected)
        self.assertNotIn("eos.skillpack.design.ui-ux-pro-max", result.selected)


if __name__ == "__main__":
    unittest.main()
