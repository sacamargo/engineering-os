"""Marketing skillpack integration tests."""

from __future__ import annotations

import unittest

from skillpacks.registry import load_registry
from skillpacks.routing import resolve_skills


class MarketingSkillTests(unittest.TestCase):
    def test_registered_unavailable(self) -> None:
        reg = load_registry()
        pack = reg.get("eos.skillpack.marketing.corey-haines")
        assert pack is not None
        self.assertEqual(pack.status, "unavailable")
        self.assertFalse(pack.is_selectable())
        self.assertTrue(pack.provenance.unavailable_source_content)

    def test_landing_conversion_candidate_but_unavailable(self) -> None:
        intent = {
            "utterance": "Improve landing page conversion and product positioning",
            "possible_intents": ["design"],
            "signals": [],
            "domains": [],
        }
        result = resolve_skills(intent, ["eos.capability.design.system-architecture"], min_score=0.5)
        self.assertIn("eos.skillpack.marketing.corey-haines", result.unavailable)
        self.assertNotIn("eos.skillpack.marketing.corey-haines", result.selected)

    def test_database_migration_not_marketing(self) -> None:
        intent = {
            "utterance": "Perform a database migration for booking schema",
            "possible_intents": ["migrate"],
            "signals": [],
            "domains": [],
        }
        result = resolve_skills(intent, [], min_score=0.5)
        self.assertNotIn("eos.skillpack.marketing.corey-haines", result.selected)

    def test_no_deploy_permissions_in_manifest(self) -> None:
        pack = load_registry().get("eos.skillpack.marketing.corey-haines")
        assert pack is not None
        self.assertTrue(pack.cannot_grant_permissions)
        self.assertIn("cannot_deploy", pack.constraints)


if __name__ == "__main__":
    unittest.main()
