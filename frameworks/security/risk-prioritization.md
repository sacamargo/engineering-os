---
id: eos.framework.security.risk-prioritization
type: framework
title: Security Risk Prioritization Framework
summary: A decision framework for ranking security findings and choosing remediation urgency under constraints.
purpose: Make security prioritization inspectable by separating impact, likelihood, exposure, and validation burden.
audience: Engineers and reviewers deciding what security work to do first
status: active
applicability: When multiple security findings, risks, or candidate controls exist and a prioritized action order is required.
limits: Not a full security review method; not a CVSS calculator replacement; not a compliance scoring system; not an implementation playbook; not a substitute for accredited risk acceptance where required.
domain: security
language: en
complexity: medium
tags:
  - security
  - risk
  - prioritization
  - decision-making
principles:
  - P6
  - P7
  - P10
  - P15
  - P19
inputs:
  - Candidate security findings or risks
  - Asset and exposure context
  - Constraints on time, access, and blast radius
  - Risk tolerance and release constraints
outputs:
  - Prioritized finding list
  - Rationale for top actions
  - Explicit deferred or accepted risks
  - Escalations requiring higher authority
---

# Security Risk Prioritization Framework

## Purpose

This framework ranks **security findings or candidate risks** so teams can act under constraints.

It assumes findings already exist. If the review still needs to be structured, use `eos.playbook.security.application-review` first or in parallel for distinct workstreams.

## Core Idea

Security work fails when teams:

- treat all findings as equal
- optimize for novelty over exposure
- confuse theoretical weakness with reachable abuse
- hide risk acceptance instead of recording it

This framework forces prioritization into the open.

## Method

### 1. State the prioritization question

Examples:

- Which findings must be addressed before release?
- Which risks are acceptable temporarily with monitoring?
- Which items need deeper validation before claiming severity?

### 2. Normalize each candidate

For each finding/risk, capture:

| Field | Meaning |
|---|---|
| Claim | What is wrong or missing |
| Asset | What is endangered |
| Exposure | Who can reach it and from where |
| Impact | What happens if abused |
| Evidence strength | Observed, likely, or speculative |
| Fix class | Config, code, design, process, escalate |

Discard duplicates before ranking.

### 3. Score with transparent criteria

Use a small criterion set:

| Criterion | Asks |
|---|---|
| Reachability | Can an attacker or mistaken operator reach it now? |
| Impact severity | Confidentiality, integrity, availability, safety, or trust damage? |
| Exploit effort | How hard is abuse relative to the adversary model? |
| Detectability | Would abuse be noticed quickly? |
| Blast radius | How widely does failure propagate? |
| Remediation cost | Relative effort and risk of the fix itself |
| Uncertainty | How weak is the evidence? |

Do not pretend the scores are objective physics. Record assumptions.

### 4. Separate urgency classes

Map results into action classes:

1. **Blocker** — must address before the stated milestone
2. **Urgent** — schedule immediately after blockers
3. **Planned** — real risk, not release-blocking under stated tolerance
4. **Deferred with rationale** — accepted temporarily, with owner and revisit date
5. **Escalate** — needs security leadership, legal, or accredited assessment

### 5. Recommend with residuals

A complete prioritization includes:

- ordered actions
- why top items won
- what was deferred and why
- uncertainties that could reopen ranking
- authorities needed for formal risk acceptance when relevant

## Mini-Example

Candidates after an application review:

1. Public admin endpoint without strong auth
2. Missing security headers on a marketing page
3. Outdated transitive dependency with no known reachable path
4. Design concern: remote control plane shares overly broad credentials with local automation

Likely urgency shape under a typical release constraint:

- Blocker: item 1
- Urgent: item 4 if remote compromise can command local actuators
- Planned: item 3 if exposure is unproven but tracking is warranted
- Deferred/low: item 2 unless context elevates it

## Anti-Patterns

- Ranking by CVE count alone
- Inflating severity to force attention without exposure analysis
- Using the framework as a full review method
- Accepting risk silently with no owner or revisit

## Relationship to Other Units

This framework is independently usable wherever security findings need ranking.

It may fulfill `eos.capability.security.review` and later other Capabilities that need prioritization without owning this method.
