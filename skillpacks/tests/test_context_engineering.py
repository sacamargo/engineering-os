"""Context Engineering tests."""

from __future__ import annotations

import unittest

from skillpacks.context_engineering import assemble_context, invalidate_context
from skillpacks.registry import load_registry


class ContextEngineeringTests(unittest.TestCase):
    def test_registered_selectable(self) -> None:
        pack = load_registry().get("eos.skillpack.context.engineering")
        assert pack is not None
        self.assertEqual(pack.status, "active")
        self.assertTrue(pack.is_selectable())
        self.assertEqual(pack.provenance.adaptation_status, "eos-native")

    def test_assembles_relevant_excludes_irrelevant(self) -> None:
        ctx = assemble_context(
            intent={"utterance": "Build app"},
            task={"id": "t1", "title": "API"},
            skill_ids=["eos.skillpack.context.engineering"],
            tool_permissions=["READ"],
            artifacts=[
                {"path": "src/api.py", "content": "ok"},
                {"path": "docs/unrelated-marketing.md", "content": "nope"},
            ],
            codebase_evidence={
                "files": ["src/api.py", "src/ui.tsx", "vendor/huge"],
                "entire_repository": "FORBIDDEN",
            },
            task_relevance_paths=["src/api"],
            max_chars=5000,
        )
        self.assertIn("intent", ctx.included_keys)
        self.assertIn("tool_permissions", ctx.included_keys)
        self.assertFalse(ctx.to_dict()["full_repo_dumped"])
        self.assertNotIn("entire_repository", str(ctx.to_dict()))
        # unrelated artifact excluded by path filter
        self.assertTrue(any(k.startswith("artifact_excluded") for k in ctx.excluded_keys) or "artifact_1" in ctx.excluded_keys)

    def test_invalidation(self) -> None:
        ctx = assemble_context(intent={"utterance": "x"}, task={"id": "1"}, prior_decisions=[{"id": "d1"}])
        self.assertIn("prior_decisions", ctx.included_keys)
        nxt = invalidate_context(ctx, ["prior_decisions"])
        self.assertNotIn("prior_decisions", nxt.included_keys)
        self.assertIn("prior_decisions", nxt.invalidated_keys)

    def test_budget_compression(self) -> None:
        big = {"blob": "x" * 10_000}
        ctx = assemble_context(
            intent=big,
            task=big,
            evidence=[big, big, big],
            max_chars=500,
            max_items=3,
        )
        self.assertTrue(ctx.truncated or ctx.used_chars <= 500)
        self.assertLessEqual(len(ctx.included_keys), 3)

    def test_not_routing_shortcut_constraint(self) -> None:
        pack = load_registry().get("eos.skillpack.context.engineering")
        assert pack is not None
        self.assertIn("not_a_routing_shortcut", pack.constraints)


if __name__ == "__main__":
    unittest.main()
