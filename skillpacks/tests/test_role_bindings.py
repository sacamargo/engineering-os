"""Role binding tests."""

from __future__ import annotations

import unittest

from skillpacks.bindings import roles_for_skill, skills_for_role


class RoleBindingTests(unittest.TestCase):
    def test_ui_ux_roles(self) -> None:
        roles = roles_for_skill("eos.skillpack.design.ui-ux-pro-max")
        self.assertIn("eos.role.ui-ux-designer", roles)
        self.assertIn("eos.role.frontend-engineer", roles)

    def test_skill_not_equal_role(self) -> None:
        roles = roles_for_skill("eos.skillpack.marketing.corey-haines")
        self.assertTrue(all(r.startswith("eos.role.") for r in roles))
        self.assertFalse(any(r.startswith("eos.skillpack.") for r in roles))

    def test_role_may_use_multiple_skills(self) -> None:
        skills = skills_for_role("eos.role.technical-lead")
        self.assertGreaterEqual(len(skills), 2)


if __name__ == "__main__":
    unittest.main()
