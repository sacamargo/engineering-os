"""Structured execution log — no secrets."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any


SENSITIVE_KEYS = ("password", "secret", "token", "api_key", "authorization")


def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if any(s in str(k).lower() for s in SENSITIVE_KEYS):
                out[k] = "***REDACTED***"
            else:
                out[k] = redact(v)
        return out
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    if isinstance(obj, str) and len(obj) > 20_000:
        return obj[:20_000] + "…truncated"
    return obj


@dataclass
class LogEntry:
    execution_id: str
    task_id: str
    agent_id: str
    tool_id: str
    input: dict[str, Any]
    output: dict[str, Any]
    result: str
    error: str | None = None
    duration_ms: float = 0.0
    evidence: list[dict[str, Any]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["input"] = redact(data["input"])
        data["output"] = redact(data["output"])
        return data


@dataclass
class ExecutionLog:
    execution_id: str
    entries: list[LogEntry] = field(default_factory=list)

    def add(self, entry: LogEntry) -> None:
        self.entries.append(entry)

    def to_dict(self) -> dict[str, Any]:
        return {"execution_id": self.execution_id, "entries": [e.to_dict() for e in self.entries]}
