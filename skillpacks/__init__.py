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

__all__ = [
    "CompositionRule",
    "EscalationRule",
    "SkillIO",
    "SkillPack",
    "SkillProvenance",
    "SkillTrigger",
    "SkillWorkflow",
    "is_skillpack_id",
    "skillpack_from_dict",
]
