"""Source model tests."""

from __future__ import annotations

import unittest

from skillpacks.sources.model import SkillSource, content_hash, is_source_id, source_from_dict


class SourceModelTests(unittest.TestCase):
    def test_id_and_hash(self) -> None:
        self.assertTrue(is_source_id("eos.skillsource.design.ui-ux-pro-max.v1"))
        self.assertFalse(is_source_id("eos.skillpack.design.ui-ux-pro-max"))
        self.assertEqual(len(content_hash(b"abc")), 64)

    def test_active_requires_hash_and_trust(self) -> None:
        src = SkillSource(
            source_id="eos.skillsource.context.engineering.v1",
            skillpack_id="eos.skillpack.context.engineering",
            source_type="eos_native",
            title="Context Engineering EOS",
            origin="engineering-os",
            locator="skillpacks/context_engineering.py",
            version="0.1.0",
            status="active",
            trust_level="untrusted",
            content_hash=None,
        )
        errs = src.validate_shape()
        self.assertTrue(any("content_hash" in e for e in errs))
        self.assertTrue(any("untrusted" in e for e in errs))

    def test_unavailable_placeholder(self) -> None:
        src = source_from_dict(
            {
                "source_id": "eos.skillsource.marketing.corey-haines.placeholder",
                "skillpack_id": "eos.skillpack.marketing.corey-haines",
                "source_type": "unavailable_placeholder",
                "title": "Marketing source missing",
                "origin": "external",
                "locator": "NEEDS_SOURCE",
                "version": "0.0.0",
                "status": "unavailable",
                "trust_level": "untrusted",
                "notes": ["NEEDS_SOURCE"],
            }
        )
        self.assertEqual(src.validate_shape(), [])


if __name__ == "__main__":
    unittest.main()
