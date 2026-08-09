---
id: eos.playbook.design.uses-adaptation
type: playbook
title: Uses Adaptation
summary: Canonical unit depending on an adaptation.
purpose: Trigger adaptation dependency direction rule.
audience: Testers
status: draft
applicability: Fixture only
limits: Fixture only
inputs:
  - Context
outputs:
  - Packaged guidance
relationships:
  - type: depends_on
    target: eos.adaptation.cursor.packaging-example
---

Canonical must not depend_on adaptations.
