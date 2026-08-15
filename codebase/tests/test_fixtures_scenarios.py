#!/usr/bin/env python3
"""Real fixture analyses: Rivallium mini, Padel IoT mini, legacy chaos."""

from __future__ import annotations

import unittest
from pathlib import Path

from codebase.analyze import analyze_repository
from orchestration.facade import PlanningOrchestrator

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


class FixtureAnalysisTests(unittest.TestCase):
    def test_rivallium_mini_real_analysis(self) -> None:
        bundle = analyze_repository(FIXTURES / "rivallium-mini")
        snap = bundle.snapshot
        paths = {f["path"] for f in snap.files}
        self.assertIn("services/booking.py", paths)
        self.assertTrue(any(s["name"] == "create_booking" for s in snap.symbols))
        self.assertTrue(snap.dependencies)
        self.assertTrue(snap.tests)
        self.assertTrue(any(c["config_type"] in {"pip_requirements", "npm_manifest"} for c in snap.configurations))
        self.assertTrue(any(a["kind"] in {"layer_directory", "entry_point"} for a in snap.architecture_signals))
        self.assertTrue(snap.evidence)
        self.assertTrue(snap.unknowns)
        # coverage must not be invented as 0%
        for t in snap.tests:
            self.assertEqual(t.get("coverage"), "unknown")

    def test_padel_iot_detects_infra_and_human_scopes(self) -> None:
        bundle = analyze_repository(FIXTURES / "padel-iot-mini")
        snap = bundle.snapshot
        cfg_types = {c["config_type"] for c in snap.configurations}
        self.assertTrue({"docker", "compose"} & cfg_types or any("docker" in c["path"] for c in snap.configurations))
        # Orchestration must escalate physical/electrical — software fixture alone is not certification
        orch = PlanningOrchestrator(ROOT)
        plan = orch.plan(
            "Quiero automatizar una cancha de pádel con IoT, iluminación eléctrica y control de acceso físico."
        ).to_dict()
        self.assertIn(plan["readiness"]["status"], {"needs_human", "partially_ready"})
        self.assertTrue(plan["escalations"] or any(t.get("requires_professional_approval") for t in plan["generated"]["tasks"]))
        # Analysis unknowns must remain explicit
        self.assertTrue(any("Runtime" in u or "unknown" in u.lower() for u in snap.unknowns))

    def test_legacy_chaos_describes_mess(self) -> None:
        bundle = analyze_repository(FIXTURES / "legacy-chaos")
        snap = bundle.snapshot
        kinds = {f["kind"] for f in snap.findings}
        self.assertTrue({"circular_dependency", "dead_module", "insecure_pattern", "sensitive_path", "missing_tests"} & kinds)
        # secrets path inventoried without claiming contents were read safely
        sensitive = [f for f in snap.files if f.get("sensitive")]
        self.assertTrue(sensitive)
        for f in sensitive:
            self.assertFalse(f.get("content_readable"))


if __name__ == "__main__":
    unittest.main()
