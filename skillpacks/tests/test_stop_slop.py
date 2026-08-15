"""Stop Slop skill tests."""

from __future__ import annotations

import unittest

from skillpacks.registry import load_registry
from skillpacks.stop_slop import review_artifact


class StopSlopTests(unittest.TestCase):
    def test_unavailable_registered(self) -> None:
        pack = load_registry().get("eos.skillpack.quality.stop-slop")
        assert pack is not None
        self.assertEqual(pack.status, "unavailable")
        self.assertIn("not_a_god_skill", pack.constraints)

    def test_review_fails_closed_without_source(self) -> None:
        result = review_artifact({"content": "Some design text"})
        self.assertEqual(result.status, "unavailable")
        self.assertFalse(result.claims_correctness)
        self.assertFalse(result.replaces_domain_review)

    def test_boundaries(self) -> None:
        pack = load_registry().get("eos.skillpack.quality.stop-slop")
        assert pack is not None
        self.assertIn("cannot_replace_domain_review", pack.constraints)
        self.assertIn("cannot_bypass_specialist", pack.constraints)
        self.assertTrue(any(r.kind == "transversal" for r in pack.composition_rules))


if __name__ == "__main__":
    unittest.main()
