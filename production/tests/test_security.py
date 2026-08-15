#!/usr/bin/env python3
"""Security attack scenarios — all must fail-closed."""

from __future__ import annotations

import unittest

from production.adapters.local import LocalFakeAdapter
from production.approval import record_production_approval
from production.gates import production_operation_allowed
from production.loop import run_production_operation
from production.model import DEFAULT_PRODUCTION_ENVIRONMENTS, DeploymentTarget
from production.permissions import authorize
from production.secrets import assert_no_secrets, scrub_evidence


def _rc():
    return {"id": "eos.rc.sec1", "status": "ready", "readiness": "READY_FOR_DEPLOYMENT"}


def _target(env="production"):
    return DeploymentTarget(
        id="eos.target.sec",
        application="app",
        environment=env,
        version="2.0.0",
        artifact_id="eos.artifact.sec",
        adapter="local_fake",
    )


PROD_PERMS = list(DEFAULT_PRODUCTION_ENVIRONMENTS["production"].permissions_required)


class SecurityAttackTests(unittest.TestCase):
    def test_privilege_escalation_denied(self) -> None:
        d = authorize(["PRODUCTION_READ"], ["PRODUCTION_DEPLOY"])
        self.assertFalse(d.allowed)

    def test_production_without_approval(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target(),
            environment_name="production",
            granted_permissions=PROD_PERMS,
        )
        self.assertEqual(r.operation.status, "awaiting_approval")

    def test_agent_self_approval_fails(self) -> None:
        with self.assertRaises(PermissionError):
            record_production_approval(
                approval_id="a",
                release_candidate_id="rc",
                environment="production",
                scope="deploy",
                decision="approved",
                approver="agent:same",
            )
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target(),
            environment_name="production",
            granted_permissions=PROD_PERMS,
            approver="agent:deployer",
            approval_decision="approved",
            actor="agent:deployer",
        )
        self.assertEqual(r.operation.status, "awaiting_approval")

    def test_skill_cannot_approve(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target(),
            environment_name="production",
            granted_permissions=PROD_PERMS,
            approver="skill:ops",
            approval_decision="approved",
        )
        self.assertEqual(r.operation.status, "awaiting_approval")

    def test_orchestrator_cannot_approve(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target(),
            environment_name="production",
            granted_permissions=PROD_PERMS,
            approver="orchestrator",
            approval_decision="approved",
        )
        self.assertEqual(r.operation.status, "awaiting_approval")

    def test_secret_leakage_blocked(self) -> None:
        with self.assertRaises(ValueError):
            assert_no_secrets({"log": "api_key=abcd1234"})
        cleaned = scrub_evidence([{"msg": "password: x"}])
        self.assertEqual(cleaned[0]["kind"], "redacted")

    def test_wrong_environment_blocked(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target("production"),
            environment_name="not-a-real-env",
            granted_permissions=PROD_PERMS,
            approver="human:alice",
            approval_decision="approved",
        )
        self.assertEqual(r.operation.status, "failed")

    def test_artifact_substitution_fails_validate(self) -> None:
        t = _target("local")
        t.artifact_id = ""
        r = run_production_operation(
            release_candidate=_rc(),
            target=t,
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(),
        )
        self.assertEqual(r.operation.status, "failed")

    def test_rollback_to_unknown_version_fails(self) -> None:
        from production.adapters.base import AdapterRequest
        from production.rollback import execute_rollback

        adapter = LocalFakeAdapter()
        adapter.deploy(AdapterRequest("op", {"version": "1"}, "local", "art"))
        rb = execute_rollback(
            adapter,
            operation_id="op",
            target={"version": "2"},
            environment="local",
            artifact_id="art",
            from_version="2",
            to_version="",
            reason="bad",
            policy="auto_allowed",
            authorized_by="policy:auto",
        )
        self.assertEqual(rb.status, "failed")

    def test_health_spoofing_unknown_not_success(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target("local"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(force_health="unknown"),
        )
        self.assertNotEqual(r.operation.status, "succeeded")

    def test_evidence_spoofing_does_not_bypass_gate(self) -> None:
        gate = production_operation_allowed(
            environment="production",
            granted_permissions=PROD_PERMS,
            required_permissions=PROD_PERMS,
            approval_decision="approved",
            approver="agent:spoof",
            readiness_ready=True,
            release_candidate_id="rc",
            policy_evidence=[{"kind": "fake", "approved": True}],
        )
        self.assertFalse(gate.allowed)

    def test_permission_bypass_denied(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target("production"),
            environment_name="production",
            granted_permissions=[],  # empty — deny by default
            approver="human:alice",
            approval_decision="approved",
        )
        self.assertIn(r.operation.status, {"awaiting_approval", "failed"})
        self.assertFalse(r.readiness.get("ready", True))


class FailureScenarioTests(unittest.TestCase):
    def test_deployment_success(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target("local"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
        )
        self.assertEqual(r.operation.status, "succeeded")

    def test_deployment_failure(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target("local"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(fail_deploy=True),
        )
        self.assertEqual(r.operation.status, "failed")

    def test_health_failure(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target("local"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(force_health="unhealthy"),
        )
        self.assertNotEqual(r.operation.status, "succeeded")

    def test_automatic_rollback_allowed(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target("local"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(force_health="unhealthy"),
            previous_version="1.0.0",
            auto_rollback_allowed=True,
        )
        self.assertEqual(r.operation.status, "rolled_back")

    def test_rollback_requires_human(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target("staging"),
            environment_name="staging",
            granted_permissions=list(DEFAULT_PRODUCTION_ENVIRONMENTS["staging"].permissions_required),
            approver="human:bob",
            approval_decision="approved",
            adapter=LocalFakeAdapter(force_health="unhealthy"),
            previous_version="1.0.0",
            auto_rollback_allowed=False,
        )
        self.assertEqual(r.operation.status, "needs_human")

    def test_approval_missing(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target("production"),
            environment_name="production",
            granted_permissions=PROD_PERMS,
        )
        self.assertEqual(r.operation.status, "awaiting_approval")

    def test_secret_leakage_attempt(self) -> None:
        with self.assertRaises(ValueError):
            assert_no_secrets("token: Bearer aaa.bbb")

    def test_unknown_health(self) -> None:
        r = run_production_operation(
            release_candidate=_rc(),
            target=_target("local"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(force_health="unknown"),
        )
        self.assertEqual(r.operation.status, "needs_human")


if __name__ == "__main__":
    unittest.main()
