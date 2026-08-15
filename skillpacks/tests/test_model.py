"""Tests for canonical Skillpack model."""

from __future__ import annotations

import unittest

from skillpacks.model import (
    SkillPack,
    SkillProvenance,
    is_skillpack_id,
    skillpack_from_dict,
)


class SkillModelTests(unittest.TestCase):
    def test_id_shape(self) -> None:
        self.assertTrue(is_skillpack_id("eos.skillpack.design.ui-ux-pro-max"))
        self.assertFalse(is_skillpack_id("eos.skill.agency.capability-routing"))
        self.assertFalse(is_skillpack_id("eos.skillpack.Bad.ID"))

    def test_unavailable_requires_flag(self) -> None:
        pack = SkillPack(
            id="eos.skillpack.marketing.corey-haines",
            name="Marketing Skills",
            version="0.0.0",
            purpose="Marketing methodology pack",
            category="marketing",
            source="unavailable",
            provenance=SkillProvenance(
                origin="external",
                source="unavailable",
                version="0.0.0",
                unavailable_source_content=False,
            ),
            status="unavailable",
        )
        errs = pack.validate_shape()
        self.assertTrue(any("unavailable_source_content" in e for e in errs))

    def test_forbidden_privilege_metadata(self) -> None:
        pack = skillpack_from_dict(
            {
                "id": "eos.skillpack.quality.stop-slop",
                "name": "Stop Slop",
                "version": "0.0.0",
                "purpose": "Quality review",
                "category": "quality",
                "source": "unavailable",
                "status": "unavailable",
                "provenance": {
                    "origin": "external",
                    "source": "unavailable",
                    "version": "0.0.0",
                    "unavailable_source_content": True,
                },
                "metadata": {"grants_permissions": ["DEPLOY_EXECUTE"]},
            }
        )
        errs = pack.validate_shape()
        self.assertTrue(any("grants_permissions" in e for e in errs))
        self.assertFalse(pack.is_selectable())

    def test_skill_is_not_agent(self) -> None:
        pack = skillpack_from_dict(
            {
                "id": "eos.skillpack.context.engineering",
                "name": "Context Engineering",
                "version": "0.1.0",
                "purpose": "Assemble relevant agent context",
                "category": "context",
                "source": "skillpacks/packs/context-engineering",
                "status": "experimental",
                "provenance": {
                    "origin": "engineering-os",
                    "source": "eos-native",
                    "version": "0.1.0",
                    "adaptation_status": "eos-native",
                    "license": "unknown",
                    "unavailable_source_content": False,
                },
                "agent_compatibility": ["coding", "analysis"],
            }
        )
        self.assertEqual(pack.validate_shape(), [])
        self.assertTrue(pack.is_selectable())
        # Model carries compatibility hints only — not an agent identity
        self.assertNotIn("agent_id", pack.to_dict())


if __name__ == "__main__":
    unittest.main()
