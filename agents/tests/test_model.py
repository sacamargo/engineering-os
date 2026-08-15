#!/usr/bin/env python3
from __future__ import annotations

import unittest

from agents.model import ANALYSIS_AGENT, CODING_AGENT, AgentDefinition, instantiate


class AgentModelTests(unittest.TestCase):
    def test_definition_vs_instance(self) -> None:
        inst = instantiate(CODING_AGENT, task_id="eos.task.demo.x")
        self.assertTrue(inst.id.startswith("eos.agent.run."))
        self.assertEqual(inst.definition_id, CODING_AGENT.id)
        self.assertEqual(inst.status, "created")
        self.assertIn("READ", inst.permissions)
        self.assertIn("WRITE", inst.permissions)
        self.assertNotIn("DEPLOY", inst.permissions)

    def test_analysis_is_read_only(self) -> None:
        self.assertEqual(ANALYSIS_AGENT.permissions, ["READ"])
        self.assertNotIn("write_file", ANALYSIS_AGENT.authorized_tools)

    def test_god_agent_rejected(self) -> None:
        god = AgentDefinition(
            id="eos.agent.god",
            type="coding",
            permissions=["READ", "WRITE", "EXECUTE", "NETWORK", "GIT", "DEPLOY"],
            authorized_tools=["a"] * 5,
            risk_ceiling="CRITICAL",
        )
        with self.assertRaises(ValueError):
            instantiate(god)


if __name__ == "__main__":
    unittest.main()
