"""Local/fake deployment adapters — no real infrastructure."""

from __future__ import annotations

import time
from typing import Any

from production.adapters.base import AdapterRequest, AdapterResult


class LocalFakeAdapter:
    """Deterministic fake adapter for web/backend tests."""

    name = "local_fake"

    def __init__(self, *, force_health: str | None = None, fail_deploy: bool = False) -> None:
        self.force_health = force_health
        self.fail_deploy = fail_deploy
        self._deployed: dict[str, str] = {}

    def validate(self, request: AdapterRequest) -> AdapterResult:
        if not request.artifact_id:
            return AdapterResult("failed", "artifact missing", adapter=self.name)
        return AdapterResult("ok", "target validated", evidence=[{"kind": "validate"}], adapter=self.name)

    def deploy(self, request: AdapterRequest) -> AdapterResult:
        if request.dry_run:
            return AdapterResult(
                "dry_run",
                "dry-run: no infrastructure mutated",
                evidence=[{"kind": "dry_run", "planned": ["deploy_artifact", "register_version"]}],
                adapter=self.name,
            )
        if self.fail_deploy:
            return AdapterResult("failed", "forced deploy failure", adapter=self.name)
        version = str(request.target.get("version") or "0.0.0")
        self._deployed[request.environment] = version
        return AdapterResult(
            "ok",
            "fake deploy recorded",
            evidence=[{"kind": "deploy", "version": version, "ts": time.time()}],
            health_hint=None,  # health must be checked separately
            adapter=self.name,
        )

    def status(self, request: AdapterRequest) -> AdapterResult:
        v = self._deployed.get(request.environment)
        return AdapterResult(
            "ok" if v else "failed",
            f"version={v}" if v else "not deployed",
            evidence=[{"kind": "status", "version": v}],
            adapter=self.name,
        )

    def health(self, request: AdapterRequest) -> AdapterResult:
        if self.force_health:
            return AdapterResult(
                "ok" if self.force_health == "healthy" else "failed",
                f"health={self.force_health}",
                evidence=[{"kind": "health", "status": self.force_health}],
                health_hint=self.force_health,
                adapter=self.name,
            )
        if request.environment not in self._deployed:
            return AdapterResult(
                "failed",
                "unknown health — not deployed",
                evidence=[{"kind": "health", "status": "unknown"}],
                health_hint="unknown",
                adapter=self.name,
            )
        return AdapterResult(
            "ok",
            "health=healthy",
            evidence=[{"kind": "health", "status": "healthy"}],
            health_hint="healthy",
            adapter=self.name,
        )

    def rollback(self, request: AdapterRequest) -> AdapterResult:
        if request.dry_run:
            return AdapterResult("dry_run", "dry-run rollback", adapter=self.name)
        if not request.previous_version:
            return AdapterResult("failed", "rollback target version unknown", adapter=self.name)
        self._deployed[request.environment] = request.previous_version
        # Prior version is assumed healthy in the fake unless explicitly forced unknown
        if self.force_health in {"unhealthy", "degraded"}:
            self.force_health = "healthy"
        return AdapterResult(
            "ok",
            f"rolled back to {request.previous_version}",
            evidence=[{"kind": "rollback", "to": request.previous_version}],
            health_hint=None,
            adapter=self.name,
        )


class WebLocalAdapter(LocalFakeAdapter):
    name = "web_local_fake"


class BackendLocalAdapter(LocalFakeAdapter):
    name = "backend_local_fake"
