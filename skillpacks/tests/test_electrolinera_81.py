"""Phase 8.1 electrolinera agency scenario."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from orchestration.facade import PlanningOrchestrator
from skillpacks.composition import compose_skills
from skillpacks.registry import load_registry
from skillpacks.role_discovery import discover_roles_for_intent
from skillpacks.ux_contract import ux_output_skeleton

ROOT = Path(__file__).resolve().parents[2]
ELECTRO = ROOT / "examples" / "agency" / "electrolinera"


class Electrolinera81Tests(unittest.TestCase):
    def test_full_routing_surface(self) -> None:
        utterance = json.loads((ELECTRO / "input.json").read_text(encoding="utf-8"))["utterance"]
        result = PlanningOrchestrator(ROOT).plan(utterance)
        intent = result.intent
        self.assertIn("build", intent["possible_intents"])

        # Epistemic: do not invent payment provider
        blob = json.dumps(result.to_dict()).lower()
        self.assertNotIn("stripe", blob)

        skills = result.skill_resolution
        cand = {c["skill_id"] for c in skills["candidates"]}
        self.assertIn("eos.skillpack.design.ui-ux-pro-max", cand)
        self.assertNotIn("eos.skillpack.marketing.corey-haines", skills["selected"])
        # Context engineering may be selected (active)
        # composition demo
        reg = load_registry()
        selected = [s for s in skills.get("selected", []) if reg.get(s) and reg.get(s).is_selectable()]
        if "eos.skillpack.context.engineering" not in selected:
            selected.append("eos.skillpack.context.engineering")
        composed = compose_skills(selected, reg)
        self.assertFalse(composed.errors)

        roles = discover_roles_for_intent(intent)
        by_id = {r.role_id: r.need for r in roles}
        self.assertEqual(by_id.get("eos.role.mobile-engineer"), "REQUIRED")
        self.assertEqual(by_id.get("eos.role.frontend-engineer"), "REQUIRED")
        self.assertIn(by_id.get("eos.role.integration-engineer"), {"UNKNOWN", None})

        ux = ux_output_skeleton(utterance)
        self.assertEqual(ux["skill_status"], "unavailable")
        self.assertEqual(ux["artifacts"]["platform_targets"]["content"]["ios"], "REQUIRED")
        self.assertTrue(ux["epistemic"]["UNKNOWN"])
        self.assertIn("payments", ux["epistemic"]["UNKNOWN"])

        # Report-like keys present on planning result
        for key in ("intent", "capability_resolution", "skill_resolution", "roles", "gaps", "delivery"):
            self.assertIn(key, result.to_dict())


if __name__ == "__main__":
    unittest.main()
