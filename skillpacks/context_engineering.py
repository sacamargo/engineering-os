"""EOS-native Context Engineering — vendor-neutral context assembly.

More context ≠ better context. Never dump the entire repository.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any

CONTEXT_SKILL_ID = "eos.skillpack.context.engineering"
DEFAULT_MAX_ITEMS = 24
DEFAULT_MAX_CHARS = 50_000


@dataclass
class ContextItem:
    key: str
    kind: str
    content: Any
    relevance: float
    provenance: str
    fresh: bool = True
    included: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AssembledContext:
    skill_id: str
    skill_version: str
    items: list[ContextItem]
    included_keys: list[str]
    excluded_keys: list[str]
    invalidated_keys: list[str]
    budget_chars: int
    used_chars: int
    truncated: bool
    notes: list[str] = field(default_factory=list)
    assembled_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "skill_version": self.skill_version,
            "items": [i.to_dict() for i in self.items if i.included],
            "included_keys": list(self.included_keys),
            "excluded_keys": list(self.excluded_keys),
            "invalidated_keys": list(self.invalidated_keys),
            "budget_chars": self.budget_chars,
            "used_chars": self.used_chars,
            "truncated": self.truncated,
            "notes": list(self.notes),
            "assembled_at": self.assembled_at,
            "full_repo_dumped": False,
        }


def _size(content: Any) -> int:
    return len(str(content))


def assemble_context(
    *,
    intent: dict[str, Any] | None = None,
    task: dict[str, Any] | None = None,
    capability_ids: list[str] | None = None,
    skill_ids: list[str] | None = None,
    role_ids: list[str] | None = None,
    artifacts: list[dict[str, Any]] | None = None,
    prior_decisions: list[dict[str, Any]] | None = None,
    evidence: list[dict[str, Any]] | None = None,
    constraints: list[str] | None = None,
    failures: list[dict[str, Any]] | None = None,
    codebase_evidence: dict[str, Any] | None = None,
    tool_permissions: list[str] | None = None,
    unresolved_questions: list[str] | None = None,
    stale_keys: list[str] | None = None,
    skill_version: str = "0.1.0",
    max_items: int = DEFAULT_MAX_ITEMS,
    max_chars: int = DEFAULT_MAX_CHARS,
    task_relevance_paths: list[str] | None = None,
) -> AssembledContext:
    """Assemble prioritized context with provenance; exclude irrelevant and stale items."""
    candidates: list[ContextItem] = []

    def add(key: str, kind: str, content: Any, relevance: float, provenance: str, fresh: bool = True) -> None:
        if content is None or content == "" or content == [] or content == {}:
            return
        candidates.append(
            ContextItem(
                key=key,
                kind=kind,
                content=content,
                relevance=relevance,
                provenance=provenance,
                fresh=fresh,
            )
        )

    add("intent", "intent", intent, 1.0, "orchestrator.intent")
    add("task", "task", task, 1.0, "execution.task")
    add("capabilities", "capability", capability_ids, 0.9, "orchestrator.capability")
    add("skills", "skill", skill_ids, 0.85, "skillpacks.registry")
    add("roles", "role", role_ids, 0.8, "orchestrator.role")
    add("constraints", "constraint", constraints, 0.9, "intent.constraints")
    add("tool_permissions", "permission", tool_permissions, 0.95, "agent.permissions")
    add("unresolved_questions", "question", unresolved_questions, 0.7, "intent.clarifying")
    add("prior_decisions", "decision", prior_decisions, 0.75, "execution.decisions")
    add("evidence", "evidence", evidence, 0.8, "execution.evidence")
    add("failures", "failure", failures, 0.85, "execution.failures")

    # Codebase evidence: only relevant paths / summary — never full tree dump
    if codebase_evidence:
        relevant = dict(codebase_evidence)
        if task_relevance_paths:
            files = relevant.get("files") or relevant.get("relevant_files") or []
            if isinstance(files, list):
                filtered = [f for f in files if any(str(f).startswith(p) or p in str(f) for p in task_relevance_paths)]
                relevant = {**relevant, "files": filtered, "filtered_by": task_relevance_paths}
        # Drop obvious full-dump keys
        for dump_key in ("all_files", "entire_repository", "full_tree", "raw_repo"):
            relevant.pop(dump_key, None)
        add("codebase_evidence", "codebase", relevant, 0.7, "codebase.intelligence")

    for i, art in enumerate(artifacts or []):
        # Exclude artifacts unrelated to task paths when paths provided
        path = str(art.get("path") or "")
        if task_relevance_paths and path and not any(path.startswith(p) or p in path for p in task_relevance_paths):
            add(f"artifact_excluded_{i}", "artifact", art, 0.05, "artifact.store", fresh=True)
            continue
        add(f"artifact_{i}", "artifact", art, 0.65, "artifact.store")

    stale = set(stale_keys or [])
    invalidated: list[str] = []
    for item in candidates:
        if item.key in stale or not item.fresh:
            invalidated.append(item.key)
            item.fresh = False

    # Prioritize by relevance; drop low relevance and stale
    ranked = sorted(candidates, key=lambda x: x.relevance, reverse=True)
    included: list[ContextItem] = []
    excluded: list[str] = []
    used = 0
    truncated = False
    for item in ranked:
        if item.key in stale or item.relevance < 0.2:
            excluded.append(item.key)
            continue
        size = _size(item.content)
        if len(included) >= max_items or used + size > max_chars:
            excluded.append(item.key)
            truncated = True
            continue
        item.included = True
        included.append(item)
        used += size

    notes = [
        "More context ≠ better context",
        "Full repository dump is forbidden",
        "Context Engineering is transversal support, not a routing shortcut",
        "Vendor-neutral EOS-native assembly (Cursor-compatible)",
    ]
    if truncated:
        notes.append("Context compressed to budget")

    return AssembledContext(
        skill_id=CONTEXT_SKILL_ID,
        skill_version=skill_version,
        items=included,
        included_keys=[i.key for i in included],
        excluded_keys=excluded,
        invalidated_keys=invalidated,
        budget_chars=max_chars,
        used_chars=used,
        truncated=truncated,
        notes=notes,
    )


def invalidate_context(assembled: AssembledContext, keys: list[str]) -> AssembledContext:
    """Mark keys stale and rebuild exclusion list."""
    stale = set(keys) | set(assembled.invalidated_keys)
    kept = [i for i in assembled.items if i.key not in stale]
    for i in kept:
        i.included = True
    return AssembledContext(
        skill_id=assembled.skill_id,
        skill_version=assembled.skill_version,
        items=kept,
        included_keys=[i.key for i in kept],
        excluded_keys=list(dict.fromkeys([*assembled.excluded_keys, *keys])),
        invalidated_keys=sorted(stale),
        budget_chars=assembled.budget_chars,
        used_chars=sum(_size(i.content) for i in kept),
        truncated=assembled.truncated,
        notes=[*assembled.notes, f"Invalidated: {keys}"],
    )
