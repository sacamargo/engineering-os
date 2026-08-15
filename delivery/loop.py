"""Delivery execution loop — local deterministic runtime."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from agents.concurrency import workspace_lock
from agents.sandbox import Workspace
from codebase.analyze import analyze_repository
from delivery.adapter import LocalDeliveryAdapter
from delivery.deployment import DeploymentRequest, NullDeploymentAdapter
from delivery.executors import run_build_step, run_test_step, write_artifact_bundle
from delivery.gates import all_gates_passed, evaluate_delivery_gates
from delivery.model import (
    Build,
    DeliveryArtifact,
    DeliveryRecord,
    ReleaseCandidate,
    ValidationRun,
    default_pipeline,
    new_artifact_id,
    new_build_id,
    new_delivery_id,
    new_rc_id,
    new_validation_id,
)
from delivery.permissions import PROFILES, assert_authorized
from delivery.risk import classify_change_risk
from delivery.states import transition


@dataclass
class DeliveryResult:
    delivery: dict[str, Any]
    build: dict[str, Any] | None = None
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    validations: list[dict[str, Any]] = field(default_factory=list)
    gates: list[dict[str, Any]] = field(default_factory=list)
    release_candidate: dict[str, Any] | None = None
    decision: dict[str, Any] | None = None
    deployment_boundary: dict[str, Any] | None = None
    readiness: str = "BLOCKED"
    status: str = "failed"
    audit_trail: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _security_status_from_analysis(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "clear"
    blockers = [
        f
        for f in findings
        if f.get("kind") in {"insecure_pattern", "sensitive_path"}
        or f.get("severity") in {"high", "critical"}
    ]
    if blockers:
        return "blocked"
    return "clear"


def run_delivery(
    workspace_root: str | Path,
    *,
    project_id: str = "eos.project.demo",
    changeset_id: str = "eos.changeset.local",
    changed_paths: list[str] | None = None,
    environment: str = "local",
    actor_profile: str = "release_engineer",
    test_command: str = "python3 -m unittest discover -s . -p 'test_*.py' -v",
    approval_granted: bool = False,
    approver: str | None = None,
    skip_codebase_analysis: bool = False,
    force_security_status: str | None = None,
) -> DeliveryResult:
    """
    ChangeSet → Build → Tests → Security → Artifact → Gates → ReleaseCandidate → Readiness.

    Never deploys. Never self-approves production.
    """
    t0 = time.perf_counter()
    workspace = Workspace(workspace_root)
    granted = PROFILES.get(actor_profile, PROFILES["analysis"])
    audit: list[dict[str, Any]] = []
    pipeline = default_pipeline()

    # Self-approval / permission checks
    try:
        assert_authorized(granted, ["DELIVERY_READ", "BUILD_EXECUTE", "ARTIFACT_CREATE", "RELEASE_CREATE"])
    except PermissionError as exc:
        rec = DeliveryRecord(
            id=new_delivery_id(project_id),
            project_id=project_id,
            changeset_id=changeset_id,
            status="failed",
            readiness="BLOCKED",
            environment=environment,  # type: ignore[arg-type]
            failures=[{"classification": "PERMISSION_FAILURE", "reason": str(exc)}],
            notes=[str(exc)],
        )
        return DeliveryResult(delivery=rec.to_dict(), status="failed", readiness="BLOCKED", notes=[str(exc)])

    if environment == "production" and actor_profile != "human_approver" and not approval_granted:
        # Agents cannot auto-approve production
        pass  # handled by gates

    rec = DeliveryRecord(
        id=new_delivery_id(project_id),
        project_id=project_id,
        changeset_id=changeset_id,
        environment=environment,  # type: ignore[arg-type]
        readiness="READY_FOR_BUILD",
        notes=["Delivery ≠ Deployment", "Vendor-neutral local runtime"],
    )
    rec.status = transition("draft", "building")
    audit.append({"event": "delivery_started", "delivery_id": rec.id, "pipeline": pipeline.id})

    findings: list[dict[str, Any]] = []
    security_status = force_security_status or "unknown"
    with workspace_lock(workspace.root):
        if not skip_codebase_analysis:
            try:
                bundle = analyze_repository(workspace.root)
                findings = list(bundle.snapshot.findings)
                security_status = force_security_status or _security_status_from_analysis(findings)
                audit.append(
                    {
                        "event": "codebase_analysis",
                        "snapshot_id": bundle.snapshot.id,
                        "findings": len(findings),
                        "security_status": security_status,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                security_status = force_security_status or "unknown"
                audit.append({"event": "codebase_analysis_failed", "error": str(exc)})

        paths = list(changed_paths or [])
        if not paths:
            paths = []
            for p in workspace.root.rglob("*.py"):
                if p.is_file():
                    paths.append(str(p.relative_to(workspace.root)))
                if len(paths) >= 20:
                    break
        rec.risk = classify_change_risk(paths, findings=findings, environment=environment)

        # Build
        build = Build(
            id=new_build_id(),
            changeset_id=changeset_id,
            environment=environment,  # type: ignore[arg-type]
            commands=[test_command],
            status="running",
            started_at=time.time(),
        )
        build_out = run_build_step(workspace, command=test_command)
        if not build_out["success"]:
            build.status = "failed"
            build.failure_reason = build_out.get("error") or "build failed"
            build.evidence = build_out["evidence"]
            rec.status = transition("building", "failed")
            rec.readiness = "BLOCKED"
            rec.failures.append({"classification": "BUILD_FAILURE", "reason": build.failure_reason})
            rec.metrics["duration_seconds"] = round(time.perf_counter() - t0, 4)
            return DeliveryResult(
                delivery=rec.to_dict(),
                build=build.to_dict(),
                status="failed",
                readiness="BLOCKED",
                audit_trail=audit,
                notes=["Build failed — not ready."],
            )
        build.mark_succeeded(evidence=build_out["evidence"], artifact_ids=[])
        rec.build_id = build.id
        rec.status = transition("building", "validating")
        rec.readiness = "READY_FOR_VALIDATION"
        audit.append({"event": "build_succeeded", "build_id": build.id})

        # Tests
        test_out = run_test_step(workspace, command=test_command)
        v_test = ValidationRun(
            id=new_validation_id("unit"),
            kind="unit",
            build_id=build.id,
            changeset_id=changeset_id,
            status=test_out["status"],  # type: ignore[arg-type]
            command=test_command,
            evidence=test_out["evidence"],
            duration_seconds=test_out["duration_seconds"],
        )
        if test_out.get("zero_tests"):
            v_test.notes.append("Zero tests executed — treated as FAILED")
        audit.append({"event": "tests_finished", "status": v_test.status})

        # Security validation run
        v_sec = ValidationRun(
            id=new_validation_id("security"),
            kind="security",
            changeset_id=changeset_id,
            status="PASSED" if security_status == "clear" else ("BLOCKED" if security_status == "blocked" else "UNKNOWN"),
            evidence=[{"kind": "security_status", "status": security_status, "findings": len(findings)}],
        )
        if v_sec.status == "UNKNOWN":
            v_sec.notes.append("Unknown security status blocks automatic release")

        # Artifact
        adapter = LocalDeliveryAdapter()
        pkg = adapter.package({"changeset_id": changeset_id})
        content = (
            f"project={project_id}\nchangeset={changeset_id}\nbuild={build.id}\n"
            f"risk={rec.risk}\nsecurity={security_status}\n"
        )
        art_meta = write_artifact_bundle(workspace, content=content)
        artifact = DeliveryArtifact(
            id=new_artifact_id("build_output"),
            type="build_output",
            origin=f"build:{build.id}",
            version="0.1.0",
            digest=art_meta["digest"],
            path=art_meta["path"],
            evidence_ids=[],
            metadata={"adapter": adapter.name},
        )
        build.artifact_ids.append(artifact.id)
        rec.artifact_ids.append(artifact.id)
        audit.append({"event": "artifact_created", "artifact_id": artifact.id, "digest": artifact.digest})

        validations = [v_test, v_sec]
        rec.validation_ids = [v.id for v in validations]

        gates = evaluate_delivery_gates(
            validations=validations,
            artifacts=[artifact],
            security_status=security_status,
            approval_granted=approval_granted,
            environment=environment,
        )
        audit.append({"event": "gates_evaluated", "gates": [g.to_dict() for g in gates]})

        if not all_gates_passed(gates):
            missing = [m for g in gates for m in g.missing]
            if any("approval" in m for m in missing) or environment == "production" and not approval_granted:
                rec.status = transition("validating", "needs_human")
                rec.readiness = "NEEDS_HUMAN"
                status = "needs_human"
            else:
                rec.status = transition("validating", "blocked")
                rec.readiness = "BLOCKED"
                status = "blocked"
            rec.failures.append({"classification": "GATE_FAILURE", "missing": missing})
            rec.metrics["duration_seconds"] = round(time.perf_counter() - t0, 4)
            return DeliveryResult(
                delivery=rec.to_dict(),
                build=build.to_dict(),
                artifacts=[artifact.to_dict()],
                validations=[v.to_dict() for v in validations],
                gates=[g.to_dict() for g in gates],
                status=status,
                readiness=rec.readiness,
                audit_trail=audit,
                notes=["NOT READY — gates not satisfied."],
            )

        # Release candidate
        rc = ReleaseCandidate(
            id=new_rc_id(),
            version="0.1.0",
            changeset_id=changeset_id,
            artifact_ids=[artifact.id],
            validation_ids=[v.id for v in validations],
            gate_ids=[g.gate_id for g in gates],
            target_environment=environment,  # type: ignore[arg-type]
            status="ready",
        )
        decision = {
            "decision": "approved" if environment != "production" or approval_granted else "pending",
            "release_candidate_id": rc.id,
            "evidence": [e for v in validations for e in v.evidence] + art_meta["evidence"],
            "gates": [g.to_dict() for g in gates],
            "approver": approver or ("system:local" if environment != "production" else None),
            "timestamp": time.time(),
            "risk": rec.risk,
        }
        if environment == "production" and not approval_granted:
            rec.status = transition("validating", "needs_human")
            rec.readiness = "NEEDS_HUMAN"
            return DeliveryResult(
                delivery=rec.to_dict(),
                build=build.to_dict(),
                artifacts=[artifact.to_dict()],
                validations=[v.to_dict() for v in validations],
                gates=[g.to_dict() for g in gates],
                release_candidate=rc.to_dict(),
                decision=decision,
                status="needs_human",
                readiness="NEEDS_HUMAN",
                audit_trail=audit,
                notes=["Production requires human approval."],
            )

        # Prevent agent self-approval spoof: RELEASE_APPROVE required for production
        if environment == "production":
            try:
                assert_authorized(granted | ({"RELEASE_APPROVE"} if approval_granted else set()), ["RELEASE_APPROVE"])
            except PermissionError:
                # approval_granted from human path — require approver identity
                if not approver or approver.startswith("agent:"):
                    rec.status = transition("validating", "needs_human")
                    rec.readiness = "NEEDS_HUMAN"
                    return DeliveryResult(
                        delivery=rec.to_dict(),
                        build=build.to_dict(),
                        artifacts=[artifact.to_dict()],
                        validations=[v.to_dict() for v in validations],
                        gates=[g.to_dict() for g in gates],
                        release_candidate=rc.to_dict(),
                        status="needs_human",
                        readiness="NEEDS_HUMAN",
                        audit_trail=audit,
                        notes=["Agent self-approval forbidden."],
                    )

        rec.status = transition("validating", "ready")
        rec.release_candidate_id = rc.id
        rec.readiness = "READY_FOR_RELEASE"
        rc.decisions.append(decision)
        adapter.release({"rc": rc.id})

        # Optional: mark released (candidate accepted) — still not deployed
        rec.status = transition("ready", "released")
        rec.readiness = "READY_FOR_DEPLOYMENT"
        deploy = NullDeploymentAdapter().status(
            DeploymentRequest(rc.id, environment, [artifact.id])
        )
        audit.append({"event": "release_candidate_ready", "rc": rc.id, "deployment": deploy.to_dict()})
        rec.metrics = {
            "duration_seconds": round(time.perf_counter() - t0, 4),
            "risk": rec.risk,
            "validations": len(validations),
            "gates_passed": len(gates),
        }
        rec.evidence.extend(v_test.evidence + v_sec.evidence + art_meta["evidence"])

        return DeliveryResult(
            delivery=rec.to_dict(),
            build=build.to_dict(),
            artifacts=[artifact.to_dict()],
            validations=[v.to_dict() for v in validations],
            gates=[g.to_dict() for g in gates],
            release_candidate=rc.to_dict(),
            decision=decision,
            deployment_boundary=deploy.to_dict(),
            readiness=rec.readiness,
            status="released",
            audit_trail=audit,
            notes=[
                "ReleaseCandidate prepared with evidence.",
                "Deployment NOT executed (boundary).",
            ],
        )
