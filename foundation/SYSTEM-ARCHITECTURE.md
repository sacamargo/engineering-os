# System Architecture

This document defines the **system architecture** of Engineering OS: layers, module taxonomy, dependency rules, and extension boundaries.

It does **not** define how knowledge is structured for humans and AI. That belongs to [Knowledge Architecture](KNOWLEDGE-ARCHITECTURE.md).

It does **not** define the Capability catalog semantics. That belongs to [Capability Model](CAPABILITY-MODEL.md).

It does **not** define how this repository is developed. That belongs to [Engineering Workflow](ENGINEERING-WORKFLOW.md).

---

## Architectural Metaphor

Engineering OS follows the metaphor of an operating system:

| OS Concept | Engineering OS Equivalent |
|---|---|
| Kernel | Foundation (vision, philosophy, principles, architectures, capability model, roadmap, workflow) |
| System calls / entry API | Capabilities — durable intent classes the system offers to fulfill |
| Filesystem / knowledge substrate | Knowledge units with metadata, relationships, and retrieval rules |
| System libraries | Standards, decision frameworks, shared vocabulary |
| Userland programs | Playbooks, workflows, skills, templates, checklists |
| Device drivers | Optional adaptations to specific AI tools and environments |
| Users | Engineers, teams, organizations, and AI systems acting on their behalf |

The metaphor guides boundaries. It is not a mandate to imitate operating-system internals.

---

## Layer Model

```text
┌──────────────────────────────────────────────────────────────┐
│  Adaptations (optional, vendor-specific, replaceable)        │
├──────────────────────────────────────────────────────────────┤
│  Modules = Knowledge Units (playbooks, skills, standards…)   │
├──────────────────────────────────────────────────────────────┤
│  Capability Catalog (intent routing / fulfillment facades)   │
├──────────────────────────────────────────────────────────────┤
│  Contracts (schemas for units and capabilities)              │
├──────────────────────────────────────────────────────────────┤
│  Foundation / Kernel                                         │
│    vision · philosophy · principles                          │
│    system · knowledge · capability model                     │
│    project roadmap · engineering workflow                    │
└──────────────────────────────────────────────────────────────┘
```

### Layer 0 — Foundation (Kernel)

Authoritative design intent. Changes rarely and only with explicit rationale.

| Document | Responsibility |
|---|---|
| `VISION.md` | Why the system exists |
| `PHILOSOPHY.md` | Beliefs that constrain design |
| `PRINCIPLES.md` | Non-negotiable rules |
| `SYSTEM-ARCHITECTURE.md` | Layers, modules, dependencies |
| `KNOWLEDGE-ARCHITECTURE.md` | Knowledge units, retrieval, AI consumption |
| `CAPABILITY-MODEL.md` | Intent-class routing and fulfillment facades |
| `INTENT-RESOLUTION.md` | Intent framing and Capability candidate resolution |
| `PROJECT-ROADMAP.md` | Long-term evolution sequence |
| `ENGINEERING-WORKFLOW.md` | How this repository is developed |

### Layer 1 — Contracts

Machine-reviewable rules that implement Knowledge Architecture and Capability Model for authors and tooling.

Authoritative contract artifacts live in `contracts/`:

- `contracts/SPEC.md` — invariants and encoding rules
- `contracts/unit.schema.json` — single-unit metadata shape
- `contracts/validate.py` — executable catalog validator

Foundation documents remain the architectural authority for meaning. Contracts enforce encoding and structural invariants.

### Layer 2 — Capability Catalog

Durable canonical intent classes. The primary surface for Orchestrator routing and human “what can this system help with?” discovery.

See [Capability Model](CAPABILITY-MODEL.md). Directory `capabilities/` is created only when the first Capability lands.

### Layer 3 — Modules (Knowledge Units)

Reusable engineering knowledge that fulfills Capabilities: methods, standards, procedures, structures, checks.

Modules must remain independently meaningful. Capabilities optimize routing; they do not make modules unreachable.

### Layer 4 — Adaptations

Thin mappings from portable Capabilities/units onto specific tools. Adaptations may package or translate; they must not become the source of truth.

---

## Planned Module Taxonomy

These directories are **not created yet**. They appear when the first real artifact of that type lands.

| Module Type | Responsibility | Non-Goals |
|---|---|---|
| `capabilities/` | Intent-class routing facades | Methods; enterprise org maps; vendor packs |
| `playbooks/` | End-to-end ways of working for recurring engineering situations | Tool setup guides; vendor tutorials |
| `frameworks/` | Decision frameworks and mental models for choosing among options | One-size-fits-all prescriptions |
| `standards/` | Engineering standards that define quality bars | Style preference dumps without rationale |
| `workflows/` | Ordered, reusable sequences of steps with clear entry/exit criteria | Rigid bureaucracy |
| `skills/` | Portable AI-operable procedures with explicit inputs/outputs | Model-specific prompt packs |
| `templates/` | Starting structures for documents, designs, ADRs, plans, etc. | Decorative boilerplate |
| `checklists/` | Verifiable inspection lists for quality, readiness, and risk | Endless audit theater |
| `adaptations/` | Optional bridges to specific AI products and environments | Core methodology |

Additional types may be proposed only when an existing type cannot express the need without distortion — and only after Knowledge Architecture extension rules are satisfied.

---

## Authoring Requirements

Every Capability and module MUST:

1. Satisfy [Contracts](../contracts/SPEC.md) metadata and relationship rules
2. Remain AI-agnostic at the core
3. Be independently adoptable (modules) or clearly offered (capabilities)
4. Be written in professional English
5. Use stable identifiers and explicit relationships
6. Honor the Capability Model constraints when defining or binding Capabilities

---

## Dependency Rules

```text
Foundation        →  depends on nothing inside this repository
Contracts         →  may depend only on Foundation
Capabilities      →  may depend on Foundation and Contracts; bind to Modules
Modules           →  may depend on Foundation, Contracts, and other Modules with care
                     must not require Capabilities for their own validity
Adaptations       →  may depend on Capabilities and Modules; must not be depended on by either
```

Forbidden:

- A playbook that only works inside one AI product
- A skill that silently embeds vendor lock-in as if it were methodology
- An adaptation that forks canonical content instead of referencing it
- Circular dependencies between unrelated modules
- Modules that bypass Knowledge Architecture identifiers and relationships
- Capabilities that embed full methods instead of binding to units
- Deep Capability execution DAGs

Allowed:

- A Capability fulfilled by playbooks, frameworks, checklists, and skills
- A playbook composing checklists, templates, and skills via declared relationships
- An adaptation packaging a Capability or skill for a specific tool’s extension format

---

## Target Repository Shape

```text
engineering-os/
├── README.md
├── foundation/                      # Kernel
│   ├── VISION.md
│   ├── PHILOSOPHY.md
│   ├── PRINCIPLES.md
│   ├── SYSTEM-ARCHITECTURE.md
│   ├── KNOWLEDGE-ARCHITECTURE.md
│   ├── CAPABILITY-MODEL.md
│   ├── INTENT-RESOLUTION.md
│   ├── PROJECT-ROADMAP.md
│   └── ENGINEERING-WORKFLOW.md
├── contracts/                       # Enforceable schemas + validation
├── experiments/                     # Focused architectural experiments
├── capabilities/                    # Intent catalog (proof started)
├── playbooks/                       # Fulfillment methods (proof started)
├── frameworks/                      # Decision models (proof started)
├── standards/                       # Future
├── workflows/                       # Future
├── skills/                          # Future
├── templates/                       # Future
├── checklists/                      # Future
└── adaptations/                     # Future, optional, peripheral
```

Empty directories are intentionally omitted. Folders appear when content justifies them.

Licensing and public contribution guides are deferred until the project is ready to distribute and accept external contributions. See [Project Roadmap](PROJECT-ROADMAP.md).

---

## Extension Model

1. **Propose** — identify a gap in offered intent classes or fulfillment knowledge
2. **Classify** — Capability vs knowledge unit type
3. **Contract-check** — satisfy foundation models and (when present) contracts
4. **Land** — add canonical English content with metadata and relationships
5. **Bind** — if a unit fulfills an intent class, update Capability bindings
6. **Adapt (optional)** — create thin tool-specific packaging if needed
7. **Review & revise** — improve through use; deprecate when obsolete

Organizations may maintain private extensions. Private forks should track foundation changes and avoid rewriting the kernel without cause.

---

## Why This Architecture

| Decision | Rationale | Rejected Alternative |
|---|---|---|
| Capability catalog above modules | Intent routing must not equal document inventory | Playbook-first navigation — fails at orchestration scale |
| Separate system vs knowledge vs capability docs | Different concerns; naming must stay precise | One generic architecture file — ambiguous at scale |
| Modules remain valid without Capabilities | Progressive adoption; no routing bureaucracy lock-in | Mandatory Capability wrapping of every unit |
| Delay empty module folders | Avoids false structure and placeholder rot | Scaffold everything now — looks complete, is hollow |
| AI-agnostic core + optional adaptations | Survives vendor churn | Tool-native repo — high short-term convenience, low longevity |
| Defer LICENSE / CONTRIBUTING | Legal and community process are publishing decisions | GitHub-default files without distribution need |

Architecture preserves optionality where the future is uncertain, and constrains it where principles are settled.
