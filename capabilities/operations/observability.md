---
id: eos.capability.operations.observability
type: capability
title: Observability and Metrics Design
summary: Route intents to design how an application should be observed through metrics, logs, traces, and actionable alerts.
purpose: Provide a durable entry point for observability and metrics intents without owning a full SRE platform.
audience: Engineers and operators responsible for production insight and service health
status: active
applicability: When the primary need is to define what to measure, which signals indicate health, and how teams detect and diagnose failure in production or pre-production.
limits: Does not implement a full observability vendor stack; does not replace incident response command; does not perform deep performance engineering as a complete practice; does not invent SLOs without product context.
domain: operations
language: en
complexity: high
tags:
  - observability
  - metrics
  - monitoring
  - reliability
entry_signals:
  - What metrics should this application expose
  - Design monitoring and alerts for this service
  - Define SLIs and SLOs for this system
  - How will we know this is healthy in production
  - Add observability to this architecture
outcome_expectations: A reviewable observability design with golden signals, key metrics, alert intent, and explicit blind spots.
arbitration: Prefer the observability design playbook when shaping the overall measurement model. Prefer the signal prioritization framework when candidate metrics/alerts must be ranked.
relationships:
  - type: primary_fulfillment
    target: eos.playbook.operations.observability-design
  - type: fulfilled_by
    target: eos.framework.operations.signal-prioritization
  - type: related_capability
    target: eos.capability.design.system-architecture
  - type: related_capability
    target: eos.capability.quality.test-planning
  - type: related_capability
    target: eos.capability.security.review
---

# Observability and Metrics Design

## Intent Class

> Decide how the system should expose health, performance, and failure signals that humans can act on.

## In Scope

- SLI/SLO candidates and golden signals
- Metric, log, and trace intent at design level
- Alert purposefulness and noise control
- Blind-spot declaration

## Out of Scope

- Vendor-specific dashboard clickops as methodology
- Full incident command process
- Security audit as primary ask
- Claiming reliability without operational evidence
