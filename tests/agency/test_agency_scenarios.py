#!/usr/bin/env python3
"""Agency scenario contract tests for Engineering OS Execution Layer."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = Path(__file__).resolve().parent / "scenarios"
EXAMPLES = ROOT / "examples"

LIVE_CAPABILITIES = {
    "eos.capability.design.system-architecture",
    "eos.capability.security.review",
    "eos.capability.quality.test-planning",
    "eos.capability.operations.observability",
}


def load_scenario(name: str) -> dict:
    return json.loads((SCENARIOS / f"{name}.json").read_text(encoding="utf-8"))


class AgencyScenarioTests(unittest.TestCase):
    def assert_scenario_shape(self, data: dict) -> None:
        for key in (
            "id",
            "intent",
            "intent_recognized",
            "capabilities_resolved",
            "gaps_detected",
            "artifacts_identified",
            "tasks_generated",
            "validation_required",
            "human_escalation_when_necessary",
        ):
            self.assertIn(key, data)
        self.assertTrue(data["intent_recognized"])
        self.assertTrue(data["artifacts_identified"])
        self.assertTrue(data["tasks_generated"])
        self.assertTrue(data["validation_required"])
        for cid in data["capabilities_resolved"]:
            self.assertIn(cid, LIVE_CAPABILITIES, f"invented capability: {cid}")
        for gap in data["gaps_detected"]:
            self.assertNotRegex(
                gap.get("area", ""),
                r"^eos\.capability\.",
                "gaps must not invent capability ids as areas",
            )
            if gap.get("invented_capability_id"):
                self.fail("must not invent capability ids")

    def test_build_saas(self) -> None:
        data = load_scenario("build-saas")
        self.assert_scenario_shape(data)
        self.assertFalse(data["human_escalation_when_necessary"])

    def test_analyze_repository(self) -> None:
        self.assert_scenario_shape(load_scenario("analyze-repository"))

    def test_audit_system(self) -> None:
        self.assert_scenario_shape(load_scenario("audit-system"))

    def test_refactor_codebase(self) -> None:
        self.assert_scenario_shape(load_scenario("refactor-codebase"))

    def test_design_architecture(self) -> None:
        self.assert_scenario_shape(load_scenario("design-architecture"))

    def test_investigate_incident(self) -> None:
        self.assert_scenario_shape(load_scenario("investigate-incident"))

    def test_optimize_application(self) -> None:
        self.assert_scenario_shape(load_scenario("optimize-application"))

    def test_migrate_legacy_system(self) -> None:
        self.assert_scenario_shape(load_scenario("migrate-legacy-system"))

    def test_build_iot_system(self) -> None:
        data = load_scenario("build-iot-system")
        self.assert_scenario_shape(data)
        self.assertTrue(data["human_escalation_when_necessary"])
        self.assertTrue(
            any(g.get("professional_validation_required") for g in data["gaps_detected"])
        )

    def test_padel_iot_fixture_aligns(self) -> None:
        project = json.loads((EXAMPLES / "padel-iot" / "project.json").read_text())
        self.assertTrue(any(
            g.get("professional_validation_required")
            for g in project.get("insufficient_coverage", [])
        ))
        esc_dir = EXAMPLES / "padel-iot" / "escalations"
        self.assertTrue(esc_dir.exists())
        self.assertGreaterEqual(len(list(esc_dir.glob("*.json"))), 2)

    def test_rivallium_fixture_multi_capability(self) -> None:
        project = json.loads((EXAMPLES / "rivallium" / "project.json").read_text())
        caps = set(project["capability_ids"])
        self.assertTrue(LIVE_CAPABILITIES.issubset(caps) or caps == LIVE_CAPABILITIES)
        self.assertGreaterEqual(len(project["insufficient_coverage"]), 1)


if __name__ == "__main__":
    unittest.main()
