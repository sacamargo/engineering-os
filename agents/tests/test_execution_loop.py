#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agents.coding import DeterministicPlan
from agents.loop import run_execution


class ExecutionLoopTests(unittest.TestCase):
    def test_add_function_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "mathutil.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
            (root / "test_mathutil.py").write_text(
                "import unittest\nfrom mathutil import add, mul\n\n"
                "class T(unittest.TestCase):\n"
                "    def test_add(self):\n"
                "        self.assertEqual(add(2, 3), 5)\n"
                "    def test_mul(self):\n"
                "        self.assertEqual(mul(2, 3), 6)\n",
                encoding="utf-8",
            )
            # Initially mul missing — first show failure path separately; for success write both
            (root / "mathutil.py").write_text(
                "def add(a, b):\n    return a + b\n",
                encoding="utf-8",
            )
            plan = DeterministicPlan(
                steps=[
                    {"tool": "read_file", "arguments": {"path": "mathutil.py"}},
                    {
                        "tool": "write_file",
                        "arguments": {
                            "path": "mathutil.py",
                            "content": "def add(a, b):\n    return a + b\n\ndef mul(a, b):\n    return a * b\n",
                        },
                    },
                    {
                        "tool": "run_tests",
                        "arguments": {"command": "python3 -m unittest test_mathutil"},
                    },
                ]
            )
            task = {
                "id": "eos.task.demo.add-mul",
                "title": "Add mul function",
                "task_kind": "coding",
                "target_paths": ["mathutil.py"],
            }
            result = run_execution(root, task, plan, require_tests=True)
            self.assertEqual(result.status, "SUCCESS", msg=result.to_dict())
            self.assertTrue(result.evidence)
            self.assertIn("def mul", (root / "mathutil.py").read_text(encoding="utf-8"))

    def test_permission_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("x=1\n", encoding="utf-8")
            plan = DeterministicPlan(
                steps=[
                    {
                        "tool": "write_file",
                        "arguments": {"path": "a.py", "content": "x=2\n"},
                    }
                ]
            )
            task = {
                "id": "eos.task.demo.analyze-only",
                "title": "Analyze repository",
                "task_kind": "codebase_analysis",
            }
            result = run_execution(root, task, plan, require_tests=False)
            self.assertIn(result.status, {"FAILED", "REPLAN"})
            self.assertTrue(result.failures or result.evidence)

    def test_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = DeterministicPlan(
                steps=[{"tool": "write_file", "arguments": {"path": "x.py", "content": "1"}}]
            )
            task = {"id": "eos.task.demo.dry", "title": "Add code", "task_kind": "coding"}
            result = run_execution(root, task, plan, dry_run=True)
            self.assertEqual(result.status, "DRY_RUN")
            self.assertFalse((root / "x.py").exists())

    def test_human_escalation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = {
                "id": "eos.task.demo.electrical",
                "title": "Certify electrical install",
                "requires_professional_approval": True,
            }
            result = run_execution(tmp, task, None)
            self.assertEqual(result.status, "NEEDS_HUMAN")


if __name__ == "__main__":
    unittest.main()
