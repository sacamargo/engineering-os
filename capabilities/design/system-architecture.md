---
id: eos.capability.design.system-architecture
type: capability
title: System Architecture Design
summary: Route intents to design a coherent system architecture under stated goals and constraints.
purpose: Provide a durable product entry point for architecture-design intents without owning the design method.
audience: Engineers, architects, and technical leads shaping system structure
status: active
applicability: When the primary need is to propose, reshape, or reason about system structure, boundaries, control planes, failure modes, and local/remote placement for greenfield work or significant redesign.
limits: Does not own step-by-step design methods; does not replace detailed implementation design; does not perform security audits or incident response as primary intents; does not authorize electrical, structural, or regulated physical work; does not replace licensed professional engineering where law or physical safety requires it.
domain: design
language: en
complexity: high
tags:
  - architecture
  - system-design
  - boundaries
  - trade-offs
entry_signals:
  - Design the architecture for this system
  - How should I structure this system
  - Propose a high-level system design
  - What are the major components and boundaries
  - Design for local autonomy and remote control
  - Architecture for an IoT or cyber-physical system
  - How should local and cloud responsibilities be split
outcome_expectations: A coherent architecture recommendation with explicit boundaries, major components, critical trade-offs, failure-mode thinking, and clear escalation to professional validation where physical or regulatory risk exists.
arbitration: Prefer the system-architecture playbook when shaping an overall architecture from goals and constraints. Prefer the architecture trade-offs framework when candidate structures already exist and the need is to choose among them. Use both when shaping and deciding are both required; do not treat either unit as a mandatory sequential pipeline.
relationships:
  - type: primary_fulfillment
    target: eos.playbook.design.system-architecture
  - type: fulfilled_by
    target: eos.framework.design.architecture-trade-offs
  - type: related_capability
    target: eos.capability.security.review
  - type: related_capability
    target: eos.capability.quality.test-planning
  - type: related_capability
    target: eos.capability.operations.observability
---

# System Architecture Design

## Intent Class

This Capability represents the durable intent class:

> Help design an appropriate **system architecture** for a stated problem under constraints.

Users typically ask in outcome language, in any spoken language. Examples of demand-side phrasing include requests to design, structure, or reshape a system; to define major components and boundaries; or to reason about local autonomy, remote access, and failure behavior.

Engineering OS routes those intents here. Fulfillment knowledge supplies methods and decision models.

## In Scope

- Identifying architectural drivers and constraints
- Proposing major components and responsibility boundaries
- Reasoning about control, data, and trust boundaries
- Placing responsibilities across local, edge, and remote/cloud contexts
- Surfacing critical trade-offs and failure modes at architecture level
- Distinguishing architectural recommendations from professional physical validation

## Out of Scope

- End-to-end implementation of a product
- Detailed electrical, structural, or safety-code design
- Penetration testing or full security audits as the primary ask
- Choosing a single vendor pack without architectural framing
- Acting as a licensed professional engineer for regulated physical systems

## Fulfillment

Bound units:

| Unit | Role |
|---|---|
| `eos.playbook.design.system-architecture` | Primary method for shaping architecture from intent and constraints |
| `eos.framework.design.architecture-trade-offs` | Decision model for comparing architectural options |

Additional units may be bound later without changing this Capability’s identity.

## Related Intent Classes

This Capability is often adjacent to Application Security Review when architecture choices create or remove trust-boundary risk.

`related_capability` means soft co-relevance for future routing. It does **not** create an execution sequence or Capability DAG.
