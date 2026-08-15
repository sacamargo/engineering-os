"""Phase 8.1 runtime polish tests."""

from __future__ import annotations

import unittest

from skillpacks.agent_bridge import bind_skills_to_agent
from skillpacks.role_discovery import discover_roles_for_intent
from skillpacks.routing import resolve_skills
from skillpacks.ux_contract import ux_output_skeleton


class RuntimePolishTests(unittest.TestCase):
    def test_bounded_context_not_full_dump(self) -> None:
        binding = bind_skills_to_agent(
            task={"id": "eos.task.t1"},
            capability_ids=["eos.capability.design.system-architecture"],
            skill_ids=["eos.skillpack.context.engineering"],
            role_ids=["eos.role.technical-lead"],
            agent_type="analysis",
            tool_permissions=["READ"],
        )
        self.assertFalse(binding.context.get("full_skill_dumped"))
        self.assertTrue(binding.invocations)
        self.assertIn("source_versions", binding.invocations[0])

    def test_marketing_not_on_backend_bug(self) -> None:
        result = resolve_skills(
            {
                "utterance": "Fix backend bug causing null pointer in booking API",
                "possible_intents": ["investigate_incident"],
                "signals": [],
                "domains": [],
            },
            [],
            min_score=0.5,
        )
        self.assertNotIn("eos.skillpack.marketing.corey-haines", result.selected)

    def test_role_discovery_electrolinera(self) -> None:
        roles = discover_roles_for_intent(
            {
                "utterance": "Quiero una aplicación para electrolinera iOS Android y web",
                "possible_intents": ["build"],
            }
        )
        by_id = {r.role_id: r for r in roles}
        self.assertEqual(by_id["eos.role.mobile-engineer"].need, "REQUIRED")
        self.assertEqual(by_id["eos.role.frontend-engineer"].need, "REQUIRED")
        # payments engineer not assumed as dedicated required role invent
        self.assertTrue(any(r.need == "UNKNOWN" for r in roles))

    def test_ux_skeleton_distinguishes_platforms(self) -> None:
        sk = ux_output_skeleton("app for iOS and Android and also web")
        targets = sk["artifacts"]["platform_targets"]["content"]
        self.assertEqual(targets["ios"], "REQUIRED")
        self.assertEqual(targets["android"], "REQUIRED")
        self.assertEqual(targets["web"], "REQUIRED")
        self.assertEqual(sk["skill_status"], "unavailable")


if __name__ == "__main__":
    unittest.main()
