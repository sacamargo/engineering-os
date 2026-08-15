"""LLM boundary — optional future adapter; core must run without providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class LLMDecision:
    thought: str
    tool_id: str | None
    arguments: dict[str, Any]


class LLMProvider(Protocol):
    def decide(self, context: dict[str, Any]) -> LLMDecision: ...


class NullLLM:
    """Deterministic path: no model calls."""

    def decide(self, context: dict[str, Any]) -> LLMDecision:
        return LLMDecision(thought="null llm — use deterministic plan", tool_id=None, arguments={})
