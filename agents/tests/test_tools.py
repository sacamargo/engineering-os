#!/usr/bin/env python3
from __future__ import annotations

import unittest

from agents.tools import get_tool
from agents.tools.permissions import authorize_tool
from agents.tools.risk import evaluate_tool_risk


class ToolModelTests(unittest.TestCase):
    def test_read_vs_write_permissions(self) -> None:
        self.assertTrue(authorize_tool("read_file", ["READ"]).allowed)
        self.assertFalse(authorize_tool("write_file", ["READ"]).allowed)
        self.assertTrue(authorize_tool("write_file", ["READ", "WRITE"]).allowed)

    def test_risk_levels(self) -> None:
        self.assertEqual(get_tool("read_file").risk_level, "LOW")
        self.assertEqual(get_tool("write_file").risk_level, "MEDIUM")
        self.assertEqual(get_tool("run_command").risk_level, "HIGH")
        self.assertFalse(evaluate_tool_risk("run_command", "MEDIUM").allowed)
        self.assertTrue(evaluate_tool_risk("run_command", "HIGH").requires_gate)

    def test_no_deploy_tool(self) -> None:
        with self.assertRaises(KeyError):
            get_tool("deploy_production")


if __name__ == "__main__":
    unittest.main()
