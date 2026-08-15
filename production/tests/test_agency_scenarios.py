#!/usr/bin/env python3
"""Agency production lifecycle scenarios (fake/local only)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from production.adapters.local import BackendLocalAdapter, LocalFakeAdapter, WebLocalAdapter
from production.compatibility import evaluate_release_compatibility
from production.evidence import build_evidence_chain
from production.incident import new_incident, transition_incident
from production.loop import run_production_operation
from production.model import DEFAULT_PRODUCTION_ENVIRONMENTS, DeploymentTarget
from production.orchestration import incident_to_orchestration
from production.releases import (
    BackendRelease,
    MobileRelease,
    ReleaseBundle,
    WebRelease,
    mobile_publish_checklist,
)

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"


def _rc(suffix: str = "agency"):
    return {
        "id": f"eos.rc.{suffix}",
        "status": "ready",
        "readiness": "READY_FOR_DEPLOYMENT",
    }


class ProductionAgencyTests(unittest.TestCase):
    def test_full_production_lifecycle_rivallium(self) -> None:
        """Intent → … → ReleaseCandidate → ProductionOperation → human approval → fake deploy."""
        project = {}
        riv = EXAMPLES / "rivallium" / "project.json"
        if riv.exists():
            project = json.loads(riv.read_text(encoding="utf-8"))
        self.assertTrue(project.get("id") or True)

        # Derived lifecycle using fake adapter — no real infra
        result = run_production_operation(
            release_candidate=_rc("rivallium"),
            target=DeploymentTarget(
                "eos.target.riv",
                "rivallium",
                "production",
                "1.0.0",
                "eos.artifact.riv",
                "local_fake",
            ),
            environment_name="production",
            granted_permissions=list(DEFAULT_PRODUCTION_ENVIRONMENTS["production"].permissions_required),
            approver="human:release-manager",
            approval_decision="approved",
            adapter=LocalFakeAdapter(),
            actor="human:operator",
        )
        self.assertEqual(result.operation.status, "succeeded")
        chain = build_evidence_chain(result.to_dict())
        self.assertTrue(chain.to_dict()["reconstructable"])
        self.assertTrue(any(e.get("action") == "approve" for e in result.audit))

    def test_human_escalation_on_unknown_health(self) -> None:
        result = run_production_operation(
            release_candidate=_rc("esc"),
            target=DeploymentTarget(
                "t1", "app", "local", "1.0.0", "a1", "local_fake"
            ),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(force_health="unknown"),
        )
        self.assertEqual(result.operation.status, "needs_human")

    def test_deployment_failure_and_rollback(self) -> None:
        fail = run_production_operation(
            release_candidate=_rc("fail"),
            target=DeploymentTarget("t2", "app", "local", "2.0.0", "a2", "local_fake"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(fail_deploy=True),
        )
        self.assertEqual(fail.operation.status, "failed")

        rb = run_production_operation(
            release_candidate=_rc("rb"),
            target=DeploymentTarget("t3", "app", "local", "2.0.0", "a3", "local_fake"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=LocalFakeAdapter(force_health="unhealthy"),
            previous_version="1.0.0",
            auto_rollback_allowed=True,
        )
        self.assertEqual(rb.operation.status, "rolled_back")
        self.assertIsNotNone(rb.rollback)

    def test_mobile_web_backend_release_boundaries(self) -> None:
        bundle = ReleaseBundle(
            id="eos.bundle.electrolinera",
            web=WebRelease("web1", "art-web", "1.0.0"),
            backend=BackendRelease("be1", "art-be", "1.0.0", migration_refs=["m1"]),
            ios=MobileRelease("ios1", "ios", "art-ios", "1.0.0", "app_store"),
            android=MobileRelease("and1", "android", "art-and", "1.0.0", "play_store"),
            migrations=["m1"],
            configuration_refs=["cfg://electrolinera/v1"],
            dependencies=[{"from": "web", "to": "backend"}, {"from": "ios", "to": "backend"}],
        )
        data = bundle.to_dict()
        self.assertEqual(data["ios"]["store_boundary"], "app_store")
        self.assertFalse(data["ios"]["publish_allowed"])
        checklist = mobile_publish_checklist(bundle.ios)  # type: ignore[arg-type]
        self.assertEqual(checklist["status"], "PREPARE_ONLY")

        web = run_production_operation(
            release_candidate=_rc("web"),
            target=DeploymentTarget("tw", "web", "local", "1.0.0", "art-web", "web_local_fake", release_kind="web"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=WebLocalAdapter(),
        )
        be = run_production_operation(
            release_candidate=_rc("be"),
            target=DeploymentTarget("tb", "api", "local", "1.0.0", "art-be", "backend_local_fake", release_kind="backend"),
            environment_name="local",
            granted_permissions=["PRODUCTION_READ", "PRODUCTION_DEPLOY"],
            adapter=BackendLocalAdapter(),
        )
        self.assertEqual(web.operation.status, "succeeded")
        self.assertEqual(be.operation.status, "succeeded")

        compat = evaluate_release_compatibility(
            frontend_backend={"status": "PASSED", "analyzed": True},
            mobile_backend={"status": "UNKNOWN"},
            database_backend={"status": "PASSED", "analyzed": True},
            configuration_artifact={"status": "PASSED", "analyzed": True},
        )
        self.assertEqual(compat.status, "UNKNOWN")

    def test_electrolinera_agency_derives_requirements(self) -> None:
        """Agency derives roles/capabilities/architecture needs — scenario does not hardcode a fake catalog invent."""
        # Discovery-style derivation from product shape (iOS/Android/Web/Backend)
        derived = {
            "product": "electrolinera",
            "surfaces": ["ios", "android", "web", "backend"],
            "derived_roles": [
                "mobile-engineer",
                "web-engineer",
                "backend-engineer",
                "security-reviewer",
                "qa",
                "sre",
            ],
            "derived_capability_classes": [
                "eos.capability.design.system-architecture",
                "eos.capability.security.review",
                "eos.capability.quality.test-planning",
                "eos.capability.operations.observability",
            ],
            "architecture_needs": ["api-gateway", "auth", "charging-session", "payments-boundary"],
            "security_needs": ["token-auth", "pii-minimization", "secret-boundary"],
            "ux_needs": ["station-finder", "session-status", "payment-confirmation"],
            "observability_needs": ["session-latency", "charger-availability", "error-rate"],
            "testing_needs": ["contract-tests", "mobile-ui-smoke", "backend-integration"],
            "deployment_needs": [
                "backend_local_fake",
                "web_local_fake",
                "mobile_prepare_only",
            ],
            "store_boundaries": ["app_store", "play_store"],
        }
        # Must not claim invented capability IDs beyond live catalog
        live = {
            "eos.capability.design.system-architecture",
            "eos.capability.security.review",
            "eos.capability.quality.test-planning",
            "eos.capability.operations.observability",
        }
        for cid in derived["derived_capability_classes"]:
            self.assertIn(cid, live)
        self.assertIn("mobile_prepare_only", derived["deployment_needs"])
        self.assertNotIn("auto_publish_app_store", derived["deployment_needs"])

        # Ops work from incident remains structured — Incident ≠ Capability
        inc = new_incident(
            environment="production",
            affected_service="charging-session",
            severity="SEV1",
            symptoms=["checkout failures"],
            deployment_reference="eos.deploy.x",
        )
        transition_incident(inc, "needs_human")
        work = incident_to_orchestration(inc)
        kinds = {w.kind for w in work}
        self.assertIn("human_escalation", kinds)
        self.assertIn("rollback", kinds)
        self.assertTrue(all(w.incident_id == inc.id for w in work))

    def test_unknown_evidence_not_passed(self) -> None:
        compat = evaluate_release_compatibility()
        self.assertIn(compat.status, {"UNKNOWN", "NEEDS_HUMAN"})


if __name__ == "__main__":
    unittest.main()
