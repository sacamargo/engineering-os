---
id: eos.playbook.quality.test-planning
type: playbook
title: Test Planning
summary: A reusable method for building a risk-based test plan for an application or change.
purpose: Produce a coherent validation plan without turning testing into endless ceremony.
audience: Engineers and leads defining validation strategy
status: active
applicability: When a feature, system, or release needs a clear plan for what to test and why.
limits: Not a complete automation framework guide; not a security pentest plan; not a substitute for missing product requirements.
domain: quality
language: en
complexity: medium
tags:
  - testing
  - quality
  - planning
principles:
  - P1
  - P9
  - P10
  - P12
  - P15
inputs:
  - System or change under validation
  - Critical user journeys and business risks
  - Time and environment constraints
  - Known quality or security concerns
outputs:
  - Test scope and non-goals
  - Risk-ordered validation focus areas
  - Evidence expected before release
  - Open questions and escalations
relationships:
  - type: references
    target: eos.framework.quality.test-risk-prioritization
---

# Test Planning

## Purpose

Shape a **risk-based test plan**: what must be validated, why, and what evidence is enough.

## Method

### 1. Frame the validation goal

Capture the change, users affected, and the decision the tests must support (ship, hold, narrow scope).

### 2. Identify critical journeys and failure modes

List journeys that create revenue, trust, safety, or irreversible side effects. Pair each with likely failures.

### 3. Choose validation layers intentionally

Decide where unit, integration, contract, end-to-end, manual exploratory, or operational checks belong. Avoid “test everything everywhere.”

### 4. Define evidence

State what passing means: assertions, scenarios, data conditions, environments, and sign-off owners.

### 5. Prioritize under constraints

Use `eos.framework.quality.test-risk-prioritization` when time forces ranking.

### 6. Separate planning from adjacent Capabilities

- Security-specific audits → Application Security Review
- Metrics/SLO design → Observability
- Architecture gaps discovered while planning → System Architecture Design as related work, not a silent takeover
