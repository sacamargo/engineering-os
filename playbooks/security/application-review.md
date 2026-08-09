---
id: eos.playbook.security.application-review
type: playbook
title: Application Security Review
summary: A reusable method for structuring an application or system security review into scoped findings and next actions.
purpose: Enable coherent security reviews without dumping vulnerability catalogs or pretending to be a penetration-test engagement.
audience: Engineers and reviewers assessing application or system security posture
status: active
applicability: When an existing application, service, API, or system design needs a structured security review with clear scope, findings, and follow-ups.
limits: Not a penetration-test playbook; not a compliance certification method; not a vulnerability encyclopedia; not an implementation guide for fixing every finding; not incident response.
domain: security
language: en
complexity: high
tags:
  - security
  - review
  - application-security
  - trust-boundaries
principles:
  - P1
  - P6
  - P7
  - P10
  - P11
  - P15
inputs:
  - Review objective and urgency
  - System or application context under review
  - Known trust boundaries and sensitive assets
  - Constraints on access, time, and evidence available
outputs:
  - Review scope and non-goals
  - Structured findings with evidence notes
  - Missing-control observations
  - Recommended next actions and escalation points
relationships:
  - type: references
    target: eos.framework.security.risk-prioritization
---

# Application Security Review

## Purpose

This playbook structures an **application security review**.

It helps a reviewer:

- define scope and non-goals
- examine trust boundaries and sensitive assets
- identify weakness classes and missing controls
- produce findings that can be prioritized and acted on

It does **not** replace accredited assessments, penetration-test execution, or implementation work.

## When to Use

Strong fit:

- “Audit this application for security issues”
- “Review this service for missing controls”
- “Assess whether this design introduces security risks”
- Pre-release or change-driven security reviews with limited time

Weak fit:

- “Design the architecture for this system” as the primary ask
- “Fix this authentication bug now” as the primary ask
- Full red-team / penetration-test campaigns
- Live incident containment

## Method

### 1. Frame the review

Capture:

1. What is being reviewed (app, API, service, design, change)
2. Why now (release, incident near-miss, due diligence, architecture concern)
3. Sensitive assets and abuse scenarios that matter
4. Access and evidence constraints
5. Explicit non-goals

Translate user language into review concerns. Canonical knowledge remains English; conversation may be any language.

### 2. Define scope and depth

State:

- in-scope components and interfaces
- out-of-scope components
- review depth (design review, code-assisted review, config review, mixed)
- time box

A useful review with honest scope beats an unbounded vulnerability dump.

### 3. Map trust boundaries and assets

Identify:

- actors (users, admins, services, third parties)
- trust boundaries (client/server, service/service, admin planes, remote access)
- sensitive assets (credentials, personal data, payments, control actions)
- assumptions that, if false, become findings

### 4. Examine control coverage

For each important boundary or asset, ask what controls exist for:

- authentication
- authorization
- session/token handling
- input/output trust
- secrets handling
- cryptography in transit and at rest where relevant
- logging and abuse detection
- dependency and supply-chain exposure at a reviewable level
- administrative and break-glass paths

Do not expand this into an OWASP encyclopedia. Use the categories to find gaps relative to the system under review.

### 5. Record findings as reviewable claims

Each finding should include:

- what was observed or inferred
- why it matters
- affected boundary or asset
- confidence (observed evidence vs design inference)
- suggested next action class (investigate, mitigate, accept with rationale, escalate)

### 6. Separate review from implementation and certification

This playbook produces review guidance.

It must not claim:

- the system is “secure”
- compliance is achieved
- patches have been correctly applied

If regulation or contract requires an accredited assessor, say so explicitly.

### 7. Hand off prioritization when needed

When many findings compete, use `eos.framework.security.risk-prioritization` rather than inventing an ad-hoc ranking inside the narrative.

## Quality Bar

Good output:

- clear scope and non-goals
- findings tied to boundaries/assets
- prioritized next actions or an explicit handoff to prioritization
- honest confidence levels
- escalation where professional assessment is required

Poor output:

- unbounded CVE laundry lists
- tool-vendor lock-in framed as methodology
- “fix everything” without prioritization
- architecture redesign disguised as a security review without stating the intent shift
