"""Agency scenarios for Skill Integration (Phase 8)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from orchestration.boundaries.codebase import intent_requires_codebase
from orchestration.facade import PlanningOrchestrator
from skillpacks.composition import compose_skills
from skillpacks.context_engineering import assemble_context
from skillpacks.registry import load_registry
from skillpacks.routing import resolve_skills

ROOT = Path(__file__).resolve().parents[2]
ELECTRO = ROOT / "examples" / "agency" / "electrolinera"
QUOTE = ROOT / "examples" / "agency" / "quotation-assessment"


class ElectrolineraScenarioTests(unittest.TestCase):
    def test_electrolinera_skills_and_unknowns(self) -> None:
        data = json.loads((ELECTRO / "input.json").read_text(encoding="utf-8"))
        utterance = data["utterance"]
        orch = PlanningOrchestrator(ROOT)
        result = orch.plan(utterance)
        intent = result.intent
        self.assertIn("build", intent["possible_intents"])
        # Do not invent payment provider
        ctx_vals = [str(c.get("value")) for c in intent.get("context") or []]
        self.assertNotIn("stripe", " ".join(ctx_vals).lower())

        skills = result.skill_resolution
        # UI UX should be considered (mobile+web) — may be unavailable but not absent from consideration
        cand_ids = {c["skill_id"] for c in skills["candidates"]}
        self.assertIn("eos.skillpack.design.ui-ux-pro-max", cand_ids)
        # Marketing not forced
        self.assertNotIn("eos.skillpack.marketing.corey-haines", skills["selected"])
        # Context engineering may assemble separately
        ctx = assemble_context(
            intent=intent,
            skill_ids=skills.get("selected") or [],
            capability_ids=[result.arbitration.get("primary")] if result.arbitration.get("primary") else [],
            unresolved_questions=intent.get("clarifying_questions") or [],
        )
        self.assertIn("intent", ctx.included_keys)
        self.assertFalse(ctx.to_dict()["full_repo_dumped"])

        # Unknowns remain present as clarifying / missing
        self.assertTrue(
            intent.get("clarifying_questions")
            or result.gaps
            or result.capability_resolution.get("missing")
        )


class QuotationAssessmentTests(unittest.TestCase):
    def test_quotation_is_not_codebase_task(self) -> None:
        text = (QUOTE / "quotation.md").read_text(encoding="utf-8")
        utterance = f"Analiza esta cotización como assessment de alcance:\n\n{text[:500]}"
        # Explicit context: assessment artifact — must not require codebase
        self.assertFalse(
            intent_requires_codebase(
                ["analyze"],
                {"artifact_kind": "quotation", "assessment": True},
            )
        )
        orch = PlanningOrchestrator(ROOT)
        result = orch.plan(utterance, context={"artifact_kind": "quotation", "assessment": True})
        self.assertFalse(intent_requires_codebase(result.intent["possible_intents"], {"assessment": True}))
        # Should not mark codebase analysis as required via readiness when assessment
        notes = " ".join(result.notes).lower()
        # Gaps may mention missing info, not repo indexing
        gap_text = json.dumps(result.gaps).lower()
        self.assertNotIn("snapshot", gap_text)


class SkillSelectionMatrixTests(unittest.TestCase):
    def test_landing_may_select_marketing_and_ux_candidates(self) -> None:
        intent = {
            "utterance": "Create a landing page to improve conversion",
            "possible_intents": ["design", "build"],
            "signals": [],
            "domains": [],
        }
        result = resolve_skills(intent, ["eos.capability.design.system-architecture"], min_score=0.5)
        ids = {
            c.skill_id
            for c in result.candidates
            if c.score > 0 or c.role == "unavailable"
        }
        self.assertIn("eos.skillpack.design.ui-ux-pro-max", ids)
        self.assertIn("eos.skillpack.marketing.corey-haines", result.unavailable)


if __name__ == "__main__":
    unittest.main()
