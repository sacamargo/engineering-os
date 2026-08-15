#!/usr/bin/env python3
"""Additional Phase 4 scenario coverage: refactor + incident."""

from __future__ import annotations

import unittest
from pathlib import Path

from orchestration.facade import PlanningOrchestrator

ROOT = Path(__file__).resolve().parents[2]


class ExtraScenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.orch = PlanningOrchestrator(ROOT)

    def test_refactor_scenario(self) -> None:
        result = self.orch.plan("Refactoriza este repositorio sin romper funcionalidades.")
        data = result.to_dict()
        self.assertTrue(data["capability_resolution"]["candidates"])
        tasks = data["generated"]["tasks"]
        self.assertTrue(any(t.get("task_kind") == "codebase_analysis" for t in tasks))
        self.assertIn(data["readiness"]["status"], {"partially_ready", "ready", "needs_input"})
        self.assertTrue(
            any(g.get("kind") == "MISSING_CODEBASE_EVIDENCE" for g in data["gaps"])
        )
        self.assertIn(data["codebase"]["analysis_status"], {"deferred", "not_run", "complete"})

    def test_incident_scenario(self) -> None:
        result = self.orch.plan("Mi API está devolviendo 500 en producción.")
        data = result.to_dict()
        ids = {c["capability_id"] for c in data["capability_resolution"]["candidates"]}
        self.assertIn("eos.capability.operations.observability", ids)
        self.assertTrue(
            any(e["domain"] == "production_access" for e in data["escalations"])
            or "production_impact" in data["intent"]["risk_signals"]
        )


if __name__ == "__main__":
    unittest.main()
