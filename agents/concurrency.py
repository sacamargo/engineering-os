"""One writer per workspace (conservative concurrency)."""

from __future__ import annotations

import threading
from pathlib import Path

_locks: dict[str, threading.Lock] = {}
_guard = threading.Lock()


def workspace_lock(root: str | Path) -> threading.Lock:
    key = str(Path(root).resolve())
    with _guard:
        if key not in _locks:
            _locks[key] = threading.Lock()
        return _locks[key]
