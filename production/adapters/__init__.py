"""Vendor-neutral deployment adapters (fake/local only in Phase 9)."""

from production.adapters.base import AdapterRequest, AdapterResult, DeploymentAdapter
from production.adapters.local import BackendLocalAdapter, LocalFakeAdapter, WebLocalAdapter

__all__ = [
    "AdapterRequest",
    "AdapterResult",
    "BackendLocalAdapter",
    "DeploymentAdapter",
    "LocalFakeAdapter",
    "WebLocalAdapter",
]
