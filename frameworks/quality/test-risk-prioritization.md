---
id: eos.framework.quality.test-risk-prioritization
type: framework
title: Test Risk Prioritization Framework
summary: A decision framework for ranking what to test first under time and risk constraints.
purpose: Make test triage explicit so teams do not confuse coverage theater with risk reduction.
audience: Engineers prioritizing validation work
status: active
applicability: When candidate test areas exist and must be ordered against risk, blast radius, and effort.
limits: Not a full test strategy method; not a coverage-percentage target system; not automation vendor guidance.
domain: quality
language: en
complexity: low
tags:
  - testing
  - risk
  - prioritization
principles:
  - P7
  - P9
  - P15
inputs:
  - Candidate test areas or scenarios
  - User/business impact context
  - Time and environment constraints
outputs:
  - Prioritized validation list
  - Deferred tests with rationale
  - Residual risk statement
---

# Test Risk Prioritization Framework

## Method

1. List candidate validation items.
2. Score each on impact, likelihood, detectability in production, and effort.
3. Classify as blocker / urgent / planned / deferred.
4. Record residual risk for deferred items.

## Anti-Patterns

- Prioritizing only what is easy to automate
- Using coverage % as the primary decision metric
- Deferring high-impact auth/payment journeys silently
