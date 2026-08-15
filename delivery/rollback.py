"""Rollback model — traceability only; no infra mutation."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any

from delivery.adapter import LocalDeliveryAdapter


@dataclass
class RollbackPlan:
    id: str
    from_release: str
    to_release: str
    reason: str
    authorized_by: str | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    status: str = "planned"  # planned | authorized | unsupported
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def plan_rollback(
    *,
    from_release: str,
    to_release: str,
    reason: str,
    authorized_by: str | None = None,
) -> RollbackPlan:
    adapter = LocalDeliveryAdapter()
    result = adapter.rollback({"from": from_release, "to": to_release, "reason": reason})
    return RollbackPlan(
        id=f"eos.rollback.{from_release[-8:]}-{to_release[-8:]}",
        from_release=from_release,
        to_release=to_release,
        reason=reason,
        authorized_by=authorized_by,
        evidence=result.evidence,
        status="authorized" if authorized_by else "planned",
    )
