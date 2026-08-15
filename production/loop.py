"""Production operation execution loop.

prepare → validate → approval → deploy → health → evidence → finalize
Deploy OK + unhealthy health ≠ succeeded.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from production.adapters.base import AdapterRequest
from production.adapters.local import LocalFakeAdapter
from production.approval import is_human_approver, record_production_approval
from production.audit import AuditTrail
from production.gates import production_operation_allowed
from production.health import aggregate_health
from production.model import (
    DEFAULT_PRODUCTION_ENVIRONMENTS,
    DeploymentRecord,
    DeploymentTarget,
    ProductionOperation,
    new_operation,
)
from production.permissions import authorize
from production.readiness import evaluate_pre_deploy
from production.rollback import execute_rollback, rollback_policy_decision
from production.secrets import assert_no_secrets, scrub_evidence
from production.states import assert_transition, mark_succeeded_allowed
from production.verification import verify_deployment


@dataclass
class OpsResult:
    operation: ProductionOperation
    deployment: DeploymentRecord | None = None
    readiness: dict[str, Any] = field(default_factory=dict)
    verification: dict[str, Any] = field(default_factory=dict)
    rollback: dict[str, Any] | None = None
    audit: list[dict[str, Any]] = field(default_factory=list)
    safety_gate: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation.to_dict(),
            "deployment": self.deployment.to_dict() if self.deployment else None,
            "readiness": self.readiness,
            "verification": self.verification,
            "rollback": self.rollback,
            "audit": self.audit,
            "safety_gate": self.safety_gate,
        }


def run_production_operation(
    *,
    release_candidate: dict[str, Any],
    target: DeploymentTarget,
    environment_name: str,
    granted_permissions: list[str],
    approver: str | None = None,
    approval_decision: str | None = None,
    dry_run: bool = False,
    adapter: Any | None = None,
    previous_version: str | None = None,
    auto_rollback_allowed: bool = False,
    tests_status: str = "PASSED",
    security_status: str = "PASSED",
    gates_passed: bool = True,
    evidence_complete: bool = True,
    artifact_exists: bool = True,
    actor: str = "human:operator",
    role: str = "deployer",
) -> OpsResult:
    env = DEFAULT_PRODUCTION_ENVIRONMENTS.get(environment_name)
    if not env:
        op = new_operation(
            release_candidate_id=str(release_candidate.get("id")),
            environment=environment_name,
            target_id=target.id,
            dry_run=dry_run,
        )
        assert_transition(op.status, "validating")
        op.status = "validating"
        assert_transition(op.status, "failed")
        op.status = "failed"
        op.notes.append("ENVIRONMENT_INVALID")
        return OpsResult(operation=op, readiness={"ready": False, "gaps": [{"code": "ENVIRONMENT_INVALID"}]})

    op = new_operation(
        release_candidate_id=str(release_candidate.get("id")),
        environment=environment_name,
        target_id=target.id,
        dry_run=dry_run,
    )
    trail = AuditTrail()
    trail.append(
        actor=actor,
        role=role,
        environment=environment_name,
        action="prepare",
        result="ok",
        release=op.release_candidate_id,
        evidence={"operation_id": op.id},
    )
    adapter = adapter or LocalFakeAdapter()

    # --- validate / readiness ---
    assert_transition(op.status, "validating")
    op.status = "validating"
    perms = authorize(granted_permissions, env.permissions_required)
    needs_human_approval = env.approval_policy == "human_required" and not dry_run
    approval_ok = True
    if needs_human_approval:
        approval_ok = bool(
            approval_decision == "approved" and approver and is_human_approver(approver)
        )

    readiness = evaluate_pre_deploy(
        release_candidate=release_candidate,
        artifact_exists=artifact_exists,
        tests_status=tests_status,
        security_status=security_status,
        gates_passed=gates_passed,
        evidence_complete=evidence_complete,
        environment=env.to_dict(),
        permissions_ok=perms.allowed,
        approval_satisfied=approval_ok if needs_human_approval else True,
        rollback_strategy=True,
        health_checks_defined=bool(env.health_checks),
    )
    op.gaps = [g.to_dict() for g in readiness.gaps]
    op.evidence.append({"kind": "pre_deploy_readiness", **readiness.to_dict()})
    trail.append(
        actor=actor,
        role=role,
        environment=environment_name,
        action="validate",
        result="ready" if readiness.ready else "gaps",
        evidence={"ready": readiness.ready, "gap_count": len(readiness.gaps)},
    )

    if needs_human_approval:
        assert_transition(op.status, "awaiting_approval")
        op.status = "awaiting_approval"
        if not approval_ok:
            op.notes.append("HUMAN_APPROVAL_REQUIRED")
            return OpsResult(
                operation=op,
                readiness=readiness.to_dict(),
                audit=trail.to_list(),
            )
        appr = record_production_approval(
            approval_id=f"eos.approval.{uuid.uuid4().hex[:10]}",
            release_candidate_id=op.release_candidate_id,
            environment=environment_name,
            scope="deploy",
            decision="approved",
            approver=approver or "",
        )
        op.approval_id = appr.id
        op.evidence.append(appr.to_dict())
        trail.append(
            actor=approver or "unknown",
            role="human_approver",
            environment=environment_name,
            action="approve",
            decision="approved",
            result="ok",
            release=op.release_candidate_id,
        )

    if not readiness.ready:
        # approval may have passed but other gaps remain
        if op.status == "validating":
            assert_transition(op.status, "failed")
        elif op.status == "awaiting_approval":
            assert_transition(op.status, "failed")
        op.status = "failed"
        op.notes.append("NO DEPLOY — readiness gaps")
        return OpsResult(operation=op, readiness=readiness.to_dict(), audit=trail.to_list())

    safety = production_operation_allowed(
        environment=environment_name,
        granted_permissions=granted_permissions,
        required_permissions=env.permissions_required,
        approval_decision=approval_decision if needs_human_approval else "n/a",
        approver=approver if needs_human_approval else "n/a",
        readiness_ready=True,
        release_candidate_id=op.release_candidate_id,
        dry_run=dry_run,
    )

    if not safety.allowed:
        op.notes.append("PRODUCTION_OPERATION_ALLOWED denied")
        assert_transition(op.status, "failed")
        op.status = "failed"
        return OpsResult(
            operation=op,
            readiness=readiness.to_dict(),
            audit=trail.to_list(),
            safety_gate=safety.to_dict(),
        )

    # --- deploy ---
    if op.status == "validating":
        # environments without approval go validating → deploying via awaiting_approval hop? 
        # State machine requires awaiting_approval before deploying. Use explicit hop.
        assert_transition(op.status, "awaiting_approval")
        op.status = "awaiting_approval"
        op.notes.append("approval_policy=none — auto-advance")
    assert_transition(op.status, "deploying")
    op.status = "deploying"

    dep = DeploymentRecord(
        id=f"eos.deploy.{uuid.uuid4().hex[:10]}",
        operation_id=op.id,
        target_id=target.id,
        adapter=getattr(adapter, "name", "unknown"),
        status="running",
        started_at=time.time(),
    )
    req = AdapterRequest(
        operation_id=op.id,
        target=target.to_dict(),
        environment=environment_name,
        artifact_id=target.artifact_id,
        dry_run=dry_run,
        previous_version=previous_version,
    )

    validate = adapter.validate(req)
    op.evidence.extend(scrub_evidence(validate.evidence))
    if validate.status == "failed":
        dep.status = "failed"
        assert_transition(op.status, "failed")
        op.status = "failed"
        op.notes.append("DEPLOYMENT_VALIDATION_FAILED")
        return OpsResult(
            operation=op,
            deployment=dep,
            readiness=readiness.to_dict(),
            audit=trail.to_list(),
            safety_gate=safety.to_dict(),
        )

    deploy = adapter.deploy(req)
    op.evidence.extend(scrub_evidence(deploy.evidence))
    assert_no_secrets(op.evidence)
    trail.append(
        actor=actor,
        role=role,
        environment=environment_name,
        action="deploy",
        result=deploy.status,
        evidence={"adapter": getattr(adapter, "name", "unknown"), "dry_run": dry_run},
    )

    if dry_run:
        dep.status = "succeeded"
        dep.ended_at = time.time()
        assert_transition(op.status, "verifying")
        op.status = "verifying"
        assert_transition(op.status, "succeeded")
        op.status = "succeeded"
        op.deployment_id = dep.id
        op.notes.append("dry-run only — no infrastructure mutated")
        return OpsResult(
            operation=op,
            deployment=dep,
            readiness=readiness.to_dict(),
            verification={"decision": "dry_run", "health": "n/a"},
            audit=trail.to_list(),
            safety_gate=safety.to_dict(),
        )

    if deploy.status != "ok":
        dep.status = "failed"
        assert_transition(op.status, "failed")
        op.status = "failed"
        op.notes.append("DEPLOYMENT_EXECUTION_FAILED")
        return OpsResult(
            operation=op,
            deployment=dep,
            readiness=readiness.to_dict(),
            audit=trail.to_list(),
            safety_gate=safety.to_dict(),
        )

    # --- verify health (deploy ok ≠ succeeded) ---
    assert_transition(op.status, "verifying")
    op.status = "verifying"
    health_res = adapter.health(req)
    op.evidence.extend(scrub_evidence(health_res.evidence))
    health = aggregate_health([health_res.health_hint])
    op.health_status = health
    verification = verify_deployment(deployment_id=dep.id, health=health, evidence=health_res.evidence)
    trail.append(
        actor=actor,
        role=role,
        environment=environment_name,
        action="health_check",
        result=health,
        evidence={"decision": verification.decision},
    )

    if not mark_succeeded_allowed(health=health):
        dep.ended_at = time.time()
        dep.status = "failed" if health == "unhealthy" else "succeeded"
        policy = rollback_policy_decision(
            environment_policy=env.rollback_policy,
            health=health,
            auto_rollback_allowed=auto_rollback_allowed,
        )
        if policy == "auto_rollback" and previous_version:
            assert_transition(op.status, "rollback_required")
            op.status = "rollback_required"
            assert_transition(op.status, "rolling_back")
            op.status = "rolling_back"
            rb = execute_rollback(
                adapter,
                operation_id=op.id,
                target=target.to_dict(),
                environment=environment_name,
                artifact_id=target.artifact_id,
                from_version=target.version,
                to_version=previous_version,
                reason=f"health={health}",
                policy="auto_allowed",
                authorized_by="policy:auto",
            )
            op.evidence.extend(scrub_evidence(rb.evidence))
            if rb.status == "verified":
                assert_transition(op.status, "rolled_back")
                op.status = "rolled_back"
            else:
                assert_transition(op.status, "needs_human")
                op.status = "needs_human"
                op.notes.append("ROLLBACK_FAILED")
            return OpsResult(
                operation=op,
                deployment=dep,
                readiness=readiness.to_dict(),
                verification=verification.to_dict(),
                rollback=rb.to_dict(),
                audit=trail.to_list(),
                safety_gate=safety.to_dict(),
            )

        next_status = verification.decision
        if next_status == "succeeded":
            next_status = "needs_human"
        if next_status not in {"degraded", "rollback_required", "needs_human", "failed"}:
            next_status = "needs_human"
        assert_transition(op.status, next_status)  # type: ignore[arg-type]
        op.status = next_status  # type: ignore[assignment]
        if env.rollback_policy == "human_required" and op.status in {"degraded", "rollback_required"}:
            assert_transition(op.status, "needs_human")
            op.status = "needs_human"
        return OpsResult(
            operation=op,
            deployment=dep,
            readiness=readiness.to_dict(),
            verification=verification.to_dict(),
            audit=trail.to_list(),
            safety_gate=safety.to_dict(),
        )

    dep.status = "succeeded"
    dep.ended_at = time.time()
    assert_transition(op.status, "succeeded")
    op.status = "succeeded"
    op.deployment_id = dep.id
    trail.append(
        actor=actor,
        role=role,
        environment=environment_name,
        action="finalize",
        result="succeeded",
        release=op.release_candidate_id,
    )
    return OpsResult(
        operation=op,
        deployment=dep,
        readiness=readiness.to_dict(),
        verification=verification.to_dict(),
        audit=trail.to_list(),
        safety_gate=safety.to_dict(),
    )
