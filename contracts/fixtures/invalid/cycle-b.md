---
id: eos.workflow.delivery.step-b
type: workflow
title: Step B
summary: Second node in a depends_on cycle.
purpose: Trigger cycle detection.
audience: Testers
status: draft
applicability: Fixture only
limits: Fixture only
inputs:
  - Context
outputs:
  - Intermediate state
relationships:
  - type: depends_on
    target: eos.workflow.delivery.step-a
---

Cycle member B.
