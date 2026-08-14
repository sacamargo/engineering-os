"""Adapter boundary — Core remains vendor-neutral."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol


@dataclass
class AdapterDescriptor:
    name: str
    direction: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EnvironmentAdapter(Protocol):
    """External Environment → Engineering OS."""

    name: str

    def ingest(self, payload: dict[str, Any]) -> dict[str, Any]: ...


def core_adapter_policy() -> AdapterDescriptor:
    return AdapterDescriptor(
        name="core_policy",
        direction="external_to_eos",
        notes="Core must not depend on Cursor/Claude/ChatGPT APIs. Adapters translate inward.",
    )
