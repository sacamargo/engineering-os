#!/usr/bin/env python3
"""Phase 6 agency/security scenarios."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from agents.coding import DeterministicPlan
from agents.loop import run_execution
from agents.model import AgentDefinition, instantiate
from codebase.analyze import analyze_repository
from orchestration.facade import PlanningOrchestrator

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "codebase" / "fixtures"


class AgencyScenarioTests(unittest.TestCase):
    def test_bugfix_before_after(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "calc.py").write_text("def div(a, b):\n    return a + b\n", encoding="utf-8")
            (root / "test_calc.py").write_text(
                "import unittest\nfrom calc import div\n\n"
                "class T(unittest.TestCase):\n"
                "    def test_div(self):\n"
                "        self.assertEqual(div(6, 3), 2)\n",
                encoding="utf-8",
            )
            # Prove failure first
            fail_plan = DeterministicPlan(
                steps=[{"tool": "run_tests", "arguments": {"command": "python3 -m unittest test_calc"}}]
            )
            fail = run_execution(
                root,
                {"id": "eos.task.bug.prove", "title": "Prove failing test", "task_kind": "coding"},
                fail_plan,
                require_tests=True,
                auto_rollback_on_failure=False,
            )
            self.assertEqual(fail.status, "FAILED")

            fix_plan = DeterministicPlan(
                steps=[
                    {"tool": "read_file", "arguments": {"path": "calc.py"}},
                    {
                        "tool": "write_file",
                        "arguments": {
                            "path": "calc.py",
                            "content": "def div(a, b):\n    return a / b\n",
                        },
                    },
                    {"tool": "run_tests", "arguments": {"command": "python3 -m unittest test_calc"}},
                ]
            )
            ok = run_execution(
                root,
                {"id": "eos.task.bug.fix", "title": "Fix div bug", "task_kind": "bugfix", "target_paths": ["calc.py"]},
                fix_plan,
            )
            self.assertEqual(ok.status, "SUCCESS")
            self.assertTrue(ok.changeset)

    def test_rivallium_small_change(self) -> None:
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
            result = run_execution(
                dest,
                {
                    "id": "eos.task.rivallium.validate-booking",
                    "title": "Add booking validation",
                    "task_kind": "coding",
                    "target_paths": ["services/booking.py"],
                },
                plan,
            )
            self.assertEqual(result.status, "SUCCESS", msg=result.to_dict())

    def test_legacy_requires_analysis_first(self) -> None:
        snap = analyze_repository(FIXTURES / "legacy-chaos")
        self.assertTrue(snap.snapshot.findings)
        orch = PlanningOrchestrator(ROOT)
        plan = orch.plan("Quiero refactorizar este sistema legado.").to_dict()
        self.assertTrue(any(t.get("task_kind") == "codebase_analysis" for t in plan["generated"]["tasks"]))
        self.assertNotEqual(plan["codebase"].get("analysis_status"), "complete")
        # Agent without plan/context → NEEDS_INPUT
        result = run_execution(
            FIXTURES / "legacy-chaos",
            {"id": "eos.task.legacy.refactor", "title": "Refactor legacy", "task_kind": "coding"},
            None,
        )
        self.assertEqual(result.status, "NEEDS_INPUT")

    def test_padel_human_escalation(self) -> None:
        orch = PlanningOrchestrator(ROOT)
        plan = orch.plan(
            "Automatiza cancha de pádel con iluminación eléctrica y control de acceso físico."
        ).to_dict()
        self.assertIn(plan["readiness"]["status"], {"needs_human", "partially_ready"})
        result = run_execution(
            FIXTURES / "padel-iot-mini",
            {
                "id": "eos.task.padel.electrical",
                "title": "Install electrical circuits",
                "requires_professional_approval": True,
            },
            None,
        )
        self.assertEqual(result.status, "NEEDS_HUMAN")

    def test_agency_analyze_and_fix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "mod.py").write_text("def value():\n    return 1\n", encoding="utf-8")
            (root / "test_mod.py").write_text(
                "import unittest\nfrom mod import value\n\n"
                "class T(unittest.TestCase):\n"
                "    def test_value(self):\n"
                "        self.assertEqual(value(), 2)\n",
                encoding="utf-8",
            )
            analysis = analyze_repository(root)
            self.assertTrue(analysis.snapshot.id)
            plan = DeterministicPlan(
                steps=[
                    {"tool": "search_code", "arguments": {"pattern": "def value"}},
                    {
                        "tool": "write_file",
                        "arguments": {"path": "mod.py", "content": "def value():\n    return 2\n"},
                    },
                    {"tool": "run_tests", "arguments": {"command": "python3 -m unittest test_mod"}},
                ]
            )
            result = run_execution(
                root,
                {
                    "id": "eos.task.agency.fix",
                    "title": "Analyze and fix bug",
                    "task_kind": "bugfix",
                    "target_paths": ["mod.py"],
                },
                plan,
                codebase_snapshot_id=analysis.snapshot.id,
            )
            self.assertEqual(result.status, "SUCCESS")
            self.assertTrue(any(e.get("kind") == "context" for e in result.evidence))

    def test_agency_unresolvable_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "x.py").write_text("def f():\n    return 1\n", encoding="utf-8")
            (root / "test_x.py").write_text(
                "import unittest\nfrom x import f\n\n"
                "class T(unittest.TestCase):\n"
                "    def test_f(self):\n"
                "        self.assertEqual(f(), 999)\n",
                encoding="utf-8",
            )
            plan = DeterministicPlan(
                steps=[
                    {
                        "tool": "write_file",
                        "arguments": {"path": "x.py", "content": "def f():\n    return 1\n"},
                    },
                    {"tool": "run_tests", "arguments": {"command": "python3 -m unittest test_x"}},
                ]
            )
            result = run_execution(
                root,
                {"id": "eos.task.agency.fail", "title": "Fix impossible assertion", "task_kind": "bugfix"},
                plan,
            )
            self.assertIn(result.status, {"FAILED", "REPLAN", "NEEDS_HUMAN"})
            self.assertNotEqual(result.status, "SUCCESS")

    def test_no_god_agent(self) -> None:
        with self.assertRaises(ValueError):
            instantiate(
                AgentDefinition(
                    id="eos.agent.god",
                    type="coding",
                    permissions=["READ", "WRITE", "EXECUTE", "NETWORK", "GIT", "DEPLOY"],
                    authorized_tools=["read_file"],
                    risk_ceiling="CRITICAL",
                )
            )

    def test_security_path_and_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env").write_text("SECRET=1\n", encoding="utf-8")
            plan = DeterministicPlan(
                steps=[
                    {"tool": "read_file", "arguments": {"path": "../etc/passwd"}},
                    {"tool": "write_file", "arguments": {"path": ".env", "content": "x"}},
                ]
            )
            result = run_execution(
                root,
                {"id": "eos.task.sec", "title": "Attack sandbox", "task_kind": "coding"},
                plan,
                require_tests=False,
            )
            self.assertNotEqual(result.status, "SUCCESS")


if __name__ == "__main__":
    unittest.main()
