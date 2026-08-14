"""Knowledge Resolution — progressive disclosure of Knowledge Units.

Select REQUIRED / RECOMMENDED / OPTIONAL units for selected Capabilities.
Does not load entire repository bodies into context.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from orchestration.capability.arbitration import ArbitrationResult
from orchestration.catalog import CatalogUnit, load_catalog

Priority = Literal["required", "recommended", "optional"]


@dataclass
class KnowledgeSelection:
    unit_id: str
    priority: Priority
    capability_id: str
    reason: str
    path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class KnowledgeResolution:
    selected: list[KnowledgeSelection]
    deferred_body_loads: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected": [s.to_dict() for s in self.selected],
            "deferred_body_loads": self.deferred_body_loads,
            "notes": self.notes,
            "unit_ids": [s.unit_id for s in self.selected],
        }


def resolve_knowledge(
    arbitration: ArbitrationResult,
    repo_root: Path | None = None,
    catalog: dict[str, CatalogUnit] | None = None,
) -> KnowledgeResolution:
    units = catalog if catalog is not None else load_catalog(repo_root)
    selected: list[KnowledgeSelection] = []
    notes = [
        "Progressive disclosure: metadata selected now; bodies load when tasks execute.",
        "Do not dump the entire repository into planner context.",
    ]

    for cap_id in arbitration.selected:
        cap = units.get(cap_id)
        if not cap:
            continue
        for rel in cap.relationships:
            rel_type = rel.get("type")
            target = rel.get("target")
            if not target or target not in units:
                continue
            if rel_type == "primary_fulfillment":
                priority: Priority = "required"
            elif rel_type == "fulfilled_by":
                priority = "recommended"
            else:
                continue
            selected.append(
                KnowledgeSelection(
                    unit_id=target,
                    priority=priority,
                    capability_id=cap_id,
                    reason=f"{rel_type} binding",
                    path=units[target].path,
                )
            )

    # Defer body loads — only IDs/paths now
    deferred = [s.unit_id for s in selected]
    return KnowledgeResolution(selected=selected, deferred_body_loads=deferred, notes=notes)
