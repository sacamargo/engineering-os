"""Extend Failure Model classifications for agent runtime."""

from __future__ import annotations

from orchestration.failure import FailureDecision, classify_failure

AGENT_CLASSES = {
    "TOOL_FAILURE": ("tool", False, "block"),
    "TASK_FAILURE": ("task", False, "replan"),
    "VALIDATION_FAILURE": ("validation", False, "block"),
    "PERMISSION_FAILURE": ("permission", False, "abort"),
    "TIMEOUT": ("timeout", True, "retry"),
    "ENVIRONMENT_FAILURE": ("environment", True, "retry"),
    "HUMAN_BLOCKED": ("human_blocked", False, "escalate"),
    "UNKNOWN_FAILURE": ("unknown", False, "block"),
}


def classify_agent_failure(task_id: str, classification: str, message: str = "") -> FailureDecision:
    key = classification.upper()
    if key in AGENT_CLASSES:
        kind, retryable, action = AGENT_CLASSES[key]
        # Map to orchestration FailureDecision actions
        return FailureDecision(
            task_id=task_id,
            classification=key,
            retryable=retryable,
            action=action,  # type: ignore[arg-type]
            reason=message or key,
        )
    return classify_failure(task_id, classification.lower(), message)
