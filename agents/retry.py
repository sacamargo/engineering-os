"""Controlled retry — never infinite."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any


RETRYABLE = frozenset({"timeout", "transient", "TOOL_FAILURE", "ENVIRONMENT_FAILURE"})
NON_RETRYABLE = frozenset(
    {
        "PERMISSION_FAILURE",
        "VALIDATION_FAILURE",
        "HUMAN_BLOCKED",
        "UNKNOWN_FAILURE",
        "TASK_FAILURE",
    }
)


@dataclass
class RetryPolicy:
    max_attempts: int = 2
    backoff_seconds: float = 0.05

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AttemptRecord:
    attempt: int
    classification: str
    action: str
    error: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def should_retry(classification: str, attempt: int, policy: RetryPolicy) -> bool:
    if attempt >= policy.max_attempts:
        return False
    if classification in NON_RETRYABLE:
        return False
    return classification in RETRYABLE or classification.lower() in {"timeout", "transient"}


def backoff_sleep(policy: RetryPolicy, attempt: int) -> None:
    time.sleep(policy.backoff_seconds * attempt)
