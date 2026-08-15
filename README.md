# Engineering OS

**An autonomous software engineering agency — vendor-neutral, AI-native, architecture-first.**

Engineering OS turns high-level engineering intent (“build this”, “audit this”, “investigate this”) into coordinated Capabilities, knowledge, execution plans, tasks, artifacts, and validation gates.

It is **not** only a knowledge base.  
It is **not** a prompt collection.  
It is **not** a Cursor rules repository.  
It is **not** a catalog of GPTs or vendor-specific agents.  
It is **not** organized primarily around documents.

It is a vendor-neutral platform composed of:

| Layer | Role |
|---|---|
| **Knowledge Layer** | Playbooks, frameworks, skills, standards, and related units |
| **Capability Layer** | Durable intent classes for routing |
| **Execution Layer** | Projects, plans, tasks, artifacts, roles, dependencies |
| **Validation Layer** | Gates and evidence requirements |
| **Delivery Layer** | Boundary for repo/CI/deploy/release (runtime later) |
| **Agent Layer** | Executor boundary (runtime later) |
| **Adapter Layer** | Optional bridges to Cursor, CLI, GitHub, CI, clouds |

Users ask for outcomes. Engineering OS resolves specialists, Capabilities, plans, and validations — users should not need to assemble that menu manually.

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

**Phase 6 — Agent Execution** lands a sandboxed runtime (`agents/`) that executes Tasks with authorized Tools, Evidence, and Gates.

- Deterministic coding agent (no LLM required)
- Workspace sandbox, allowlisted commands, permission/risk checks
- Execution loop with retry/rollback/dry-run/human escalation
- Orchestrator assigns Agent Definitions; does not own tool execution
- Demo tests: `PYTHONPATH=. python3 -m unittest discover -s agents/tests -v`

Phase 5 Codebase Intelligence and Phase 4 Planning remain. This is **not** CI/CD autonomy, deploy, or agent swarms (Phase 7+).

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
| [Execution Model](foundation/EXECUTION-MODEL.md) | Intent → plan → tasks → gates coordination |
| [Orchestration package](orchestration/README.md) | Planning Orchestrator (Phase 4) |
| [Codebase Intelligence](codebase/README.md) | Repository observation pipeline (Phase 5) |
| [Agent Runtime](agents/README.md) | Sandboxed Task execution (Phase 6) |
| [Phase 6 Validation](docs/PHASE-6-VALIDATION.md) | Phase 6 evidence and limits |
| [Phase 5 Validation](docs/PHASE-5-VALIDATION.md) | Phase 5 evidence, limits, next step |
| [Engineering Workflow](foundation/ENGINEERING-WORKFLOW.md) | Git workflow and repository discipline |
| [Project Roadmap](foundation/PROJECT-ROADMAP.md) | Long-term evolution plan |
| [Contracts](contracts/README.md) | Knowledge + execution contracts and validation |
| [Rivallium Example](examples/rivallium/execution-plan.md) | Multi-capability execution proof |
| [Padel IoT Example](examples/padel-iot/execution-plan.md) | Cross-domain + professional escalation |
| [Intent Disambiguation Experiment](experiments/intent-disambiguation/README.md) | Authored routing cases + structural evaluator |
| [Agency MVP Use Cases](experiments/agency-mvp/USE-CASES.md) | Runnable prompts to test the agency loop |
| [System Architecture Capability](capabilities/design/system-architecture.md) | Architecture-design intent routing |
| [Application Security Review Capability](capabilities/security/review.md) | Security-review intent routing |
| [Test Planning Capability](capabilities/quality/test-planning.md) | Validation strategy intent routing |
| [Observability Capability](capabilities/operations/observability.md) | Metrics/monitoring intent routing |
