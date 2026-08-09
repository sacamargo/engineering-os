---
id: eos.framework.design.architecture-trade-offs
type: framework
title: Architecture Trade-off Framework
summary: A decision framework for comparing system-architecture options under explicit criteria and constraints.
purpose: Make architectural choices inspectable by forcing criteria, options, and consequences into the open.
audience: Engineers and architects choosing among viable architecture options
status: active
applicability: When two or more credible architecture options exist and a decision must be reasoned, recorded, and reviewed, including local-versus-remote placement, coupling, and failure strategy.
limits: Not a discovery method for inventing the initial architecture shape; not a scoring cult; not a substitute for measurement where evidence is required; not professional certification of physical designs.
domain: design
language: en
complexity: medium
tags:
  - architecture
  - trade-offs
  - decision-making
  - reliability
  - security
principles:
  - P6
  - P7
  - P8
  - P15
  - P19
inputs:
  - Decision question
  - Constraints and non-negotiables
  - Candidate architecture options
  - Success criteria and risk tolerances
outputs:
  - Criteria set with priorities
  - Comparison of options against criteria
  - Recommended option with explicit rejected alternatives
  - Residual risks and follow-up validations
---

# Architecture Trade-off Framework

## Purpose

This framework helps choose among **viable system-architecture options**.

It assumes candidates already exist. If the architecture still needs to be shaped from intent, use `eos.playbook.design.system-architecture` first (or in parallel for distinct sub-decisions).

## Core Idea

Architectural decisions fail when teams:

- argue about products before responsibilities
- optimize one criterion (usually convenience) in silence
- forget degraded-mode behavior
- confuse software architecture recommendations with professional physical validation

This framework forces those issues into an explicit comparison.

## Method

### 1. State the decision question

Write one question.

Examples:

- Where should authoritative control live for facility automation?
- How should remote access relate to local autonomy?
- Should identity be edge-authoritative or cloud-authoritative under partition?

If you cannot state the question, you are not ready to compare options.

### 2. Lock constraints before preferences

Separate:

| Class | Meaning |
|---|---|
| Non-negotiable constraints | Must hold or the option is invalid |
| High-priority criteria | Strongly preferred |
| Secondary criteria | Useful but not decisive |
| Explicit non-goals | What this decision will not optimize |

For connectivity-sensitive systems, “local operation during internet loss” is usually a constraint, not a preference.

### 3. Name only viable options

Keep the option set small (typically 2–4). Discard options that violate constraints before scoring rhetoric begins.

Each option needs:

- a one-sentence structure statement
- where authority lives
- what fails first
- what remains operable under partition

### 4. Compare on architecture criteria

Use criteria that expose real trade-offs. A practical default set:

| Criterion | Asks |
|---|---|
| Constraint fit | Does the option satisfy non-negotiables? |
| Boundary clarity | Are responsibilities and trust boundaries obvious? |
| Local autonomy | What works with no internet / limited network? |
| Remote operability | What can authorized users do when connected? |
| Failure behavior | Are degraded modes explicit and safe? |
| Security exposure | What new attack surface appears, especially via remote paths? |
| Operability | Can on-site operators understand and recover the system? |
| Evolability | Can parts change without rewriting the whole architecture? |
| Validation burden | What requires professional physical/regulatory validation before claim of readiness? |
| Complexity cost | What cognitive and operational load does the option add? |

Do not pretend all criteria are equal. Record priorities.

### 5. Recommend with residuals

A complete recommendation includes:

1. Selected option
2. Why it wins on the prioritized criteria
3. Why rejected options lose
4. Residual risks
5. Tests or validations still required
6. Escapes: conditions that would reopen the decision

## Worked Mini-Example — Local Authority vs Cloud Authority

Decision question:

> For a padel-court facility automation system that must operate without internet, where should authoritative control live?

Constraints:

- Local operation without internet is mandatory
- Authorized remote control is required when connectivity exists
- Physical actuation implies professional validation outside this framework’s authority

Candidate options:

1. **Edge-authoritative controller** with remote access gateway
2. **Cloud-authoritative control** with local cache/failover scripts
3. **Per-device autonomy only** with no facility-level edge coordinator

Constraint filter:

- Option 2 is usually invalid if failover is speculative and cloud remains the real authority.
- Option 3 may keep devices alive but often fails facility-level policy, coordinated access, and operability.

Likely recommendation shape:

- Prefer Option 1 when coordinated local policy matters.
- Reject Option 2 when offline operation is a hard constraint.
- Consider Option 3 only for very small scopes with weak coordination needs.

Residual risks to record:

- remote-plane compromise
- edge controller single point of failure
- ambiguous command precedence if local and remote diverge
- physical installation and safety certification still requiring qualified professionals

## Anti-Patterns

- Scoring options after a favorite product was already chosen
- Treating “smart home convenience” as equal to “offline operability” when offline is mandatory
- Using the framework to rubber-stamp unsafe physical designs
- Expanding into a full architecture-shaping playbook inside the comparison table

## Relationship to Other Units

This framework is independently usable for architecture decisions in many domains.

It may fulfill `eos.capability.design.system-architecture` and, later, other Capabilities that need structured architectural choice without owning this method.
