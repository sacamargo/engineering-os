---
id: eos.capability.security.review
type: capability
title: Application Security Review
summary: Route intents to review an application or system for security risks, weaknesses, and missing controls.
purpose: Provide a durable product entry point for security-review intents without owning a full security methodology.
audience: Engineers, security reviewers, and technical leads assessing application or system security posture
status: active
applicability: When the primary need is to evaluate an existing application, service, or system design for security risks, missing controls, trust-boundary weaknesses, and prioritized remediation guidance.
limits: Does not own penetration testing execution; does not replace a full AppSec program; does not perform incident response as the primary intent; does not implement vulnerability fixes; does not certify compliance; does not replace licensed security assessment where regulation or contract requires an accredited assessor.
domain: security
language: en
complexity: high
tags:
  - security
  - review
  - risk
  - controls
  - application-security
entry_signals:
  - Audit this application for security issues
  - Review this system for security vulnerabilities
  - Assess security risks in this design
  - What security controls are missing
  - Perform an application security review
  - Check this architecture for security weaknesses
  - Prioritize security findings for remediation
outcome_expectations: A structured security review with scoped findings, prioritized risks, missing-control gaps, and recommended next actions that distinguish review guidance from implementation or accredited assessment.
arbitration: Prefer the application security review playbook when the caller needs to structure an end-to-end review. Prefer the security risk prioritization framework when findings or candidate risks already exist and the need is to rank them. Use both when structuring the review and prioritizing findings are both required; do not treat either unit as a mandatory sequential pipeline.
relationships:
  - type: primary_fulfillment
    target: eos.playbook.security.application-review
  - type: fulfilled_by
    target: eos.framework.security.risk-prioritization
  - type: related_capability
    target: eos.capability.design.system-architecture
  - type: related_capability
    target: eos.capability.quality.test-planning
  - type: related_capability
    target: eos.capability.operations.observability
---

# Application Security Review

## Intent Class

This Capability represents the durable intent class:

> Evaluate an application or system to identify security risks, weaknesses, and missing controls, and produce prioritized recommendations.

Users typically ask in outcome language, in any spoken language. They should not need to name a security specialist. Demand-side phrasing includes audit, review, assess, find weaknesses, and prioritize security issues.

Engineering OS routes those intents here. Fulfillment knowledge supplies review method and risk-prioritization models.

## In Scope

- Scoping a security review of an application, service, or system design
- Identifying trust boundaries, likely weakness classes, and missing controls
- Producing prioritized findings and recommended next actions
- Distinguishing architectural security concerns from implementation defects
- Escalating when accredited assessment, legal, or compliance authority is required

## Out of Scope

- Designing a greenfield system architecture as the primary ask
- Writing or applying vulnerability patches as the primary ask
- Running a penetration test engagement end-to-end
- Incident response and forensics as the primary ask
- Performance optimization
- Claiming formal certification or compliance attestation

## Related Intent Classes

This Capability is often adjacent to System Architecture Design when a review targets architectural trust boundaries.

`related_capability` means soft co-relevance for future routing. It does **not** mean:

- security review requires architecture design first
- architecture design includes security review automatically
- a Capability execution DAG or call stack

## Fulfillment

Bound units:

| Unit | Role |
|---|---|
| `eos.playbook.security.application-review` | Primary method for structuring a security review |
| `eos.framework.security.risk-prioritization` | Decision model for ranking security risks and actions |

Additional units may be bound later without changing this Capability’s identity.
