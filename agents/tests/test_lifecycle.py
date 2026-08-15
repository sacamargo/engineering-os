#!/usr/bin/env python3
from __future__ import annotations

import unittest

from agents.lifecycle import InvalidAgentTransition, can_transition, is_terminal, transition


class AgentLifecycleTests(unittest.TestCase):
    def test_happy_path(self) -> None:
        s = "created"
        s = transition(s, "ready")
        s = transition(s, "running")
        s = transition(s, "succeeded")
        self.assertTrue(is_terminal(s))

    def test_blocked_to_escalated(self) -> None:
        s = transition("created", "ready")
        s = transition(s, "running")
        s = transition(s, "blocked")
        s = transition(s, "escalated")
        self.assertEqual(s, "escalated")

    def test_invalid_transition(self) -> None:
        self.assertFalse(can_transition("succeeded", "running"))
        with self.assertRaises(InvalidAgentTransition):
            transition("created", "succeeded")
        with self.assertRaises(InvalidAgentTransition):
            transition("failed", "ready")


if __name__ == "__main__":
    unittest.main()
