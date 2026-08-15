"""Release boundaries — Mobile/Web/Backend are distinct; stores are external adapters."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

ReleaseKind = Literal["backend", "web", "ios", "android", "bundle"]


@dataclass
class BackendRelease:
    id: str
    artifact_id: str
    version: str
    migration_refs: list[str] = field(default_factory=list)
    config_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "backend", **asdict(self)}


@dataclass
class WebRelease:
    id: str
    artifact_id: str
    version: str
    config_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "web", **asdict(self)}


@dataclass
class MobileRelease:
    id: str
    platform: Literal["ios", "android"]
    artifact_id: str
    version: str
    store_boundary: str  # app_store | play_store — external only
    publish_allowed: bool = False  # Engineering OS never auto-publishes

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["kind"] = self.platform
        d["notes"] = [
            "App Store / Play Store remain external adapters",
            "publish_allowed defaults False — prepare artifacts/checklists only",
        ]
        return d


@dataclass
class ReleaseBundle:
    id: str
    web: WebRelease | None = None
    backend: BackendRelease | None = None
    ios: MobileRelease | None = None
    android: MobileRelease | None = None
    migrations: list[str] = field(default_factory=list)
    configuration_refs: list[str] = field(default_factory=list)
    dependencies: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": "bundle",
            "web": self.web.to_dict() if self.web else None,
            "backend": self.backend.to_dict() if self.backend else None,
            "ios": self.ios.to_dict() if self.ios else None,
            "android": self.android.to_dict() if self.android else None,
            "migrations": self.migrations,
            "configuration_refs": self.configuration_refs,
            "dependencies": self.dependencies,
        }


def mobile_publish_checklist(release: MobileRelease) -> dict[str, Any]:
    return {
        "release_id": release.id,
        "platform": release.platform,
        "store_boundary": release.store_boundary,
        "auto_publish": False,
        "required_evidence": [
            "artifact_signed",
            "version_bump",
            "release_notes",
            "human_store_submission",
        ],
        "status": "PREPARE_ONLY",
    }
