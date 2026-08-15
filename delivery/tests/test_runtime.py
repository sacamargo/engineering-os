#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from delivery.deployment import NullDeploymentAdapter, DeploymentRequest
from delivery.gates import evaluate_delivery_gates
from delivery.loop import run_delivery
from delivery.model import DeliveryArtifact, ValidationRun
from delivery.permissions import authorize
from delivery.rollback import plan_rollback
from delivery.risk import classify_change_risk


class DeliveryRuntimeTests(unittest.TestCase):
    def _workspace_with_passing_tests(self, root: Path) -> None:
        (root / "app.py").write_text("def ok():\n    return 1\n", encoding="utf-8")
        (root / "test_app.py").write_text(
            "import unittest\nfrom app import ok\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertEqual(ok(), 1)\n",
            encoding="utf-8",
        )

    def test_end_to_end_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._workspace_with_passing_tests(root)
            result = run_delivery(
                root,
                test_command="python3 -m unittest test_app",
                force_security_status="clear",
                skip_codebase_analysis=True,
            )
            self.assertIn(result.readiness, {"READY_FOR_RELEASE", "READY_FOR_DEPLOYMENT"})
            self.assertTrue(result.artifacts)
            self.assertTrue(result.artifacts[0].get("digest"))
            self.assertEqual(result.deployment_boundary.get("status"), "READY_FOR_DEPLOYMENT")

    def test_zero_tests_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text("x=1\n", encoding="utf-8")
            (root / "test_empty.py").write_text("import unittest\n\nclass T(unittest.TestCase):\n    pass\n", encoding="utf-8")
            result = run_delivery(
                root,
                test_command="python3 -m unittest test_empty",
                force_security_status="clear",
                skip_codebase_analysis=True,
            )
            self.assertIn(result.readiness, {"BLOCKED", "NEEDS_HUMAN"})
            self.assertNotIn(result.readiness, {"READY_FOR_RELEASE", "READY_FOR_DEPLOYMENT"})

    def test_security_unknown_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._workspace_with_passing_tests(root)
            result = run_delivery(
                root,
                test_command="python3 -m unittest test_app",
                force_security_status="unknown",
                skip_codebase_analysis=True,
            )
            self.assertEqual(result.readiness, "BLOCKED")

    def test_production_needs_human(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._workspace_with_passing_tests(root)
            result = run_delivery(
                root,
                environment="production",
                test_command="python3 -m unittest test_app",
                force_security_status="clear",
                skip_codebase_analysis=True,
                approval_granted=False,
            )
            self.assertEqual(result.readiness, "NEEDS_HUMAN")

    def test_analysis_profile_denied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_delivery(tmp, actor_profile="analysis", skip_codebase_analysis=True)
            self.assertEqual(result.status, "failed")

    def test_deploy_adapter_unsupported(self) -> None:
        r = NullDeploymentAdapter().deploy(DeploymentRequest("rc1", "production", ["a"]))
        self.assertEqual(r.status, "UNSUPPORTED")

    def test_risk_classification(self) -> None:
        self.assertEqual(classify_change_risk(["web/ui.css"]), "low")
        self.assertIn(classify_change_risk(["services/booking.py"]), {"medium", "high"})
        self.assertEqual(classify_change_risk(["auth/login.py"], environment="production"), "critical")

    def test_gate_not_run_not_passed(self) -> None:
        gates = evaluate_delivery_gates(
            validations=[ValidationRun(id="v1", kind="unit", status="NOT_RUN")],
            artifacts=[],
            security_status="clear",
            approval_granted=True,
            environment="local",
        )
        by = {g.gate_id: g for g in gates}
        self.assertFalse(by["tests"].passed)
        self.assertFalse(by["artifact"].passed)

    def test_rollback_model(self) -> None:
        plan = plan_rollback(from_release="B", to_release="A", reason="B failed", authorized_by="human:release")
        self.assertEqual(plan.status, "authorized")
        self.assertTrue(plan.evidence)

    def test_release_approve_permission(self) -> None:
        self.assertFalse(authorize(["DELIVERY_READ"], ["RELEASE_APPROVE"]).allowed)


if __name__ == "__main__":
    unittest.main()
