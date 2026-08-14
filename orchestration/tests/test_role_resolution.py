#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from orchestration.capability import resolve_capabilities
from orchestration.capability.arbitration import arbitrate_capabilities
from orchestration.intent import intake_intent
from orchestration.role import resolve_roles

ROOT = Path(__file__).resolve().parents[2]


class RoleResolutionTests(unittest.TestCase):
    def test_saas_roles_not_agents(self) -> None:
        intent = intake_intent(
            "Build a booking SaaS that is secure, testable, and observable."
        )
        arb = arbitrate_capabilities(intent, resolve_capabilities(intent, ROOT))
        roles = resolve_roles(intent, arb)
        ids = {r.role_id for r in roles.roles}
        self.assertIn("eos.role.system-architect", ids)
        self.assertIn("eos.role.security-engineer", ids)
        self.assertTrue(any("not Agents" in n for n in roles.notes))
        for r in roles.roles:
            self.assertTrue(r.role_id.startswith("eos.role."))
            self.assertFalse(r.role_id.startswith("eos.capability."))

    def test_electrical_human_required(self) -> None:
        intent = intake_intent(
            "Automatiza iluminación eléctrica de una cancha de pádel."
        )
        arb = arbitrate_capabilities(intent, resolve_capabilities(intent, ROOT))
        roles = resolve_roles(intent, arb)
        electrical = next(
            r for r in roles.roles if r.role_id == "eos.role.electrical-engineer-professional"
        )
        self.assertTrue(electrical.human_required)
        self.assertEqual(electrical.executor_hint, "human")
        self.assertFalse(electrical.future_agent_eligible)


if __name__ == "__main__":
    unittest.main()
