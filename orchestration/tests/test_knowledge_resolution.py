#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from orchestration.capability import resolve_capabilities
from orchestration.capability.arbitration import arbitrate_capabilities
from orchestration.intent import intake_intent
from orchestration.knowledge import resolve_knowledge

ROOT = Path(__file__).resolve().parents[2]


class KnowledgeResolutionTests(unittest.TestCase):
    def test_selects_fulfillment_not_whole_repo(self) -> None:
        intent = intake_intent("Design architecture for a booking SaaS")
        arb = arbitrate_capabilities(intent, resolve_capabilities(intent, ROOT))
        knowledge = resolve_knowledge(arb, ROOT)
        self.assertTrue(knowledge.selected)
        self.assertTrue(
            any(s.unit_id.startswith("eos.playbook.") for s in knowledge.selected)
        )
        # Should not include every markdown file in repo
        self.assertLess(len(knowledge.selected), 20)
        self.assertTrue(any(" Progressive disclosure" in n or "Progressive disclosure" in n for n in knowledge.notes))


if __name__ == "__main__":
    unittest.main()
