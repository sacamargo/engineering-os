"""Configuration vs secret — secrets are external references only."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ConfigRef:
    id: str
    version: str
    locator: str  # non-secret reference

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SecretRef:
    id: str
    provider_ref: str  # external reference only — never a value
    notes: str = "secret value must not enter core"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if "value" in d:
            raise ValueError("secret value forbidden")
        return d
