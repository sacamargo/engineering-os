---
id: eos.framework.operations.signal-prioritization
type: framework
title: Signal Prioritization Framework
summary: A decision framework for ranking metrics and alerts by actionability and user impact.
purpose: Prevent observability sprawl by forcing prioritization of signals that change decisions.
audience: Engineers choosing what to measure and alert on first
status: active
applicability: When many candidate metrics or alerts exist and instrumentation effort must be ordered.
limits: Not a full observability design method; not a vendor pricing optimizer; not an incident retrospective template.
domain: operations
language: en
complexity: low
tags:
  - observability
  - metrics
  - prioritization
principles:
  - P6
  - P7
  - P9
inputs:
  - Candidate metrics or alerts
  - User-impact context
  - Instrumentation cost constraints
outputs:
  - Prioritized signal list
  - Deferred signals with rationale
  - Alert vs dashboard-only decisions
---

# Signal Prioritization Framework

## Criteria

| Criterion | Ask |
|---|---|
| User impact | Does this signal detect real user harm? |
| Actionability | Can a human act when it fires or moves? |
| Leading vs lagging | Does it warn early enough? |
| Noise risk | Will it train people to ignore alerts? |
| Cost | Is instrumentation/maintenance justified? |

## Classes

1. Must instrument now
2. Dashboard-only initially
3. Deferred
4. Reject as vanity
