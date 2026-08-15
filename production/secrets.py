"""Secret boundary — never store/print/log secret values."""

from __future__ import annotations

import re
from typing import Any

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|password|token|private[_-]?key)\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[a-z0-9\-._~+/]+=*"),
]


def looks_like_secret(value: str) -> bool:
    return any(p.search(value) for p in SECRET_PATTERNS)


def scrub_evidence(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for item in items:
        blob = str(item)
        if looks_like_secret(blob):
            cleaned.append({"kind": "redacted", "reason": "secret_boundary"})
        else:
            cleaned.append(item)
    return cleaned


def assert_no_secrets(payload: Any) -> None:
    text = str(payload)
    if looks_like_secret(text):
        raise ValueError("secret leakage forbidden in production evidence/logs")
