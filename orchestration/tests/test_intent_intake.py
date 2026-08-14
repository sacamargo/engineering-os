#!/usr/bin/env python3
"""Tests for Intent Intake."""

from __future__ import annotations

import unittest

from orchestration.intent import intake_intent


class IntentIntakeTests(unittest.TestCase):
    def test_saas_spanish_multi_constraint(self) -> None:
        intent = intake_intent(
            "Quiero construir una SaaS de reservas de canchas. Debe ser segura, testeable y observable."
        )
        self.assertEqual(intent.language, "es")
        self.assertIn("build", intent.possible_intents)
        domains = {s.value for s in intent.signals if s.kind == "domain"}
        self.assertTrue({"security", "testing", "observability"} & domains)
        self.assertTrue(any(c.startswith("Must be secure") for c in intent.constraints))
        # Must not invent Stripe / PSP
        self.assertTrue(any(u.key == "payments_required" for u in intent.uncertainties))
        self.assertTrue(any("payment" in q.lower() for q in intent.clarifying_questions))
        self.assertFalse(any("stripe" in intent.utterance.lower() for _ in [0]))
        self.assertFalse(any("stripe" in f.value.lower() for f in intent.context))

    def test_does_not_invent_payment_provider(self) -> None:
        intent = intake_intent("Build a booking SaaS")
        values = " ".join(f.value for f in intent.context + intent.uncertainties)
        self.assertNotIn("stripe", values.lower())

    def test_empty_utterance_rejected(self) -> None:
        with self.assertRaises(ValueError):
            intake_intent("  ")

    def test_known_context_passthrough(self) -> None:
        intent = intake_intent(
            "Design architecture for Rivallium",
            context={"repo": "examples/rivallium"},
        )
        self.assertTrue(any(f.key == "repo" and f.certainty == "known" for f in intent.context))


if __name__ == "__main__":
    unittest.main()
