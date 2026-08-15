"""Production safety gate — never authorize with `if production: true`."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from production.approval import is_human_approver
from production.permissions import authorize


@dataclass
class SafetyGateResult:
    allowed: bool
    gate: str = "PRODUCTION_OPERATION_ALLOWED"
    evidence: list[dict[str, Any]] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def production_operation_allowed(
    *,
    environment: str,
    granted_permissions: list[str],
    required_permissions: list[str],
    approval_decision: str | None,
    approver: str | None,
    readiness_ready: bool,
    release_candidate_id: str | None,
    policy_evidence: list[dict[str, Any]] | None = None,
    dry_run: bool = False,
) -> SafetyGateResult:
    gaps: list[str] = []
    evidence: list[dict[str, Any]] = list(policy_evidence or [])
    # Explicit: never treat environment name alone as authorization
    evidence.append({"kind": "env_name_not_authorization", "environment": environment})

    if not release_candidate_id:
        gaps.append("missing_release_candidate")
    if not readiness_ready:
        gaps.append("readiness_not_ready")

    perm = authorize(granted_permissions, required_permissions)
    evidence.append({"kind": "permissions", **perm.__dict__})
    if not perm.allowed:
        gaps.append("permissions_denied")

    if environment == "production" and not dry_run:
        if approval_decision != "approved":
            gaps.append("PRODUCTION_APPROVAL_MISSING")
        if not is_human_approver(approver or ""):
            gaps.append("HUMAN_APPROVAL_REQUIRED")
        evidence.append(
            {
                "kind": "human_approval_check",
                "approver": approver,
                "decision": approval_decision,
                "human": is_human_approver(approver or ""),
            }
        )
    else:
        evidence.append(
            {
                "kind": "non_production_or_dry_run_gate",
                "environment": environment,
                "dry_run": dry_run,
            }
        )

    return SafetyGateResult(allowed=not gaps, evidence=evidence, gaps=gaps)
