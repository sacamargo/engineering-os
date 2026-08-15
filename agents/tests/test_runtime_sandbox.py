#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agents.invocation import ToolInvocation
from agents.model import ANALYSIS_AGENT, CODING_AGENT, instantiate
from agents.runtime import LocalToolRuntime
from agents.sandbox import Workspace, WorkspaceEscapeError


class SandboxRuntimeTests(unittest.TestCase):
    def test_path_traversal_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("x", encoding="utf-8")
            ws = Workspace(root)
            with self.assertRaises(WorkspaceEscapeError):
                ws.resolve("../etc/passwd")
            with self.assertRaises(WorkspaceEscapeError):
                ws.resolve("/etc/passwd")

    def test_read_write_and_permission_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text("x = 1\n", encoding="utf-8")
            coding = instantiate(CODING_AGENT, "eos.task.t1")
            coding.status = "running"
            rt = LocalToolRuntime(Workspace(root), CODING_AGENT, coding)
            ok = rt.invoke(
                ToolInvocation("read_file", {"path": "app.py"}, "eos.task.t1", coding.id)
            )
            self.assertTrue(ok.success)
            write = rt.invoke(
                ToolInvocation(
                    "write_file",
                    {"path": "app.py", "content": "x = 2\n"},
                    "eos.task.t1",
                    coding.id,
                )
            )
            self.assertTrue(write.success)
            self.assertTrue(rt.write_log)

            analysis = instantiate(ANALYSIS_AGENT, "eos.task.t2")
            art = LocalToolRuntime(Workspace(root), ANALYSIS_AGENT, analysis)
            denied = art.invoke(
                ToolInvocation(
                    "write_file",
                    {"path": "app.py", "content": "nope"},
                    "eos.task.t2",
                    analysis.id,
                )
            )
            self.assertFalse(denied.success)
            self.assertIn("PermissionError", denied.error or "")

    def test_command_injection_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            coding = instantiate(CODING_AGENT, "eos.task.t3")
            rt = LocalToolRuntime(Workspace(root), CODING_AGENT, coding, approval_granted=True)
            bad = rt.invoke(
                ToolInvocation(
                    "run_command",
                    {"command": "git status; rm -rf /"},
                    "eos.task.t3",
                    coding.id,
                )
            )
            self.assertFalse(bad.success)


if __name__ == "__main__":
    unittest.main()
