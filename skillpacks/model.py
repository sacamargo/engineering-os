"""Canonical Integrated Skill (skillpack) model — Phase 8.

Skill ≠ Capability ≠ Role ≠ Agent ≠ Knowledge Unit ≠ Tool.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

SkillStatus = Literal["active", "experimental", "deprecated", "unavailable"]
CompositionKind = Literal["primary", "supporting", "transversal"]

SKILLPACK_ID_PREFIX = "eos.skillpack."


def is_skillpack_id(value: str) -> bool:
    """Validate eos.skillpack.<category>.<name> shape."""
    if not value.startswith(SKILLPACK_ID_PREFIX):
        return False
    rest = value[len(SKILLPACK_ID_PREFIX) :]
    parts = rest.split(".")
    if len(parts) != 2:
        return False
    return all(p and p[0].islower() and all(c.isalnum() or c == "-" for c in p) for p in parts)


@dataclass
class SkillProvenance:
    origin: str
    source: str
    version: str
    license: str = "unknown"
    adaptation_status: str = "none"  # none | adapted | eos-native
    modifications: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    unavailable_source_content: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SkillTrigger:
    """Structured applicability signal — not keyword-only routing."""

    signal_type: str  # intent_class | domain | artifact_kind | mode | negative
    value: str
    weight: float = 1.0
    polarity: str = "positive"  # positive | negative
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SkillIO:
    name: str
    description: str = ""
    required: bool = False
    artifact_kinds: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SkillWorkflow:
    id: str
    name: str
    mode: str = "default"
    description: str = ""
    steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EscalationRule:
    when: str
    action: str  # NEEDS_INPUT | NEEDS_HUMAN | NEEDS_SPECIALIST | NEEDS_SOURCE | APPROVAL_REQUIRED
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompositionRule:
    kind: CompositionKind
    with_skill_ids: list[str] = field(default_factory=list)
    notes: str = ""
    # Explicit: composition does not imply task DAG edges
    implies_task_dependency: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SkillPack:
    """First-class Integrated Skill definition."""

    id: str
    name: str
    version: str
    purpose: str
    category: str
    source: str
    provenance: SkillProvenance
    status: SkillStatus = "unavailable"
    triggers: list[SkillTrigger] = field(default_factory=list)
    inputs: list[SkillIO] = field(default_factory=list)
    outputs: list[SkillIO] = field(default_factory=list)
    required_context: list[str] = field(default_factory=list)
    knowledge_dependencies: list[str] = field(default_factory=list)
    tool_requirements: list[str] = field(default_factory=list)
    capability_relationships: list[str] = field(default_factory=list)
    role_relationships: list[str] = field(default_factory=list)
    agent_compatibility: list[str] = field(default_factory=list)
    workflows: list[SkillWorkflow] = field(default_factory=list)
    quality_gates: list[str] = field(default_factory=list)
    evidence_requirements: list[str] = field(default_factory=list)
    escalation_rules: list[EscalationRule] = field(default_factory=list)
    composition_rules: list[CompositionRule] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    # Security: never interpret as granted permissions
    cannot_grant_permissions: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

    def validate_shape(self) -> list[str]:
        errors: list[str] = []
        if not is_skillpack_id(self.id):
            errors.append(f"invalid skillpack id: {self.id}")
        if not self.name.strip():
            errors.append("name required")
        if not self.version.strip():
            errors.append("version required")
        if not self.purpose.strip():
            errors.append("purpose required")
        if not self.provenance.origin.strip():
            errors.append("provenance.origin required")
        if self.status == "unavailable" and not self.provenance.unavailable_source_content:
            errors.append("unavailable status requires provenance.unavailable_source_content=true")
        if self.status == "active" and self.provenance.unavailable_source_content:
            errors.append("active status cannot have unavailable_source_content")
        # Privilege elevation fields must never appear as grants
        for key in ("grants_permissions", "grants_tools", "bypass_gates", "auto_approve"):
            if key in self.metadata:
                errors.append(f"forbidden privilege field in metadata: {key}")
        return errors

    def is_selectable(self) -> bool:
        return self.status in ("active", "experimental") and not self.provenance.unavailable_source_content


def skillpack_from_dict(data: dict[str, Any]) -> SkillPack:
    prov_raw = data.get("provenance") or {}
    provenance = SkillProvenance(
        origin=str(prov_raw.get("origin", "")),
        source=str(prov_raw.get("source", data.get("source", ""))),
        version=str(prov_raw.get("version", data.get("version", ""))),
        license=str(prov_raw.get("license", "unknown")),
        adaptation_status=str(prov_raw.get("adaptation_status", "none")),
        modifications=list(prov_raw.get("modifications") or []),
        limitations=list(prov_raw.get("limitations") or []),
        unavailable_source_content=bool(prov_raw.get("unavailable_source_content", False)),
    )
    triggers = [
        SkillTrigger(
            signal_type=str(t.get("signal_type", "")),
            value=str(t.get("value", "")),
            weight=float(t.get("weight", 1.0)),
            polarity=str(t.get("polarity", "positive")),
            notes=str(t.get("notes", "")),
        )
        for t in (data.get("triggers") or [])
    ]
    def _ios(key: str) -> list[SkillIO]:
        return [
            SkillIO(
                name=str(i.get("name", "")),
                description=str(i.get("description", "")),
                required=bool(i.get("required", False)),
                artifact_kinds=list(i.get("artifact_kinds") or []),
            )
            for i in (data.get(key) or [])
        ]

    workflows = [
        SkillWorkflow(
            id=str(w.get("id", "")),
            name=str(w.get("name", "")),
            mode=str(w.get("mode", "default")),
            description=str(w.get("description", "")),
            steps=list(w.get("steps") or []),
        )
        for w in (data.get("workflows") or [])
    ]
    escalations = [
        EscalationRule(
            when=str(e.get("when", "")),
            action=str(e.get("action", "NEEDS_HUMAN")),
            reason=str(e.get("reason", "")),
        )
        for e in (data.get("escalation_rules") or [])
    ]
    composition = [
        CompositionRule(
            kind=str(c.get("kind", "supporting")),  # type: ignore[arg-type]
            with_skill_ids=list(c.get("with_skill_ids") or []),
            notes=str(c.get("notes", "")),
            implies_task_dependency=bool(c.get("implies_task_dependency", False)),
        )
        for c in (data.get("composition_rules") or [])
    ]
    return SkillPack(
        id=str(data["id"]),
        name=str(data.get("name", "")),
        version=str(data.get("version", "")),
        purpose=str(data.get("purpose", "")),
        category=str(data.get("category", "")),
        source=str(data.get("source", "")),
        provenance=provenance,
        status=str(data.get("status", "unavailable")),  # type: ignore[arg-type]
        triggers=triggers,
        inputs=_ios("inputs"),
        outputs=_ios("outputs"),
        required_context=list(data.get("required_context") or []),
        knowledge_dependencies=list(data.get("knowledge_dependencies") or []),
        tool_requirements=list(data.get("tool_requirements") or []),
        capability_relationships=list(data.get("capability_relationships") or []),
        role_relationships=list(data.get("role_relationships") or []),
        agent_compatibility=list(data.get("agent_compatibility") or []),
        workflows=workflows,
        quality_gates=list(data.get("quality_gates") or []),
        evidence_requirements=list(data.get("evidence_requirements") or []),
        escalation_rules=escalations,
        composition_rules=composition,
        constraints=list(data.get("constraints") or []),
        limitations=list(data.get("limitations") or []),
        cannot_grant_permissions=bool(data.get("cannot_grant_permissions", True)),
        metadata=dict(data.get("metadata") or {}),
    )
