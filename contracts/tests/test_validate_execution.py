#!/usr/bin/env python3
"""Tests for Engineering OS Execution Layer validation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

CONTRACTS = Path(__file__).resolve().parent.parent
REPO = CONTRACTS.parent
sys.path.insert(0, str(CONTRACTS))

from validate_execution import (  # noqa: E402
    load_capability_ids,
    validate_bundle,
)

FIX = CONTRACTS / "fixtures" / "execution"


class ValidateExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.caps = load_capability_ids(REPO)

    def errors(self, name: str) -> list[str]:
        return validate_bundle(FIX / name, self.caps)

    def test_valid_multi_capability_project(self) -> None:
        errs = self.errors("valid-multi-capability")
        self.assertEqual(errs, [], "\n".join(errs))

    def test_valid_dependency(self) -> None:
        errs = self.errors("valid-dependency")
        self.assertEqual(errs, [], "\n".join(errs))

    def test_invalid_project(self) -> None:
        errs = self.errors("invalid-project")
        joined = "\n".join(errs)
        self.assertTrue(errs)
        self.assertIn("invalid project id", joined)
        self.assertIn("invalid project status", joined)

    def test_invalid_task(self) -> None:
        errs = self.errors("invalid-task")
        joined = "\n".join(errs)
        self.assertTrue(errs)
        self.assertIn("invalid task id", joined)
        self.assertIn("missing input artifact", joined)

    def test_invalid_dependency(self) -> None:
        errs = self.errors("invalid-dependency")
        joined = "\n".join(errs)
        self.assertTrue(errs)
        self.assertTrue(
            "missing dependency task" in joined or "invalid task_depends_on_task" in joined,
            joined,
        )

    def test_cyclic_dependency(self) -> None:
        errs = self.errors("cyclic-dependency")
        self.assertTrue(any("cyclic task dependency" in e for e in errs), "\n".join(errs))

    def test_broken_artifact_reference(self) -> None:
        errs = self.errors("broken-artifact-ref")
        self.assertTrue(any("broken depends_on" in e for e in errs), "\n".join(errs))

    def test_invalid_gate(self) -> None:
        errs = self.errors("invalid-gate")
        joined = "\n".join(errs)
        self.assertTrue(errs)
        self.assertIn("invalid gate id", joined)
        self.assertTrue("requires evidence" in joined or "missing condition" in joined, joined)

    def test_valid_role_binding(self) -> None:
        errs = self.errors("valid-multi-capability")
        self.assertEqual(errs, [], "\n".join(errs))
        bindings = (FIX / "valid-multi-capability" / "roles" / "bindings.json").read_text()
        self.assertIn("eos.role.system-architect", bindings)
        self.assertNotIn("eos.capability.system-architect", bindings)

    def test_invalid_role(self) -> None:
        errs = self.errors("invalid-role")
        self.assertTrue(any("invalid role id" in e for e in errs), "\n".join(errs))

    def test_invalid_role_binding(self) -> None:
        errs = self.errors("invalid-role-binding")
        joined = "\n".join(errs)
        self.assertTrue(errs)
        self.assertTrue(
            "requires non-empty role_ids" in joined or "unknown capability" in joined or "invalid role binding" in joined,
            joined,
        )


if __name__ == "__main__":
    unittest.main()
