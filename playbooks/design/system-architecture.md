---
id: eos.playbook.design.system-architecture
type: playbook
title: System Architecture Shaping
summary: A reusable method for shaping a system architecture from goals, constraints, and failure expectations.
purpose: Enable coherent architecture proposals without collapsing into implementation or professional physical design.
audience: Engineers and architects responsible for system structure decisions
status: active
applicability: When a system needs an architecture shaped from intent, especially systems with mixed local operation, remote access, integration boundaries, and explicit failure expectations.
limits: Not a coding guide; not an electrical or installation manual; not a substitute for licensed professional validation of physical, safety-critical, or regulated work; not a complete security audit method.
domain: design
language: en
complexity: high
tags:
  - architecture
  - system-design
  - edge
  - reliability
  - security
principles:
  - P1
  - P6
  - P8
  - P10
  - P11
  - P12
inputs:
  - Problem intent and desired outcomes
  - Hard constraints and non-negotiables
  - Environment assumptions including connectivity and operators
  - Known risks, especially physical or regulatory
outputs:
  - Architecture narrative with major components and boundaries
  - Local versus remote responsibility split
  - Key failure modes and mitigations at architecture level
  - Explicit open questions and professional-validation escalations
relationships:
  - type: references
    target: eos.framework.design.architecture-trade-offs
---

# System Architecture Shaping

## Purpose

This playbook provides a reusable method for turning an engineering intent into a coherent **system architecture recommendation**.

It shapes:

- what the system must achieve
- which responsibilities exist
- where those responsibilities live
- how the system should behave when parts fail
- which decisions are architectural versus which require professional physical validation

It does **not** prescribe a vendor stack, wire schedules, or certified installation procedures.

## When to Use

Use this playbook when the caller needs architecture, not merely a feature list or a purchase recommendation.

Strong fit:

- greenfield system design
- significant redesign of boundaries or control planes
- systems that must keep working under network or internet failure
- systems with remote operators and local autonomy requirements
- cyber-physical or facility systems where software architecture and physical safety boundaries interact

Weak fit:

- pure code refactoring inside an existing well-understood architecture
- detailed electrical design
- incident response for a live outage as the primary intent

## Method

### 1. Frame the intent

Capture:

1. Desired outcomes in operator and user terms
2. Hard constraints (must work offline, must allow remote control, must authenticate users, etc.)
3. Soft preferences
4. Explicit non-goals
5. Physical or regulatory risk indicators

Do not assume the conversation language matches canonical knowledge language. Translate the intent into architectural concerns; keep canonical reasoning in Engineering OS knowledge terms.

### 2. Identify architectural drivers

Convert the intent into drivers such as:

- local autonomy
- remote operability
- security and trust boundaries
- reliability and degraded-mode behavior
- observability and recoverability
- integration with devices or external systems
- operability by non-expert on-site staff
- safety and professional-validation boundaries

### 3. Partition responsibilities

Propose major responsibility areas before technologies. Typical partitions for facility/cyber-physical control systems include:

| Responsibility | Questions to answer |
|---|---|
| Local control | What must keep working with no internet? |
| Edge coordination | What local brain coordinates devices and policies? |
| Remote access plane | How do authorized users reach the system when connectivity exists? |
| Identity and authorization | Who may do what, from where, and under which trust assumptions? |
| Device integration | How are actuators/sensors represented without freezing vendor choices too early? |
| Observability | What must be visible locally vs remotely? |
| Safety interlocks | Which actions are software-gated vs professionally engineered physical protections? |

### 4. Place local / edge / remote boundaries

For each responsibility, decide:

- **Local-only** — required during total internet loss
- **Local-first, remote-optional** — local path is authoritative; remote is convenience
- **Remote-dependent** — acceptable only if failure leaves the local system safe and operable

Architecture rule of thumb:

> If a capability is required during connectivity loss, its control path must not depend on the cloud.

### 5. Define trust and failure modes

At minimum, reason about:

- internet failure
- local network failure
- remote credential compromise
- edge controller failure
- partial device failure
- split-brain risk between local and remote commands
- unsafe commanded states

For each critical failure, state the expected degraded behavior.

### 6. Separate architecture from professional validation

If the system actuates physical equipment, affects access control to real spaces, or touches regulated electrical work, the architecture must explicitly say:

- what Engineering OS can recommend as software/system structure
- what requires a qualified professional before installation or operation claims are made

Architectural reasoning may identify that a local emergency-stop or physically safe default is required. It must not pretend that identifying the need equals certified design of the mechanism.

### 7. Emit a reviewable architecture

Produce:

1. Context and drivers
2. Component/responsibility map
3. Local vs remote placement
4. Trust boundaries
5. Failure-mode behavior
6. Key open decisions
7. Escalations to professional validation
8. Optional candidates for trade-off analysis via `eos.framework.design.architecture-trade-offs`

## Worked Scenario — Padel Court Facility Automation

Illustrative intent:

> Install complete home-automation-style control for a padel court: access, lighting, and related systems. The installation must keep working locally if internet is lost. Authorized users must also control the system remotely from a phone when connectivity exists.

### Architectural reading of the intent

This is primarily a **system architecture** problem with cyber-physical consequences:

- local autonomy is a hard constraint
- remote control is a valued secondary path
- access control implies authentication and authorization
- lighting and facility actuators imply physical safety boundaries
- internet failure must not disable local operation

### Candidate responsibility map

```text
[Authorized mobile users]
          |
          v
   Remote access plane  ----(only when connected)----\
          |                                           \
          v                                            \
   Edge facility controller  <---- authoritative local policy
          |
          +--> Access subsystem
          +--> Lighting subsystem
          +--> Other facility subsystems
          |
          v
   Local operator controls / safe defaults
```

### Boundary decisions

| Concern | Architectural stance |
|---|---|
| Local operation without internet | Mandatory. Edge controller and local device control paths remain authoritative. |
| Remote phone control | Optional enhancement through a remote access plane; never the sole control path for required functions. |
| Authorization | Local policy store on the edge; remote access authenticates into that policy model rather than inventing a second authority during partition. |
| Internet failure | Remote features degrade; local access and lighting control continue. |
| Local network failure | Define safe device defaults; avoid unbounded remote actuation assumptions. |
| Security | Treat remote plane as high-risk exposure; minimize privileges; prefer least privilege and audited actions. |
| Observability | Local status must be available on-site; remote telemetry is best-effort. |
| Physical safety | Software architecture can require safe defaults and interlocks as design constraints; electrical installation, lock hardware, and safety certification require qualified professionals. |

### What this playbook should not invent here

- Exact relay models, cable gauges, or breaker schedules
- A claim that a recommended architecture is installation-ready without professional review
- A cloud-only design that violates the offline constraint

### How the companion framework helps

If multiple placements remain viable — for example “edge-authoritative with remote gateway” versus “local controllers with a thinner supervisory edge” — evaluate them with `eos.framework.design.architecture-trade-offs` rather than embedding an ad-hoc comparison inside this playbook.

## Quality Bar

A good output of this playbook:

- can be reviewed by a human without tool-specific jargon
- states boundaries before products
- preserves the offline constraint when required
- names failure behavior
- clearly escalates physical/regulatory validation

A poor output:

- jumps to brand shopping
- hides cloud dependency inside “smart” defaults
- treats architecture as a substitute for licensed electrical work
- produces an unreviewable blob of components without responsibilities
