#!/usr/bin/env python3
from __future__ import annotations

import unittest

from agents.task_states import (
    InvalidTaskTransition,
    assert_agent_task_pair_legal,
    task_status_for_agent,
    transition_task,
)


class TaskStateIntegrationTests(unittest.TestCase):
    def test_execution_path(self) -> None:
        s = "pending"
        for nxt in ("ready", "assigned", "in_progress", "validating", "completed"):
            s = transition_task(s, nxt)
        self.assertEqual(s, "completed")

    def test_agent_success_is_not_task_completed(self) -> None:
        self.assertEqual(task_status_for_agent("succeeded"), "validating")
        self.assertNotEqual(task_status_for_agent("succeeded"), "completed")

    def test_invalid_skip(self) -> None:
        with self.assertRaises(InvalidTaskTransition):
            transition_task("ready", "completed")

    def test_paired_legal(self) -> None:
        assert_agent_task_pair_legal("ready", "running", "assigned", "in_progress")
        with self.assertRaises(InvalidTaskTransition):
            assert_agent_task_pair_legal("created", "succeeded", "ready", "completed")


if __name__ == "__main__":
    unittest.main()
