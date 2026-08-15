#!/usr/bin/env python3
"""Orchestration ↔ Codebase Intelligence integration."""

from __future__ import annotations

import unittest
from pathlib import Path

from orchestration.boundaries.codebase import LocalCodebaseIntelligence, intent_requires_codebase
from orchestration.facade import PlanningOrchestrator

ROOT = Path(__file__).resolve().parents[2]


class CodebaseOrchestrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.orch = PlanningOrchestrator(ROOT)

    def test_refactor_inserts_codebase_analysis_and_blocks_blind_impl(self) -> None:
        result = self.orch.plan("Refactoriza el módulo de autenticación")
        data = result.to_dict()
        tasks = data["generated"]["tasks"]
        self.assertTrue(any(t.get("task_kind") == "codebase_analysis" for t in tasks))
        self.assertTrue(data["generated"]["project"].get("requires_codebase_analysis"))
        self.assertNotEqual(data["codebase"].get("analysis_status"), "complete")
        self.assertIn(data["readiness"]["status"], {"partially_ready", "needs_input", "ready"})
        # Automatable should prefer analysis task when evidence missing
        auto = data["readiness"].get("automatable_task_ids") or []
        self.assertTrue(any("codebase-analysis" in t for t in auto) or data["readiness"]["status"] == "ready")

    def test_analyze_intent_requires_codebase(self) -> None:
        self.assertTrue(intent_requires_codebase(["analyze"]))
        self.assertFalse(intent_requires_codebase(["analyze"], {"codebase_analyzed": True}))

    def test_local_analyze_produces_evidence(self) -> None:
        # Tiny path: analyze orchestration package only would still be large;
        # use LocalCodebaseIntelligence.analyze on ROOT but only assert schema.
        # To keep test fast, analyze a fixture-like subdirectory if present.
        target = ROOT / "codebase"
        payload = LocalCodebaseIntelligence().analyze(str(target))
        self.assertEqual(payload["schema"], "eos.codebase.analysis.v1")
        self.assertTrue(payload["summary"]["snapshot_id"])


if __name__ == "__main__":
    unittest.main()
