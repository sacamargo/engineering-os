---
id: eos.playbook.delivery.change-introduction
type: playbook
title: Change Introduction
summary: Playbook incorrectly owning capability relationships.
purpose: Trigger capability-only relationship rule.
audience: Testers
status: active
applicability: Fixture only
limits: Fixture only
inputs:
  - Change description
outputs:
  - Introduction plan
relationships:
  - type: fulfilled_by
    target: eos.skill.design.trade-off-analysis
---

Modules must not declare fulfilled_by.
