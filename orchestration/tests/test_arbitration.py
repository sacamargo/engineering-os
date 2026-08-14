#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from orchestration.capability import resolve_capabilities
from orchestration.capability.arbitration import arbitrate_capabilities
from orchestration.intent import intake_intent

ROOT = Path(__file__).resolve().parents[2]


class ArbitrationTests(unittest.TestCase):
    def test_saas_multi_capability_no_capability_dag_claim(self) -> None:
        intent = intake_intent(
            "Build a booking SaaS that is secure, testable, and observable."
        )
        resolution = resolve_capabilities(intent, ROOT)
        arb = arbitrate_capabilities(intent, resolution)
        self.assertTrue(arb.primary)
        self.assertGreaterEqual(len(arb.selected), 2)
        self.assertTrue(any("artifact/task dependencies" in n for n in arb.notes))
        # related must not force selection of all catalog neighbors automatically
        for note in arb.notes:
            self.assertNotIn("execute security after architecture capability", note.lower())

    def test_insufficient_marks_gaps(self) -> None:
        intent = intake_intent(
            "Quiero automatizar una cancha de pádel con iluminación eléctrica y puerta."
        )
        resolution = resolve_capabilities(intent, ROOT)
        arb = arbitrate_capabilities(intent, resolution)
        areas = {i["area"] for i in arb.insufficient}
        self.assertTrue({"electrical_engineering", "physical_access_control"} & areas)


if __name__ == "__main__":
    unittest.main()
