#!/usr/bin/env python3
"""Behavioral tests for the Planning Orchestrator facade."""

from __future__ import annotations

import unittest
from pathlib import Path

from orchestration.facade import PlanningOrchestrator
from orchestration.evidence import record_claim, record_evidence, task_completion_allowed

ROOT = Path(__file__).resolve().parents[2]


class PlanningOrchestratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.orch = PlanningOrchestrator(ROOT)

    def test_saas_booking_plan(self) -> None:
        result = self.orch.plan(
            "Quiero construir una SaaS de reservas de canchas. Debe ser segura, testeable y observable."
        )
        data = result.to_dict()
        self.assertEqual(
            data["arbitration"]["primary"],
            "eos.capability.design.system-architecture",
        )
        for needed in (
            "eos.capability.security.review",
            "eos.capability.quality.test-planning",
            "eos.capability.operations.observability",
        ):
            self.assertIn(needed, data["arbitration"]["selected"])
        self.assertGreaterEqual(len(data["generated"]["tasks"]), 4)
        self.assertGreaterEqual(len(data["generated"]["artifacts"]), 4)
        self.assertTrue(data["generated"]["gates"])
        self.assertTrue(data["dependencies"]["ok"])
        self.assertIn(data["readiness"]["status"], {"ready", "partially_ready", "needs_input"})
        self.assertTrue(data["roles"]["role_ids"])
        self.assertTrue(data["knowledge"]["unit_ids"])
        self.assertTrue(any(g["kind"] == "MISSING_CAPABILITY" for g in data["gaps"]))

    def test_padel_iot_human_required(self) -> None:
        result = self.orch.plan(
            "Quiero automatizar una cancha de pádel completa: puerta, iluminación y control remoto "
            "desde celular incluso si no estoy físicamente allí, sin depender del Wi-Fi local."
        )
        data = result.to_dict()
        self.assertTrue(data["escalations"])
        self.assertTrue(
            any(
                e["domain"] in {"electrical_engineering", "physical_access_control"}
                for e in data["escalations"]
            )
        )
        self.assertIn(data["readiness"]["status"], {"needs_human", "partially_ready"})
        self.assertTrue(
            any(t.get("requires_professional_approval") for t in data["generated"]["tasks"])
        )

    def test_security_audit(self) -> None:
        result = self.orch.plan("Audita este sistema por vulnerabilidades.")
        self.assertEqual(
            result.arbitration["primary"], "eos.capability.security.review"
        )

    def test_missing_capability_electrical_cert(self) -> None:
        result = self.orch.plan("Certifica eléctricamente esta instalación.")
        data = result.to_dict()
        self.assertTrue(
            any(g["kind"] == "MISSING_CAPABILITY" for g in data["gaps"])
            or data["arbitration"]["insufficient"]
        )
        invented = [
            c
            for c in data["capability_resolution"]["candidates"]
            if "electrical" in c["capability_id"]
        ]
        self.assertEqual(invented, [])

    def test_failure_and_replan(self) -> None:
        result = self.orch.plan("Design architecture for a booking SaaS")
        task_id = result.generated["tasks"][0]["id"]
        failure = self.orch.classify_failure(task_id, "assumption_broken", "driver changed")
        self.assertEqual(failure.action, "replan")
        replan = self.orch.replan(result, task_id)
        self.assertEqual(replan.plan["revision"], result.generated["plan"]["revision"] + 1)

    def test_claim_is_not_evidence(self) -> None:
        claim = record_claim("eos.evidence.x.claim", "done", task_id="eos.task.x.a")
        self.assertFalse(task_completion_allowed([claim], []))
        evidence = record_evidence(
            "eos.evidence.x.out", "test output", source="unittest", task_id="eos.task.x.a"
        )
        self.assertTrue(task_completion_allowed([claim], [evidence]))

    def test_facade_is_not_god_object(self) -> None:
        facade = (ROOT / "orchestration" / "facade" / "__init__.py").read_text()
        # Soft guard: facade should stay relatively small and delegate.
        self.assertLess(len(facade.splitlines()), 220)
        self.assertIn("delegates", facade.lower())
        self.assertNotIn("entry_signals", facade)


if __name__ == "__main__":
    unittest.main()
