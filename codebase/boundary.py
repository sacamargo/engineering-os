"""Repository read boundary — what Codebase Intelligence may open."""

from __future__ import annotations

import re
from pathlib import Path

# Path segments / names never opened for content analysis
DENIED_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "credentials.json",
    "credentials.csv",
    "id_rsa",
    "id_ed25519",
    "private.key",
    "secret.key",
}

DENIED_SUFFIXES = (
    ".pem",
    ".p12",
    ".pfx",
    ".key",
)

DENIED_DIR_NAMES = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".tox",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    "coverage",
    ".next",
    "target",
}

SENSITIVE_NAME_RE = re.compile(
    r"(^|/)(\.env($|\.)|.*secret.*|.*credential.*|.*password.*|id_rsa|id_ed25519)($|/)",
    re.I,
)


def is_denied_dir(name: str) -> bool:
    return name in DENIED_DIR_NAMES


def is_sensitive_path(rel: str) -> bool:
    name = Path(rel).name
    if name in DENIED_NAMES:
        return True
    if name.endswith(DENIED_SUFFIXES):
        return True
    if SENSITIVE_NAME_RE.search(rel.replace("\\", "/")):
        return True
    return False


def may_read_content(rel: str) -> bool:
    """Whether file contents may be parsed (still inventoriable as path-only)."""
    return not is_sensitive_path(rel)
