"""Tool invocation / result interface — vendor neutral, no LLM required."""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ToolInvocation:
    tool_id: str
    arguments: dict[str, Any]
    task_id: str
    agent_id: str
    id: str = field(default_factory=lambda: f"eos.toolcall.{uuid.uuid4().hex[:10]}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ToolResult:
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    duration_ms: float = 0.0
    invocation_id: str = ""
    tool_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def timed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 3)
