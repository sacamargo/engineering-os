#!/usr/bin/env python3
"""Agency / security / cross-domain delivery scenarios."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from agents.coding import DeterministicPlan
from agents.loop import run_execution
from delivery.deployment import NullDeploymentAdapter, DeploymentRequest
from delivery.loop import run_delivery
from delivery.rollback import plan_rollback
from orchestration.facade import PlanningOrchestrator

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "codebase" / "fixtures"


class DeliveryScenarioTests(unittest.TestCase):
    def test_rivallium_agent_then_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "riv"
            shutil.copytree(FIXTURES / "rivallium-mini", dest)
            plan = DeterministicPlan(
                steps=[
                    {"tool": "read_file", "arguments": {"path": "services/booking.py"}},
                    {
                        "tool": "write_file",
                        "arguments": {
                            "path": "services/booking.py",
                            "content": (
                                '"""Booking domain service."""\n\n'
                                "from api.repository import BookingRepository\n\n\n"
                                "def create_booking(user_id: str, court_id: str, slot: str) -> dict:\n"
                                "    if not user_id or not court_id or not slot:\n"
                                '        raise ValueError("invalid booking input")\n'
                                "    repo = BookingRepository()\n"
                                '    return repo.save({"user_id": user_id, "court_id": court_id, "slot": slot})\n\n\n'
                                "def cancel_booking(booking_id: str) -> bool:\n"
                                "    repo = BookingRepository()\n"
                                "    return repo.delete(booking_id)\n"
                            ),
                        },
                    },
                    {
                        "tool": "run_tests",
                        "arguments": {"command": "python3 -m unittest tests.test_booking"},
                    },
                ]
            )
            exec_result = run_execution(
                dest,
                {
                    "id": "eos.task.rivallium.booking-rule",
                    "title": "Add booking validation rule",
                    "task_kind": "coding",
                    "target_paths": ["services/booking.py"],
                },
                plan,
            )
            self.assertEqual(exec_result.status, "SUCCESS")
            delivery = run_delivery(
                dest,
                project_id="eos.project.rivallium",
                changeset_id=exec_result.changeset["id"] if exec_result.changeset else "eos.changeset.riv",
                changed_paths=["services/booking.py"],
                test_command="python3 -m unittest tests.test_booking",
                force_security_status="clear",
                skip_codebase_analysis=True,
            )
            self.assertIn(delivery.readiness, {"READY_FOR_RELEASE", "READY_FOR_DEPLOYMENT"})
            self.assertEqual(
                NullDeploymentAdapter().deploy(DeploymentRequest("rc", "production", [])).status,
                "UNSUPPORTED",
            )

    def test_padel_human_barrier(self) -> None:
        orch = PlanningOrchestrator(ROOT)
        plan = orch.plan(
            "Automatiza cancha de pádel con iluminación eléctrica y control de acceso físico."
        ).to_dict()
        self.assertIn(plan["readiness"]["status"], {"needs_human", "partially_ready"})
        delivery = run_delivery(
            FIXTURES / "padel-iot-mini",
            project_id="eos.project.padel",
            environment="staging",
            test_command="python3 -m unittest tests.test_gateway",
            force_security_status="clear",
            skip_codebase_analysis=True,
        )
        # software can progress; physical scopes remain escalated at planning layer
        self.assertTrue(plan["escalations"] or any(t.get("requires_professional_approval") for t in plan["generated"]["tasks"]))
        self.assertIn(delivery.readiness, {"READY_FOR_RELEASE", "READY_FOR_DEPLOYMENT", "BLOCKED", "NEEDS_HUMAN"})

    def test_agency_secure_testable_ready(self) -> None:
        orch = PlanningOrchestrator(ROOT)
        planning = orch.plan(
            "Implementa una nueva funcionalidad en Rivallium. Debe ser segura, testeable, observable y lista para release."
        ).to_dict()
        self.assertTrue(planning["generated"]["tasks"])
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "riv"
            shutil.copytree(FIXTURES / "rivallium-mini", dest)
            delivery = run_delivery(
                dest,
                project_id="eos.project.rivallium",
                changed_paths=["services/booking.py"],
                test_command="python3 -m unittest tests.test_booking",
                force_security_status="clear",
                skip_codebase_analysis=True,
            )
            self.assertIn(delivery.readiness, {"READY_FOR_RELEASE", "READY_FOR_DEPLOYMENT"})
            self.assertIsNotNone(delivery.release_candidate)

    def test_security_attacks_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text("def ok():\n    return 1\n", encoding="utf-8")
            (root / "test_app.py").write_text(
                "import unittest\nfrom app import ok\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertEqual(ok(), 1)\n",
                encoding="utf-8",
            )
            # fake success attempt: unknown security
            blocked = run_delivery(
                root,
                test_command="python3 -m unittest test_app",
                force_security_status="unknown",
                skip_codebase_analysis=True,
            )
            self.assertEqual(blocked.readiness, "BLOCKED")
            # self-approval production
            needs = run_delivery(
                root,
                environment="production",
                test_command="python3 -m unittest test_app",
                force_security_status="clear",
                skip_codebase_analysis=True,
                approval_granted=True,
                approver="agent:coding",
            )
            self.assertEqual(needs.readiness, "NEEDS_HUMAN")
            # analysis cannot deliver
            denied = run_delivery(root, actor_profile="analysis", skip_codebase_analysis=True)
            self.assertEqual(denied.status, "failed")

    def test_rollback_trace(self) -> None:
        plan = plan_rollback(from_release="eos.rc.B", to_release="eos.rc.A", reason="validation failed after release B")
        self.assertEqual(plan.from_release, "eos.rc.B")
        self.assertEqual(plan.to_release, "eos.rc.A")
        self.assertTrue(plan.evidence)


if __name__ == "__main__":
    unittest.main()
