#!/usr/bin/env python3
"""Unit tests for Production Operations core (Tasks 2–12+)."""

from __future__ import annotations

import unittest

from production.adapters.local import BackendLocalAdapter, LocalFakeAdapter, WebLocalAdapter
from production.approval import is_human_approver, record_production_approval
from production.compatibility import evaluate_api_compatibility, evaluate_release_compatibility
from production.evidence import build_evidence_chain
from production.failures import make_failure
from production.gates import production_operation_allowed
from production.health import aggregate_health, health_allows_success
from production.impact import assess_change_impact
from production.incident import alert_to_incident, new_incident, transition_incident, Alert
from production.loop import run_production_operation
from production.migrations import evaluate_migration
from production.model import DEFAULT_PRODUCTION_ENVIRONMENTS, DeploymentTarget
from production.permissions import PROFILES, authorize
from production.readiness import evaluate_pre_deploy
from production.releases import MobileRelease, ReleaseBundle, BackendRelease, WebRelease, mobile_publish_checklist
from production.rollback import execute_rollback, rollback_policy_decision
from production.secrets import assert_no_secrets, looks_like_secret, scrub_evidence
from production.states import assert_transition, can_transition, mark_succeeded_allowed
from production.strategy import select_strategy
from production.verification import verify_deployment


def _rc(**kwargs):
    base = {
        "id": "eos.rc.test1",
        "status": "ready",
        "readiness": "READY_FOR_DEPLOYMENT",
    }
    base.update(kwargs)
    return base


def _target(env="local", **kwargs):
    base = dict(
        id="eos.target.1",
        application="demo",
        environment=env,
        version="1.0.0",
        artifact_id="eos.artifact.1",
        adapter="local_fake",
    )
    base.update(kwargs)
    return DeploymentTarget(**base)


class StateMachineTests(unittest.TestCase):
    def test_forbidden_transitions(self) -> None:
        self.assertFalse(can_transition("failed", "succeeded"))
        self.assertFalse(can_transition("deploying", "succeeded"))
        self.assertFalse(can_transition("planned", "succeeded"))
        with self.assertRaises(ValueError):
            assert_transition("deploying", "succeeded")

    def test_unknown_not_success(self) -> None:
        self.assertFalse(mark_succeeded_allowed(health="unknown"))
        self.assertFalse(mark_succeeded_allowed(health="degraded"))
        self.assertTrue(mark_succeeded_allowed(health="healthy"))


class EnvironmentTests(unittest.TestCase):
    def test_production_is_critical(self) -> None:
        prod = DEFAULT_PRODUCTION_ENVIRONMENTS["production"]
        self.assertEqual(prod.risk, "critical")
        self.assertEqual(prod.approval_policy, "human_required")
        self.assertEqual(prod.rollback_policy, "human_required")


class ApprovalTests(unittest.TestCase):
    def test_agent_cannot_approve(self) -> None:
        self.assertFalse(is_human_approver("agent:deployer"))
        self.assertFalse(is_human_approver("skill:ops"))
        self.assertFalse(is_human_approver("orchestrator"))
        self.assertTrue(is_human_approver("human:alice"))
        with self.assertRaises(PermissionError):
            record_production_approval(
                approval_id="a1",
                release_candidate_id="rc1",
                environment="production",
                scope="deploy",
                decision="approved",
                approver="agent:bot",
            )


class PermissionTests(unittest.TestCase):
    def test_deny_by_default(self) -> None:
        d = authorize([], ["PRODUCTION_DEPLOY"])
        self.assertFalse(d.allowed)
        self.assertEqual(PROFILES["agent"], frozenset({"PRODUCTION_READ"}))


class HealthTests(unittest.TestCase):
    def test_aggregate_unknown(self) -> None:
        self.assertEqual(aggregate_health([None]), "unknown")
        self.assertEqual(aggregate_health(["healthy", "unknown"]), "unknown")
        self.assertFalse(health_allows_success("unknown"))


class LoopTests(unittest.TestCase):
    def test_local_success(self) -> None:
        result = run_production_operation(
            release_candidate=_rc(),
            target=_target("local"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(),
        )
        self.assertEqual(result.operation.status, "succeeded")
        self.assertEqual(result.operation.health_status, "healthy")
        self.assertTrue(result.audit)

    def test_production_blocks_without_human(self) -> None:
        result = run_production_operation(
            release_candidate=_rc(),
            target=_target("production"),
            environment_name="production",
            granted_permissions=list(DEFAULT_PRODUCTION_ENVIRONMENTS["production"].permissions_required),
            approver="agent:bot",
            approval_decision="approved",
        )
        self.assertEqual(result.operation.status, "awaiting_approval")
        self.assertIn("HUMAN_APPROVAL_REQUIRED", result.operation.notes)

    def test_production_succeeds_with_human(self) -> None:
        result = run_production_operation(
            release_candidate=_rc(),
            target=_target("production"),
            environment_name="production",
            granted_permissions=list(DEFAULT_PRODUCTION_ENVIRONMENTS["production"].permissions_required),
            approver="human:alice",
            approval_decision="approved",
            adapter=LocalFakeAdapter(),
        )
        self.assertEqual(result.operation.status, "succeeded")

    def test_health_failure_not_succeeded(self) -> None:
        result = run_production_operation(
            release_candidate=_rc(),
            target=_target("local"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(force_health="unhealthy"),
            previous_version="0.9.0",
            auto_rollback_allowed=True,
        )
        self.assertNotEqual(result.operation.status, "succeeded")
        self.assertIn(result.operation.status, {"rolled_back", "needs_human", "rollback_required"})

    def test_dry_run(self) -> None:
        result = run_production_operation(
            release_candidate=_rc(),
            target=_target("production"),
            environment_name="production",
            granted_permissions=list(DEFAULT_PRODUCTION_ENVIRONMENTS["production"].permissions_required),
            dry_run=True,
            adapter=LocalFakeAdapter(),
        )
        self.assertEqual(result.operation.status, "succeeded")
        self.assertTrue(any("dry-run" in n for n in result.operation.notes))

    def test_unknown_health_needs_human(self) -> None:
        result = run_production_operation(
            release_candidate=_rc(),
            target=_target("local"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(force_health="unknown"),
        )
        self.assertEqual(result.operation.status, "needs_human")
        self.assertNotEqual(result.verification.get("decision"), "succeeded")


class SecretTests(unittest.TestCase):
    def test_secret_detection(self) -> None:
        self.assertTrue(looks_like_secret("api_key=supersecret"))
        with self.assertRaises(ValueError):
            assert_no_secrets({"msg": "password: hunter2"})
        cleaned = scrub_evidence([{"kind": "x", "token": "Bearer abc.def"}])
        self.assertEqual(cleaned[0]["kind"], "redacted")


class IncidentTests(unittest.TestCase):
    def test_resolve_requires_evidence(self) -> None:
        inc = new_incident(environment="production", affected_service="api", severity="SEV1")
        transition_incident(inc, "triaging")
        transition_incident(inc, "mitigating")
        transition_incident(inc, "monitoring")
        with self.assertRaises(ValueError):
            transition_incident(inc, "resolved")
        inc.resolution = "fixed"
        inc.evidence.append({"kind": "fix"})
        transition_incident(inc, "resolved")
        alert = Alert("a1", "latency", "SEV2", "production")
        promoted = alert_to_incident(alert, service="api")
        self.assertEqual(alert.status, "promoted_incident")
        self.assertEqual(promoted.source, "alert")


class CompatibilityTests(unittest.TestCase):
    def test_missing_evidence_unknown(self) -> None:
        self.assertEqual(evaluate_api_compatibility(None).status, "UNKNOWN")
        r = evaluate_release_compatibility()
        self.assertIn(r.status, {"UNKNOWN", "NEEDS_HUMAN"})


class MigrationTests(unittest.TestCase):
    def test_destructive_production_human(self) -> None:
        d = evaluate_migration(classification="destructive", environment="production")
        self.assertTrue(d.human_required)
        self.assertFalse(d.deploy_allowed)


class ImpactTests(unittest.TestCase):
    def test_missing_is_unknown(self) -> None:
        self.assertEqual(assess_change_impact(None).level, "unknown")


class StrategyTests(unittest.TestCase):
    def test_high_risk_not_full(self) -> None:
        s = select_strategy(risk="critical", environment="production")
        self.assertIn(s["strategy"], {"canary", "staged"})
        self.assertTrue(s["human_approval"])


class ReleaseBoundaryTests(unittest.TestCase):
    def test_mobile_no_auto_publish(self) -> None:
        ios = MobileRelease("ios1", "ios", "art1", "1.0", "app_store")
        checklist = mobile_publish_checklist(ios)
        self.assertFalse(ios.publish_allowed)
        self.assertEqual(checklist["auto_publish"], False)
        bundle = ReleaseBundle(
            "b1",
            web=WebRelease("w1", "wa", "1.0"),
            backend=BackendRelease("be1", "ba", "1.0"),
            ios=ios,
        )
        self.assertEqual(bundle.to_dict()["kind"], "bundle")


class AdapterTests(unittest.TestCase):
    def test_web_backend_adapters(self) -> None:
        self.assertEqual(WebLocalAdapter().name, "web_local_fake")
        self.assertEqual(BackendLocalAdapter().name, "backend_local_fake")


class FailureAndGateTests(unittest.TestCase):
    def test_rollback_failure_human(self) -> None:
        f = make_failure("ROLLBACK_FAILED")
        self.assertEqual(f.retry_class, "human_required")

    def test_safety_gate(self) -> None:
        denied = production_operation_allowed(
            environment="production",
            granted_permissions=["PRODUCTION_READ"],
            required_permissions=["PRODUCTION_DEPLOY"],
            approval_decision="approved",
            approver="human:x",
            readiness_ready=True,
            release_candidate_id="rc1",
        )
        self.assertFalse(denied.allowed)


class EvidenceChainTests(unittest.TestCase):
    def test_chain(self) -> None:
        result = run_production_operation(
            release_candidate=_rc(),
            target=_target("local"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
        )
        chain = build_evidence_chain(result.to_dict())
        self.assertTrue(chain.to_dict()["reconstructable"])


class RollbackPolicyTests(unittest.TestCase):
    def test_human_default(self) -> None:
        self.assertEqual(
            rollback_policy_decision(
                environment_policy="human_required",
                health="unhealthy",
                auto_rollback_allowed=False,
            ),
            "human_required",
        )
        adapter = LocalFakeAdapter()
        # seed deploy
        from production.adapters.base import AdapterRequest

        req = AdapterRequest("op", {"version": "1.0"}, "local", "art")
        adapter.deploy(req)
        rb = execute_rollback(
            adapter,
            operation_id="op",
            target={"version": "1.1"},
            environment="local",
            artifact_id="art",
            from_version="1.1",
            to_version="1.0",
            reason="test",
            policy="human_required",
            authorized_by=None,
        )
        self.assertEqual(rb.status, "needs_human")


class ReadinessTests(unittest.TestCase):
    def test_unknown_tests_block(self) -> None:
        r = evaluate_pre_deploy(
            release_candidate=_rc(),
            artifact_exists=True,
            tests_status="UNKNOWN",
            security_status="PASSED",
            gates_passed=True,
            evidence_complete=True,
            environment=DEFAULT_PRODUCTION_ENVIRONMENTS["local"].to_dict(),
            permissions_ok=True,
            approval_satisfied=True,
            rollback_strategy=True,
            health_checks_defined=True,
        )
        self.assertFalse(r.ready)


class VerificationTests(unittest.TestCase):
    def test_unknown_verification(self) -> None:
        v = verify_deployment(deployment_id="d1", health="unknown")
        self.assertEqual(v.decision, "needs_human")


if __name__ == "__main__":
    unittest.main()
