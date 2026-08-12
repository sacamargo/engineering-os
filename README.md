# Engineering OS

**An AI-native operating system for software engineering.**

Engineering OS is an engineering decision system — Capabilities, playbooks, decision frameworks, standards, workflows, templates, checklists, and specialized AI skills — designed to help humans and AI make better software engineering decisions.

It is **not** a prompt collection.  
It is **not** a Cursor rules repository.  
It is **not** a catalog of GPTs or vendor-specific agents.  
It is **not** organized primarily around documents.

It is a vendor-neutral platform and **knowledge system** that should remain useful regardless of which AI tools exist today — or ten years from now.

---

## What This Is

Engineering OS treats software engineering as a system that can be operated deliberately:

| Layer | Role |
|---|---|
| **Foundation** | Vision, philosophy, principles, system/knowledge/capability models, workflow, roadmap |
| **Contracts** | Enforceable schemas and validation for Capabilities and knowledge units |
| **Capabilities** | Durable intent classes the system offers to fulfill |
| **Modules** | Knowledge units that fulfill Capabilities: playbooks, skills, standards, workflows, templates, checklists, frameworks |
| **Adaptations** | Thin, optional bridges to specific AI tools and environments |

Users ask for outcomes. Capabilities route those intents. Knowledge units fulfill them.

---

## Design Stance

- **AI-native** — designed for collaboration with AI, not bolted on afterward
- **AI-agnostic** — works with Cursor, ChatGPT, Claude, Gemini, Windsurf, Cline, GitHub Copilot, and future systems
- **Technology-agnostic** — no mandated language, cloud, or stack
- **Vendor-neutral** — no dependency on a single product or provider
- **Capability-routed** — orchestrate by intent class, not by document genre
- **Modular & extensible** — adopt what you need; extend what you don't have
- **Production-oriented** — optimized for real delivery, not demos

---

## Language Policy

This repository is **English-first**.

All knowledge artifacts in this repository — documentation, Capabilities, playbooks, skills, templates, checklists, examples, comments, and READMEs — are written in professional English.

Communication is language-independent. Users and contributors may interact with Engineering OS (and with AI systems using it) in any language. Engineering OS never requires prompts to be written in English.

> Knowledge is stored in English. Communication is language-independent.

---

## Repository Status

Functional agency MVP is available:

- Capabilities: architecture, security review, test planning, observability/metrics
- Portable agency skill: `eos.skill.agency.capability-routing`
- Cursor adaptation skill: `.cursor/skills/engineering-os-agency`
- Use cases: `experiments/agency-mvp/USE-CASES.md`

This is not the full long-term catalog. Missing domains still return honest `insufficient_coverage`.

---

## Start Here

| Document | Purpose |
|---|---|
| [Vision](foundation/VISION.md) | Why Engineering OS exists and what it aims to become |
| [Philosophy](foundation/PHILOSOPHY.md) | Beliefs that govern every design decision |
| [Principles](foundation/PRINCIPLES.md) | Non-negotiable engineering principles |
| [System Architecture](foundation/SYSTEM-ARCHITECTURE.md) | Layers, module taxonomy, dependency rules |
| [Knowledge Architecture](foundation/KNOWLEDGE-ARCHITECTURE.md) | Knowledge units, retrieval, and AI consumption |
| [Capability Model](foundation/CAPABILITY-MODEL.md) | Intent-class routing and fulfillment facades |
| [Intent Resolution](foundation/INTENT-RESOLUTION.md) | Framing requests into Capability candidates |
| [Engineering Workflow](foundation/ENGINEERING-WORKFLOW.md) | Git workflow and repository discipline |
| [Project Roadmap](foundation/PROJECT-ROADMAP.md) | Long-term evolution plan |
| [Contracts](contracts/README.md) | Enforceable unit/capability metadata and validation |
| [Intent Disambiguation Experiment](experiments/intent-disambiguation/README.md) | Authored routing cases + structural evaluator |
| [Agency MVP Use Cases](experiments/agency-mvp/USE-CASES.md) | Runnable prompts to test the agency loop |
| [System Architecture Capability](capabilities/design/system-architecture.md) | Architecture-design intent routing |
| [Application Security Review Capability](capabilities/security/review.md) | Security-review intent routing |
| [Test Planning Capability](capabilities/quality/test-planning.md) | Validation strategy intent routing |
| [Observability Capability](capabilities/operations/observability.md) | Metrics/monitoring intent routing |
