---
id: eos.adaptation.cursor.engineering-os-agency
type: adaptation
title: Cursor Engineering OS Agency Adaptation
summary: Thin Cursor packaging for the Engineering OS capability-routing agency loop.
purpose: Let Cursor agents operate Engineering OS through a project skill without forking canonical knowledge.
audience: Engineers using Engineering OS inside Cursor
status: active
applicability: When Engineering OS is used from Cursor as the operator environment.
limits: Not the source of truth; not portable to other tools without re-packaging; not a replacement for foundation protocols.
domain: cursor
language: en
complexity: medium
tags:
  - cursor
  - adaptation
  - agency
inputs:
  - User request in Cursor
  - Engineering OS repository catalog
outputs:
  - Cursor-agent behavior aligned to Capability Routing Agency Loop
  - References to canonical Capabilities and fulfillment units
relationships:
  - type: references
    target: eos.skill.agency.capability-routing
  - type: references
    target: eos.capability.design.system-architecture
  - type: references
    target: eos.capability.security.review
  - type: references
    target: eos.capability.quality.test-planning
  - type: references
    target: eos.capability.operations.observability
---

# Cursor Engineering OS Agency Adaptation

## Packaging

Canonical procedure:

- `eos.skill.agency.capability-routing`

Cursor project skill entrypoint:

- `.cursor/skills/engineering-os-agency/SKILL.md`

## Rules

1. The Cursor skill must call into canonical Capabilities and units by ID.
2. Do not duplicate playbook methods inside the Cursor skill beyond routing instructions.
3. If Cursor-specific behavior is required, keep it here or in the project skill — never in foundation.
