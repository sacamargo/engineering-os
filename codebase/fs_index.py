"""Filesystem index — structural inventory respecting gitignore and boundary policy."""

from __future__ import annotations

import hashlib
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from codebase.boundary import is_denied_dir, is_sensitive_path, may_read_content

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tar",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp4",
    ".mp3",
    ".dylib",
    ".so",
    ".dll",
    ".exe",
    ".bin",
}

GENERATED_HINTS = (
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Cargo.lock",
    ".min.js",
    ".min.css",
    "dist/",
    "build/",
)


@dataclass
class FileRecord:
    path: str
    extension: str
    size: int
    content_hash: str | None
    is_binary: bool
    ignored: bool
    generated: bool
    sensitive: bool
    content_readable: bool
    certainty: str = "observed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DirRecord:
    path: str
    child_file_count: int = 0
    child_dir_count: int = 0
    certainty: str = "observed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FilesystemIndex:
    files: list[FileRecord] = field(default_factory=list)
    directories: list[DirRecord] = field(default_factory=list)
    included_count: int = 0
    excluded_count: int = 0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "files": [f.to_dict() for f in self.files],
            "directories": [d.to_dict() for d in self.directories],
            "included_count": self.included_count,
            "excluded_count": self.excluded_count,
            "notes": self.notes,
        }


def _load_gitignore_patterns(root: Path) -> list[str]:
    path = root / ".gitignore"
    if not path.exists():
        return []
    patterns: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _gitignore_match(rel: str, patterns: list[str]) -> bool:
    """Minimal gitignore matcher (not full git semantics)."""
    rel_posix = rel.replace("\\", "/")
    name = Path(rel_posix).name
    for pat in patterns:
        negated = pat.startswith("!")
        p = pat[1:] if negated else pat
        p = p.strip("/")
        matched = False
        if p.startswith("*") and name.endswith(p[1:]):
            matched = True
        elif p.endswith("/") and (rel_posix.startswith(p) or f"/{p}" in f"/{rel_posix}/"):
            matched = True
        elif p.endswith("/**"):
            prefix = p[:-3]
            matched = rel_posix == prefix or rel_posix.startswith(prefix + "/")
        elif "*" in p:
            # simplistic: suffix after last *
            suffix = p.split("*")[-1]
            matched = rel_posix.endswith(suffix) if suffix else False
        else:
            matched = (
                rel_posix == p
                or rel_posix.startswith(p + "/")
                or name == p
                or f"/{p}/" in f"/{rel_posix}/"
            )
        if matched:
            return not negated
    return False


def _is_binary(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        chunk = path.read_bytes()[:2048]
    except OSError:
        return True
    return b"\0" in chunk


def _hash_file(path: Path, readable: bool) -> str | None:
    if not readable:
        return None
    if _is_binary(path):
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for block in iter(lambda: fh.read(65536), b""):
                h.update(block)
        return h.hexdigest()
    try:
        data = path.read_bytes()
    except OSError:
        return None
    return hashlib.sha256(data).hexdigest()


def _generated(rel: str) -> bool:
    rel_posix = rel.replace("\\", "/")
    return any(hint in rel_posix or rel_posix.endswith(hint.rstrip("/")) for hint in GENERATED_HINTS)


def index_filesystem(root: str | Path) -> FilesystemIndex:
    root_path = Path(root).resolve()
    patterns = _load_gitignore_patterns(root_path)
    files: list[FileRecord] = []
    dirs: dict[str, DirRecord] = {}
    included = 0
    excluded = 0
    notes = [
        "gitignore matching is best-effort (not full git semantics).",
        "Sensitive paths are inventoriable but content-blocked.",
    ]

    for dirpath, dirnames, filenames in os.walk(root_path):
        # prune denied dirs in-place
        dirnames[:] = [d for d in dirnames if not is_denied_dir(d)]
        rel_dir = os.path.relpath(dirpath, root_path)
        if rel_dir == ".":
            rel_dir = ""
        if rel_dir and _gitignore_match(rel_dir + "/", patterns):
            excluded += 1
            dirnames[:] = []
            continue
        if rel_dir:
            dirs.setdefault(
                rel_dir.replace("\\", "/"),
                DirRecord(path=rel_dir.replace("\\", "/")),
            )

        for name in filenames:
            full = Path(dirpath) / name
            rel = str(Path(rel_dir) / name).replace("\\", "/") if rel_dir else name
            if _gitignore_match(rel, patterns):
                excluded += 1
                continue
            sensitive = is_sensitive_path(rel)
            readable = may_read_content(rel) and not sensitive
            binary = _is_binary(full) if readable or not sensitive else True
            try:
                size = full.stat().st_size
            except OSError:
                excluded += 1
                continue
            record = FileRecord(
                path=rel,
                extension=full.suffix.lower(),
                size=size,
                content_hash=_hash_file(full, readable and not binary) if readable else None,
                is_binary=binary,
                ignored=False,
                generated=_generated(rel),
                sensitive=sensitive,
                content_readable=readable and not binary,
            )
            files.append(record)
            included += 1
            if rel_dir:
                key = rel_dir.replace("\\", "/")
                dirs[key].child_file_count += 1

    # directory child_dir counts
    for dpath, drec in list(dirs.items()):
        parent = str(Path(dpath).parent).replace("\\", "/")
        if parent in dirs and parent != dpath:
            dirs[parent].child_dir_count += 1

    return FilesystemIndex(
        files=sorted(files, key=lambda f: f.path),
        directories=sorted(dirs.values(), key=lambda d: d.path),
        included_count=included,
        excluded_count=excluded,
        notes=notes,
    )
