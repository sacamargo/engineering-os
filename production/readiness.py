"""Pre-deploy readiness — NO DEPLOY if gaps exist."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ReadinessGap:
    code: str
    message: str
    blocking: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PreDeployReadiness:
    ready: bool
    gaps: list[ReadinessGap] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"ready": self.ready, "gaps": [g.to_dict() for g in self.gaps]}


def evaluate_pre_deploy(
    *,
    release_candidate: dict[str, Any] | None,
    artifact_exists: bool,
    tests_status: str,
    security_status: str,
    gates_passed: bool,
    evidence_complete: bool,
    environment: dict[str, Any] | None,
    permissions_ok: bool,
    approval_satisfied: bool,
    rollback_strategy: bool,
    health_checks_defined: bool,
) -> PreDeployReadiness:
    gaps: list[ReadinessGap] = []
    if not release_candidate:
        gaps.append(ReadinessGap("ARTIFACT_MISSING", "ReleaseCandidate required"))
    elif not release_candidate.get("id"):
        gaps.append(ReadinessGap("RELEASE_INVALID", "ReleaseCandidate invalid"))
    else:
        # Accept Delivery markers; UNKNOWN/missing readiness ≠ PASSED
        status = str(release_candidate.get("status") or "").lower()
        readiness = str(release_candidate.get("readiness") or "").upper()
        ok_status = status in {"ready", "approved", "release_ready", "released", ""}
        ok_ready = readiness in {
            "",
            "READY_FOR_RELEASE",
            "READY_FOR_DEPLOYMENT",
            "READY",
        }
        if status in {"blocked", "failed", "draft"} or readiness in {"BLOCKED", "NEEDS_HUMAN", "UNKNOWN"}:
            gaps.append(
                ReadinessGap(
                    "RELEASE_INVALID",
                    f"ReleaseCandidate not deployable status={status!r} readiness={readiness!r}",
                )
            )
        elif not ok_status and not ok_ready and status not in {"ready", "approved"}:
            # If neither status nor readiness looks ready, require explicit ready markers
            if readiness and readiness not in {"READY_FOR_RELEASE", "READY_FOR_DEPLOYMENT"}:
                gaps.append(ReadinessGap("RELEASE_INVALID", f"readiness={readiness!r} ≠ PASSED"))
    if not artifact_exists:
        gaps.append(ReadinessGap("ARTIFACT_MISSING", "artifact must exist"))
    if tests_status != "PASSED":
        gaps.append(ReadinessGap("TESTS_NOT_PASSED", f"tests={tests_status}"))
    if security_status != "PASSED":
        gaps.append(ReadinessGap("SECURITY_NOT_PASSED", f"security={security_status}"))
    if not gates_passed:
        gaps.append(ReadinessGap("GATES_NOT_PASSED", "required gates not passed"))
    if not evidence_complete:
        gaps.append(ReadinessGap("EVIDENCE_INCOMPLETE", "evidence incomplete"))
    if not environment:
        gaps.append(ReadinessGap("ENVIRONMENT_INVALID", "environment missing"))
    if not permissions_ok:
        gaps.append(ReadinessGap("PERMISSIONS_DENIED", "permissions invalid"))
    if environment and environment.get("approval_policy") == "human_required" and not approval_satisfied:
        gaps.append(ReadinessGap("PRODUCTION_APPROVAL_MISSING", "HUMAN_APPROVAL_REQUIRED"))
    if not rollback_strategy:
        gaps.append(ReadinessGap("ROLLBACK_STRATEGY_MISSING", "rollback strategy required"))
    if not health_checks_defined:
        gaps.append(ReadinessGap("HEALTH_CHECKS_MISSING", "health checks required"))
    # UNKNOWN must not pass
    if tests_status == "UNKNOWN":
        gaps.append(ReadinessGap("COMPATIBILITY_UNKNOWN", "UNKNOWN tests ≠ PASSED"))
    if security_status == "UNKNOWN":
        gaps.append(ReadinessGap("COMPATIBILITY_UNKNOWN", "UNKNOWN security ≠ PASSED"))
    return PreDeployReadiness(ready=not gaps, gaps=gaps)
