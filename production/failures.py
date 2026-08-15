"""Typed production failures — each maps to explicit states."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

FailureCode = Literal[
    "DEPLOYMENT_VALIDATION_FAILED",
    "DEPLOYMENT_EXECUTION_FAILED",
    "HEALTH_CHECK_FAILED",
    "ROLLBACK_FAILED",
    "PRODUCTION_APPROVAL_MISSING",
    "UNKNOWN_HEALTH",
    "CONFIGURATION_INVALID",
    "ARTIFACT_MISSING",
    "COMPATIBILITY_UNKNOWN",
]

# retryable | non_retryable | human_required
RETRY_CLASS: dict[str, str] = {
    "DEPLOYMENT_VALIDATION_FAILED": "non_retryable",
    "DEPLOYMENT_EXECUTION_FAILED": "retryable",
    "HEALTH_CHECK_FAILED": "human_required",
    "ROLLBACK_FAILED": "human_required",
    "PRODUCTION_APPROVAL_MISSING": "human_required",
    "UNKNOWN_HEALTH": "human_required",
    "CONFIGURATION_INVALID": "non_retryable",
    "ARTIFACT_MISSING": "non_retryable",
    "COMPATIBILITY_UNKNOWN": "human_required",
}

FAILURE_TO_STATUS: dict[str, str] = {
    "DEPLOYMENT_VALIDATION_FAILED": "failed",
    "DEPLOYMENT_EXECUTION_FAILED": "failed",
    "HEALTH_CHECK_FAILED": "rollback_required",
    "ROLLBACK_FAILED": "needs_human",
    "PRODUCTION_APPROVAL_MISSING": "awaiting_approval",
    "UNKNOWN_HEALTH": "needs_human",
    "CONFIGURATION_INVALID": "failed",
    "ARTIFACT_MISSING": "failed",
    "COMPATIBILITY_UNKNOWN": "needs_human",
}


@dataclass
class ProductionFailure:
    code: FailureCode
    message: str
    retry_class: str
    resulting_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_failure(code: FailureCode, message: str = "") -> ProductionFailure:
    return ProductionFailure(
        code=code,
        message=message or code,
        retry_class=RETRY_CLASS[code],
        resulting_status=FAILURE_TO_STATUS[code],
    )
