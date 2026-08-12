---
id: eos.skill.agency.capability-routing
type: skill
title: Capability Routing Agency Loop
summary: Portable procedure to frame user intent, resolve Capability candidates, bind fulfillment units, and execute without inventing catalog offers.
purpose: Make Engineering OS operable as an agency entry loop across tools while preserving Intent Resolution invariants.
audience: AI runtimes and engineers operating Engineering OS
status: active
applicability: When a user asks Engineering OS to design, review, plan validation, define metrics, or otherwise fulfill engineering intents through the catalog.
limits: Not a full Orchestrator product; not allowed to invent Capabilities; not a substitute for professional/legal validation; not vendor-specific packaging.
domain: agency
language: en
complexity: high
tags:
  - agency
  - routing
  - orchestration-lite
principles:
  - P2
  - P5
  - P11
  - P12
  - P15
  - P19
inputs:
  - User utterance in any language
  - Optional repository or system context
  - Active Engineering OS Capability catalog
outputs:
  - Intent frame
  - Candidate and selected Capabilities
  - Fulfillment units used
  - Deliverable artifacts from bound methods
  - Explicit insufficient-coverage declarations when needed
relationships:
  - type: references
    target: eos.capability.design.system-architecture
  - type: references
    target: eos.capability.security.review
  - type: references
    target: eos.capability.quality.test-planning
  - type: references
    target: eos.capability.operations.observability
---

# Capability Routing Agency Loop

## Goal

Operate Engineering OS as an agency:

1. Understand the user intent
2. Resolve against existing Capabilities
3. Load fulfillment knowledge
4. Produce reviewable engineering outputs
5. Stop honestly when coverage is missing

## Procedure

### Step 1 — Frame

Build an intent frame with:

- desired outcome
- object of work
- intent class hint
- domain hints
- constraints
- risk signals
- multi-intent flag

Do not reduce this to keyword matching.

Follow `foundation/INTENT-RESOLUTION.md`.

### Step 2 — Route to candidates

Compare the frame to active Capability metadata:

- `summary`, `purpose`, `applicability`, `limits`, `entry_signals`

Emit candidates with rationale and confidence (`high|medium|low`).

### Step 3 — Select

Choose:

- `primary` Capability (or `null` if ambiguous/gap)
- `secondary` Capabilities when multi-intent is real
- `related_suggested` from `related_capability` links (soft only)

Ask clarifying questions when confidence is low or intents conflict.

### Step 4 — Bind fulfillment

From the primary Capability, resolve:

- `primary_fulfillment`
- `fulfilled_by`

Use Capability `arbitration` guidance. Do not invent unit IDs.

### Step 5 — Execute

Follow the selected playbook/framework method. Keep outputs inspectable.

For multi-Capability work (for example build a secure observable SaaS):

1. Resolve all relevant Capabilities
2. Sequence work by dependency of artifacts (architecture before deep security review of that architecture; test plan and observability against the architecture)
3. Keep each Capability’s method intact — do not merge into one mega-prompt

### Step 6 — Record

Always report:

```text
Intent frame
Candidates
Primary / Secondary
Related suggested
Fulfillment units used
Insufficient coverage (if any)
Clarifying questions (if any)
```

## Hard Rules

1. Never invent Capability IDs
2. Never pretend a gap is covered
3. Never skip Intent Resolution for catalog-scale work
4. Never treat adaptations/tools as source of truth over canonical units
5. Conversation may be any language; canonical knowledge stays English
