---
id: eos.capability.quality.test-planning
type: capability
title: Test Planning
summary: Route intents to plan how an application or change should be validated through testing.
purpose: Provide a durable entry point for test-planning intents without owning an entire QA bureaucracy.
audience: Engineers, tech leads, and reviewers responsible for validation strategy
status: active
applicability: When the primary need is to decide what to test, at what depth, with which risks covered, and what evidence is required before release or significant change.
limits: Does not execute the full test suite as a Capability; does not replace specialized performance or security testing engagements; does not invent product requirements; does not claim certification.
domain: quality
language: en
complexity: medium
tags:
  - testing
  - quality
  - validation
  - risk
entry_signals:
  - Plan the tests for this application
  - What should we test before release
  - Design a test strategy for this change
  - How do we validate this feature
  - Define acceptance tests and risk-based coverage
outcome_expectations: A reviewable test plan with scope, risk-based priorities, validation evidence, and explicit non-goals.
arbitration: Prefer the test planning playbook when shaping an overall validation strategy. Prefer the test risk prioritization framework when candidate test areas already exist and must be ranked under time constraints.
relationships:
  - type: primary_fulfillment
    target: eos.playbook.quality.test-planning
  - type: fulfilled_by
    target: eos.framework.quality.test-risk-prioritization
  - type: related_capability
    target: eos.capability.security.review
  - type: related_capability
    target: eos.capability.design.system-architecture
  - type: related_capability
    target: eos.capability.operations.observability
---

# Test Planning

## Intent Class

> Decide how to validate an application or change so important risks are covered with honest evidence.

## In Scope

- Risk-based test scoping
- Mapping critical user journeys and failure modes to validation
- Distinguishing unit, integration, end-to-end, and exploratory needs at planning level
- Defining release evidence and non-goals

## Out of Scope

- Writing every automated test as the primary ask
- Full security audit (use Application Security Review)
- Performance deep-dives as the only ask (may relate to Observability)
- Claiming production readiness without evidence
