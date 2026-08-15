"""DeliveryAdapter interface — local fake only in Phase 7."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


@dataclass
class AdapterResult:
    ok: bool
    status: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DeliveryAdapter(Protocol):
    def validate(self, payload: dict[str, Any]) -> AdapterResult: ...

    def package(self, payload: dict[str, Any]) -> AdapterResult: ...

    def publish(self, payload: dict[str, Any]) -> AdapterResult: ...

    def release(self, payload: dict[str, Any]) -> AdapterResult: ...

    def status(self, payload: dict[str, Any]) -> AdapterResult: ...

    def rollback(self, payload: dict[str, Any]) -> AdapterResult: ...


class LocalDeliveryAdapter:
    """Deterministic local adapter — no cloud vendors."""

    name = "local"

    def validate(self, payload: dict[str, Any]) -> AdapterResult:
        return AdapterResult(True, "validated", [{"kind": "adapter_validate"}], "local validate")

    def package(self, payload: dict[str, Any]) -> AdapterResult:
        return AdapterResult(True, "packaged", [{"kind": "adapter_package"}], "local package")

    def publish(self, payload: dict[str, Any]) -> AdapterResult:
        return AdapterResult(False, "unsupported", [], "publish not implemented in local adapter")

    def release(self, payload: dict[str, Any]) -> AdapterResult:
        return AdapterResult(True, "release_prepared", [{"kind": "adapter_release"}], "local release prep")

    def status(self, payload: dict[str, Any]) -> AdapterResult:
        return AdapterResult(True, str(payload.get("status") or "unknown"), [], "status echo")

    def rollback(self, payload: dict[str, Any]) -> AdapterResult:
        return AdapterResult(
            True,
            "rollback_candidate",
            [{"kind": "rollback_model", "from": payload.get("from"), "to": payload.get("to")}],
            "rollback modeled only — no infra mutation",
        )
