"""UI UX PRO MAX tests."""

from __future__ import annotations

import unittest

from skillpacks.registry import load_registry
from skillpacks.routing import resolve_skills
from skillpacks.ui_ux import invoke_ui_ux


class UiUxProMaxTests(unittest.TestCase):
    def test_registered_unavailable(self) -> None:
        pack = load_registry().get("eos.skillpack.design.ui-ux-pro-max")
        assert pack is not None
        self.assertEqual(pack.status, "unavailable")
        modes = (pack.metadata or {}).get("modes")
        self.assertEqual(modes, ["DESIGN", "REVIEW", "IMPROVEMENT"])

    def test_mobile_booking_design_candidate(self) -> None:
        intent = {
            "utterance": "Design a mobile booking app for iOS and Android",
            "possible_intents": ["design", "build"],
            "signals": [],
            "domains": [],
        }
        result = resolve_skills(intent, ["eos.capability.design.system-architecture"], min_score=0.5)
        self.assertIn("eos.skillpack.design.ui-ux-pro-max", result.unavailable)

    def test_improve_checkout_review_mode(self) -> None:
        inv = invoke_ui_ux("REVIEW", intent="Improve this existing checkout UX")
        self.assertEqual(inv.mode, "REVIEW")
        self.assertEqual(inv.status, "unavailable")
        self.assertFalse(inv.grants_code_execution)
        self.assertFalse(inv.bypasses_security)

    def test_api_not_primary(self) -> None:
        intent = {
            "utterance": "Build an API for payments",
            "possible_intents": ["build"],
            "signals": [],
            "domains": [],
        }
        result = resolve_skills(intent, [], min_score=0.75)
        self.assertNotIn("eos.skillpack.design.ui-ux-pro-max", result.selected)

    def test_no_permission_grant(self) -> None:
        pack = load_registry().get("eos.skillpack.design.ui-ux-pro-max")
        assert pack is not None
        self.assertIn("cannot_grant_frontend_code_execution", pack.constraints)
        self.assertIn("cannot_bypass_security_gates", pack.constraints)


if __name__ == "__main__":
    unittest.main()
