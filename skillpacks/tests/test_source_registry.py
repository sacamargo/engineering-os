"""Source registry tests."""

from __future__ import annotations

import unittest

from skillpacks.sources.registry import load_source_registry


class SourceRegistryTests(unittest.TestCase):
    def test_sources_for_skill(self) -> None:
        reg = load_source_registry()
        mkt = reg.sources_for_skill("eos.skillpack.marketing.corey-haines")
        self.assertTrue(mkt)
        self.assertEqual(mkt[0].status, "unavailable")
        self.assertIn("NEEDS_SOURCE", mkt[0].notes)

    def test_skills_for_source(self) -> None:
        reg = load_source_registry()
        skills = reg.skills_for_source("eos.skillsource.context.engineering.v1")
        self.assertEqual(skills, ["eos.skillpack.context.engineering"])

    def test_multi_source_support_structure(self) -> None:
        reg = load_source_registry()
        self.assertGreaterEqual(len(reg.sources), 4)


if __name__ == "__main__":
    unittest.main()
