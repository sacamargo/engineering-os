"""Capability binding tests."""

from __future__ import annotations

import unittest

from skillpacks.bindings import capabilities_for_skill, skills_for_capability


class CapabilityBindingTests(unittest.TestCase):
    def test_architecture_may_relate_to_ux(self) -> None:
        skills = skills_for_capability("eos.capability.design.system-architecture")
        self.assertIn("eos.skillpack.design.ui-ux-pro-max", skills)

    def test_not_every_capability_forced_marketing(self) -> None:
        skills = skills_for_capability("eos.capability.operations.observability")
        self.assertNotIn("eos.skillpack.marketing.corey-haines", skills)

    def test_association_not_identity(self) -> None:
        caps = capabilities_for_skill("eos.skillpack.design.ui-ux-pro-max")
        self.assertTrue(caps)
        self.assertTrue(all(c.startswith("eos.capability.") for c in caps))
        self.assertFalse(any(c.startswith("eos.skillpack.") for c in caps))


if __name__ == "__main__":
    unittest.main()
