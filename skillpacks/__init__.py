"""Engineering OS Skill Integration Layer (skillpacks).

Phase 8: discoverable, contract-driven Integrated Skills.
Does not replace Capabilities, Roles, Agents, or knowledge-unit skills.
"""

from skillpacks.model import (
    CompositionRule,
    EscalationRule,
    SkillIO,
    SkillPack,
    SkillProvenance,
    SkillTrigger,
    SkillWorkflow,
    is_skillpack_id,
    skillpack_from_dict,
)
from skillpacks.registry import SkillRegistry, discover_skills, load_registry

__all__ = [
    "CompositionRule",
    "EscalationRule",
    "SkillIO",
    "SkillPack",
    "SkillProvenance",
    "SkillRegistry",
    "SkillTrigger",
    "SkillWorkflow",
    "discover_skills",
    "is_skillpack_id",
    "load_registry",
    "skillpack_from_dict",
]
