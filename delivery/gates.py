"""Delivery gates — reuse gate semantics; never bypass."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from delivery.model import DeliveryArtifact, ValidationRun


@dataclass
class DeliveryGateResult:
    gate_id: str
    passed: bool
    missing: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_delivery_gates(
    *,
    validations: list[ValidationRun],
    artifacts: list[DeliveryArtifact],
    security_status: str,
    approval_granted: bool,
    environment: str,
    require_security: bool = True,
) -> list[DeliveryGateResult]:
    results: list[DeliveryGateResult] = []

    # tests gate
    test_runs = [v for v in validations if v.kind in {"unit", "integration", "contract", "test"}]
    missing = []
    if not test_runs:
        missing.append("no_test_validation_run")
    elif any(v.status == "NOT_RUN" for v in test_runs):
        missing.append("tests_not_run")
    elif any(v.status != "PASSED" for v in test_runs):
        missing.append("tests_failed")
    results.append(
        DeliveryGateResult("tests", not missing, missing, ["NOT_RUN is not PASSED"])
    )

    # security gate
    sec_missing = []
    if require_security:
        if security_status in {"unknown", "UNKNOWN", ""}:
            sec_missing.append("security_unknown")
        elif security_status in {"failed", "FAILED", "blocked", "BLOCKED"}:
            sec_missing.append("security_blocker")
    results.append(DeliveryGateResult("security", not sec_missing, sec_missing, []))

    # artifact gate
    art_missing = []
    if not artifacts:
        art_missing.append("no_artifact")
    elif any(not a.digest for a in artifacts if a.type in {"package", "source_bundle", "build_output"}):
        art_missing.append("artifact_missing_digest")
    results.append(DeliveryGateResult("artifact", not art_missing, art_missing, []))

    # approval gate for production
    appr_missing = []
    if environment == "production" and not approval_granted:
        appr_missing.append("production_approval_required")
    results.append(DeliveryGateResult("approval", not appr_missing, appr_missing, []))

    return results


def all_gates_passed(gates: list[DeliveryGateResult]) -> bool:
    return all(g.passed for g in gates)
