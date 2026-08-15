"""Compare two snapshots for incremental analysis support."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from codebase.snapshot import CodebaseSnapshot


@dataclass
class SnapshotDiff:
    from_snapshot_id: str
    to_snapshot_id: str
    files_added: list[str] = field(default_factory=list)
    files_removed: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    symbols_added: list[str] = field(default_factory=list)
    symbols_removed: list[str] = field(default_factory=list)
    dependencies_added: list[str] = field(default_factory=list)
    dependencies_removed: list[str] = field(default_factory=list)
    findings_new: list[str] = field(default_factory=list)
    findings_resolved: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _file_map(snapshot: CodebaseSnapshot) -> dict[str, str]:
    out: dict[str, str] = {}
    for f in snapshot.files:
        path = f.get("path", "")
        out[path] = f.get("content_hash") or ""
    return out


def _ids(items: list[dict[str, Any]], key: str = "id") -> set[str]:
    return {i.get(key, "") for i in items if i.get(key)}


def _dep_key(d: dict[str, Any]) -> str:
    return f"{d.get('source_path') or d.get('from')}->{d.get('target') or d.get('to')}:{d.get('kind')}"


def diff_snapshots(a: CodebaseSnapshot, b: CodebaseSnapshot) -> SnapshotDiff:
    fa, fb = _file_map(a), _file_map(b)
    added = sorted(set(fb) - set(fa))
    removed = sorted(set(fa) - set(fb))
    modified = sorted(p for p in set(fa) & set(fb) if fa[p] != fb[p] and (fa[p] or fb[p]))

    sa, sb = _ids(a.symbols), _ids(b.symbols)
    da = {_dep_key(d) for d in a.dependencies}
    db = {_dep_key(d) for d in b.dependencies}
    # findings compared by kind+location when id changes across runs
    def finding_key(f: dict[str, Any]) -> str:
        return f"{f.get('kind')}|{f.get('location')}|{f.get('explanation')}"

    fa_f = {finding_key(f) for f in a.findings}
    fb_f = {finding_key(f) for f in b.findings}

    return SnapshotDiff(
        from_snapshot_id=a.id,
        to_snapshot_id=b.id,
        files_added=added,
        files_removed=removed,
        files_modified=modified,
        symbols_added=sorted(sb - sa),
        symbols_removed=sorted(sa - sb),
        dependencies_added=sorted(db - da),
        dependencies_removed=sorted(da - db),
        findings_new=sorted(fb_f - fa_f),
        findings_resolved=sorted(fa_f - fb_f),
        notes=[
            "Incremental diff is structural; semantic equivalence is unknown.",
            "Finding identity uses kind|location|explanation because ids include hashes.",
        ],
    )
