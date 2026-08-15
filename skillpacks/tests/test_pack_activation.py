"""Pack activation honesty tests."""

from __future__ import annotations

import unittest

from skillpacks.registry import load_registry
from skillpacks.sources.registry import load_source_registry


class PackActivationTests(unittest.TestCase):
    def test_external_packs_remain_unavailable(self) -> None:
        reg = load_registry()
        for sid in (
            "eos.skillpack.marketing.corey-haines",
            "eos.skillpack.quality.stop-slop",
            "eos.skillpack.design.ui-ux-pro-max",
        ):
            pack = reg.get(sid)
            assert pack is not None
            self.assertEqual(pack.status, "unavailable")
            self.assertFalse(pack.is_selectable())
        src = load_source_registry()
        for sid in (
            "eos.skillsource.marketing.corey-haines.placeholder",
            "eos.skillsource.quality.stop-slop.placeholder",
            "eos.skillsource.design.ui-ux-pro-max.placeholder",
        ):
            s = src.get(sid)
            assert s is not None
            self.assertEqual(s.status, "unavailable")
            self.assertIn("NEEDS_SOURCE", s.notes)

    def test_context_engineering_active_with_hash(self) -> None:
        pack = load_registry().get("eos.skillpack.context.engineering")
        assert pack is not None
        self.assertEqual(pack.status, "active")
        self.assertTrue(pack.is_selectable())
        src = load_source_registry().get("eos.skillsource.context.engineering.v1")
        assert src is not None
        self.assertEqual(src.status, "active")
        self.assertTrue(src.content_hash)


if __name__ == "__main__":
    unittest.main()
