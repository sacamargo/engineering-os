---
id: eos.playbook.operations.observability-design
type: playbook
title: Observability Design
summary: A reusable method for designing metrics, signals, and alert intent for an application or service.
purpose: Make production health inspectable without drowning teams in vanity metrics.
audience: Engineers designing operational visibility
status: active
applicability: When a system needs a coherent observability model tied to user journeys and failure modes.
limits: Not a vendor setup manual; not a complete SRE operating handbook; not a performance lab methodology.
domain: operations
language: en
complexity: high
tags:
  - observability
  - metrics
  - monitoring
principles:
  - P8
  - P9
  - P10
  - P15
inputs:
  - System architecture and critical journeys
  - Reliability or latency expectations
  - Operational ownership model
  - Known failure modes
outputs:
  - Golden signals and key metrics
  - Alert intent and non-alert noise boundaries
  - Diagnosis starting points
  - Declared blind spots
relationships:
  - type: references
    target: eos.framework.operations.signal-prioritization
---

# Observability Design

## Method

### 1. Anchor on user journeys and failure modes

Metrics exist to detect harm to users or the business, not to decorate dashboards.

### 2. Define golden signals

For each critical service boundary, define latency, traffic, errors, and saturation (or domain equivalents).

### 3. Distinguish SLI, metric, and alert

- SLI: quantitative measure of user-facing reliability
- Metric: instrumentation that supports SLIs and diagnosis
- Alert: human interrupt only when action is required

### 4. Design diagnosis paths

For each high-severity alert intent, state the first checks an on-call should perform.

### 5. Prioritize signals

Use `eos.framework.operations.signal-prioritization` when the candidate set is large.

### 6. Declare blind spots

Explicit unknowns are better than false confidence.
