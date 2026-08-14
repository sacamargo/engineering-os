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
        self.assertIn("boundary only", " ".join(data["codebase"]["notes"]).lower())

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
