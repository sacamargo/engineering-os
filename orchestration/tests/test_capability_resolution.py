#!/usr/bin/env python3
"""Tests for Capability Resolution."""

from __future__ import annotations

import unittest
from pathlib import Path

from orchestration.capability import resolve_capabilities
from orchestration.catalog import load_capabilities
from orchestration.intent import intake_intent

ROOT = Path(__file__).resolve().parents[2]


class CapabilityResolutionTests(unittest.TestCase):
    def test_loads_live_catalog(self) -> None:
        caps = load_capabilities(ROOT)
        self.assertGreaterEqual(len(caps), 4)
        self.assertIn("eos.capability.design.system-architecture", caps)

    def test_saas_secure_testable_observable(self) -> None:
        intent = intake_intent(
            "Quiero construir una SaaS de reservas de canchas. Debe ser segura, testeable y observable."
        )
        resolution = resolve_capabilities(intent, ROOT)
        ids = {c.capability_id for c in resolution.candidates}
        self.assertIn("eos.capability.design.system-architecture", ids)
        self.assertIn("eos.capability.security.review", ids)
        self.assertIn("eos.capability.quality.test-planning", ids)
        self.assertIn("eos.capability.operations.observability", ids)
        self.assertTrue(resolution.primary)
        self.assertTrue(any(m.area == "backend_implementation" for m in resolution.missing))
        # Never invent capability ids
        for c in resolution.candidates:
            self.assertTrue(c.capability_id.startswith("eos.capability."))
            self.assertIn(c.capability_id, load_capabilities(ROOT))

    def test_security_audit_prefers_security(self) -> None:
        intent = intake_intent("Audita este sistema por vulnerabilidades.")
        resolution = resolve_capabilities(intent, ROOT)
        self.assertEqual(resolution.primary, "eos.capability.security.review")

    def test_missing_electrical_not_invented(self) -> None:
        intent = intake_intent("Certifica eléctricamente esta instalación.")
        resolution = resolve_capabilities(intent, ROOT)
        self.assertTrue(resolution.missing)
        invented = [c for c in resolution.candidates if "electrical" in c.capability_id]
        self.assertEqual(invented, [])


if __name__ == "__main__":
    unittest.main()
