#!/usr/bin/env python3
from __future__ import annotations

import unittest

from delivery.model import Build, default_pipeline
from delivery.states import InvalidDeliveryTransition, transition


class DeliveryModelTests(unittest.TestCase):
    def test_build_requires_evidence(self) -> None:
        b = Build(id="eos.build.x", changeset_id="cs1", environment="local")
        with self.assertRaises(ValueError):
            b.mark_succeeded(evidence=[], artifact_ids=[])
        b.mark_succeeded(evidence=[{"kind": "log", "ok": True}], artifact_ids=["a1"])
        self.assertEqual(b.status, "succeeded")

    def test_pipeline_order(self) -> None:
        p = default_pipeline()
        ordered = [s.id for s in p.ordered_steps()]
        self.assertEqual(ordered[0], "source")
        self.assertLess(ordered.index("build"), ordered.index("test"))
        self.assertLess(ordered.index("artifact"), ordered.index("release_readiness"))

    def test_state_prohibitions(self) -> None:
        with self.assertRaises(InvalidDeliveryTransition):
            transition("failed", "released")
        with self.assertRaises(InvalidDeliveryTransition):
            transition("validating", "released")
        with self.assertRaises(InvalidDeliveryTransition):
            transition("needs_human", "released")
        self.assertEqual(transition("draft", "building"), "building")
        self.assertEqual(transition("validating", "ready"), "ready")
        self.assertEqual(transition("needs_human", "ready"), "ready")
        self.assertEqual(transition("ready", "released"), "released")


if __name__ == "__main__":
    unittest.main()
