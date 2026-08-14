#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from orchestration.capability import resolve_capabilities
from orchestration.capability.arbitration import arbitrate_capabilities
from orchestration.intent import intake_intent
from orchestration.knowledge import resolve_knowledge
from orchestration.plan import generate_plan
from orchestration.role import resolve_roles

ROOT = Path(__file__).resolve().parents[2]


class PlanGenerationTests(unittest.TestCase):
    def test_saas_plan_artifact_dependencies(self) -> None:
        utterance = (
            "Quiero construir una SaaS de reservas de canchas. "
            "Debe ser segura, testeable y observable."
        )
        intent = intake_intent(utterance)
        arb = arbitrate_capabilities(intent, resolve_capabilities(intent, ROOT))
        roles = resolve_roles(intent, arb)
        knowledge = resolve_knowledge(arb, ROOT)
        plan = generate_plan(intent, arb, roles, knowledge, project_slug="booking-saas")

        self.assertEqual(plan.project["status"], "planned")
        caps = set(plan.plan["capability_ids"])
        self.assertIn("eos.capability.design.system-architecture", caps)
        self.assertIn("eos.capability.security.review", caps)
        self.assertEqual(arb.primary, "eos.capability.design.system-architecture")

        art_types = {a["type"] for a in plan.artifacts}
        self.assertIn("architecture", art_types)
        self.assertIn("threat_model", art_types)
        self.assertIn("test_strategy", art_types)
        self.assertIn("observability_plan", art_types)

        # Security depends on architecture artifact/task — not a Capability DAG claim
        sec = next(t for t in plan.tasks if t["id"].endswith("security-review"))
        self.assertTrue(any(i.endswith(".architecture") for i in sec["input_artifact_ids"]))
        self.assertTrue(any(d.endswith("design-architecture") for d in sec["depends_on_task_ids"]))

        # Parallel secondaries after architecture: test and observability both depend on architecture
        test = next(t for t in plan.tasks if t["id"].endswith("test-planning"))
        obs = next(t for t in plan.tasks if t["id"].endswith("observability-design"))
        self.assertIn(
            next(t["id"] for t in plan.tasks if t["id"].endswith("design-architecture")),
            test["depends_on_task_ids"],
        )
        self.assertIn(
            next(t["id"] for t in plan.tasks if t["id"].endswith("design-architecture")),
            obs["depends_on_task_ids"],
        )
        blob = str(plan.to_dict()).lower()
        self.assertNotIn('"choice": "stripe"', blob)
        self.assertFalse(
            any(
                f.get("value", "").lower() == "stripe"
                for f in plan.project.get("uncertainties", [])
            )
        )
        self.assertTrue(plan.gates)
        self.assertTrue(plan.project["insufficient_coverage"])


if __name__ == "__main__":
    unittest.main()
