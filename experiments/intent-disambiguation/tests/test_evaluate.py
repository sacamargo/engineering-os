#!/usr/bin/env python3
"""Tests for intent-disambiguation experiment evaluator."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

EXPERIMENT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT.parents[1]
sys.path.insert(0, str(EXPERIMENT))

from evaluate import evaluate_case, load_catalog, main  # noqa: E402


class IntentDisambiguationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.capabilities, cls.units = load_catalog(REPO_ROOT)

    def test_all_authored_cases_pass(self) -> None:
        self.assertEqual(main(["--repo-root", str(REPO_ROOT)]), 0)

    def test_primary_must_be_candidate(self) -> None:
        case = {
            "id": "bad-primary",
            "utterance": "x",
            "frame": {
                "desired_outcome": "x",
                "object_of_work": "x",
                "intent_class_hint": "x",
                "domain_hints": [],
                "constraints": [],
                "risk_signals": [],
                "multi_intent": False,
                "notes": "x",
            },
            "candidates": [],
            "primary": "eos.capability.design.system-architecture",
            "secondary": [],
            "related_suggested": [],
            "insufficient_coverage": [],
            "clarifying_questions": [],
            "fulfillment_preview": None,
        }
        errors = evaluate_case(case, self.capabilities, self.units, Path("bad.json"))
        self.assertTrue(any("must appear in candidates" in e for e in errors))

    def test_invented_capability_rejected(self) -> None:
        case = {
            "id": "invented",
            "utterance": "x",
            "frame": {
                "desired_outcome": "x",
                "object_of_work": "x",
                "intent_class_hint": "x",
                "domain_hints": [],
                "constraints": [],
                "risk_signals": [],
                "multi_intent": False,
                "notes": "x",
            },
            "candidates": [
                {
                    "id": "eos.capability.performance.optimization",
                    "rationale": "invented",
                    "confidence": "high",
                }
            ],
            "primary": "eos.capability.performance.optimization",
            "secondary": [],
            "related_suggested": [],
            "insufficient_coverage": [],
            "clarifying_questions": [],
            "fulfillment_preview": None,
        }
        errors = evaluate_case(case, self.capabilities, self.units, Path("invented.json"))
        self.assertTrue(any("not an active catalog Capability" in e for e in errors))

    def test_gap_case_without_signal_is_invalid(self) -> None:
        case = {
            "id": "silent",
            "utterance": "x",
            "frame": {
                "desired_outcome": "x",
                "object_of_work": "x",
                "intent_class_hint": "x",
                "domain_hints": [],
                "constraints": [],
                "risk_signals": [],
                "multi_intent": False,
                "notes": "x",
            },
            "candidates": [],
            "primary": None,
            "secondary": [],
            "related_suggested": [],
            "insufficient_coverage": [],
            "clarifying_questions": [],
            "fulfillment_preview": None,
        }
        errors = evaluate_case(case, self.capabilities, self.units, Path("silent.json"))
        self.assertTrue(any("empty resolution" in e for e in errors))

    def test_case_05_declares_insufficient_coverage(self) -> None:
        path = EXPERIMENT / "cases" / "05-slow-checkout-database.json"
        case = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsNone(case["primary"])
        self.assertEqual(case["candidates"], [])
        self.assertGreaterEqual(len(case["insufficient_coverage"]), 1)
        self.assertEqual(evaluate_case(case, self.capabilities, self.units, path), [])


if __name__ == "__main__":
    unittest.main()
