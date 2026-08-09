# Knowledge Architecture

Engineering OS is fundamentally a **knowledge system**.

This document defines how knowledge is represented, related, discovered, retrieved, versioned, extended, and consumed — by humans and by AI systems — so that hundreds of playbooks and related units can coexist consistently.

It does **not** define playbook content. It defines the substrate that makes playbooks and other units scalable.

It does **not** define Capability semantics beyond type integration. That belongs to [Capability Model](CAPABILITY-MODEL.md).

---

## Design Intent

The central question:

> How should AI systems consume Engineering OS?

Answer in one line:

> AI systems route through **Capabilities** (canonical intent classes), then consume **addressable knowledge units** through an explicit **retrieval protocol** — not by ingesting the repository as an undifferentiated document pile.

Implications:

- Intent routing and knowledge fulfillment are separate concerns ([Capability Model](CAPABILITY-MODEL.md))
- Every durable fulfillment artifact is a knowledge unit with identity and metadata
- Relationships are first-class, not buried in prose alone
- Discovery and retrieval are designed, not accidental
- AI loads the minimum sufficient context for the task
- Humans remain able to read, review, and govern the same units

---

## Knowledge Units

### Definition

A **knowledge unit (KU)** is the atomic, addressable unit of Engineering OS.

A knowledge unit:

- solves one coherent problem or enables one coherent class of decisions/actions
- has a stable identifier
- has typed metadata
- declares relationships to other units
- can be retrieved independently
- can be composed with other units without merging files

Foundation documents are **kernel documents**, not modules. They govern the system.

**Capabilities** are addressable catalog objects (`type: capability`) that route intent. They use the same identity/lifecycle machinery as knowledge units but are not method carriers. See [Capability Model](CAPABILITY-MODEL.md).

**Modules** are knowledge units that fulfill Capabilities. Kernel documents may be referenced by either but are not interchangeable with them.

### Unit Types

Unit types align with the module taxonomy in [System Architecture](SYSTEM-ARCHITECTURE.md):

| Type | Knowledge Role |
|---|---|
| `capability` | Intent-class routing facade; binds to fulfillment units (not a method) |
| `playbook` | Situational method: how to approach an end-to-end engineering situation |
| `framework` | Decision model: how to choose among options |
| `standard` | Quality bar: what “good” requires |
| `workflow` | Ordered procedure: steps with entry/exit criteria |
| `skill` | AI-operable procedure: explicit inputs, process, outputs |
| `template` | Starting structure for a recurring artifact |
| `checklist` | Verifiable inspection list |
| `adaptation` | Tool-specific packaging of one or more canonical units or capabilities |

### Atomicity Rule

One unit = one primary responsibility.

If a document needs two audiences, two purposes, or two lifecycles, it is probably two units linked by a relationship — not one oversized file.

### Identity

Every knowledge unit MUST have a stable ID.

Recommended form:

```text
eos.<type>.<domain>.<name>
```

Examples:

```text
eos.capability.design.system-architecture
eos.capability.security.review
eos.playbook.design.system-architecture
eos.playbook.security.application-review
eos.framework.design.architecture-trade-offs
eos.framework.security.risk-prioritization
eos.checklist.review.pull-request-quality
eos.standard.quality.definition-of-done
```

Rules:

- IDs are immutable once published
- File paths may change; IDs must not
- Renames update path and title, never the ID
- Deprecated units keep their ID and gain a successor relationship

---

## Metadata

Metadata makes units discoverable, comparable, and loadable without reading the full body.

### Required Metadata (Conceptual Schema)

Contracts (Phase 1) will formalize encoding (for example YAML front matter). The conceptual fields are:

| Field | Purpose |
|---|---|
| `id` | Stable identifier |
| `type` | Unit type |
| `title` | Human-readable name |
| `summary` | One or two sentences stating what the unit does |
| `purpose` | Problem solved or decision/action enabled |
| `audience` | Who it is for (roles, not vendors) |
| `status` | `draft` \| `active` \| `deprecated` \| `retired` |
| `applicability` | When to use it |
| `limits` | When not to use it |
| `inputs` | What the unit expects (artifacts, context, decisions) — **required for fulfillment modules**; not used on Capabilities |
| `outputs` | What the unit produces — **required for fulfillment modules**; not used on Capabilities |
| `principles` | Principle IDs this unit operationalizes (optional but preferred) |

### Optional Metadata

| Field | Purpose |
|---|---|
| `tags` | Faceted keywords for discovery (`incident`, `design`, `security`, …) |
| `domain` | Coarse area (`delivery`, `design`, `quality`, `operations`, …) |
| `complexity` | Relative cognitive/operational load (`low` \| `medium` \| `high`) |
| `estimated_effort` | Human guidance only; never a SLA |
| `language` | Always `en` for canonical units |
| `supersedes` | ID of unit this replaces (if any) |
| `version` | Unit-level revision marker when contracts define it |

### Metadata Design Rules

- Metadata must be sufficient for **routing**: decide whether to load the body
- Metadata must not duplicate the entire body
- Status is mandatory; silent abandonment is forbidden
- Vendor names do not belong in core metadata except inside `adaptation` units

---

## Relationships

Relationships form the knowledge graph. Prose links are helpful; typed relationships are authoritative for composition and retrieval.

### Relationship Types

| Relationship | Meaning | Typical Use |
|---|---|---|
| `references` | Soft citation; useful context | Playbook citing a principle or standard |
| `depends_on` | Hard prerequisite; unit is incomplete without target | Workflow requiring a checklist |
| `composes` | Unit includes target as a part of its method | Playbook composing skills + templates |
| `specializes` | Narrower variant of a more general unit or capability | Narrower standard or capability |
| `alternative_to` | Peer option; choose one based on context | Two frameworks for prioritization |
| `supersedes` | Successor replaces predecessor | Version evolution / deprecation |
| `conflicts_with` | Must not be applied together without resolution | Mutually incompatible standards |
| `fulfilled_by` | Capability → unit that helps fulfill the intent class | Security review capability → playbook/checklist |
| `primary_fulfillment` | Capability → default unit when context is thin | Capability → primary playbook or framework |
| `related_capability` | Soft adjacency between capabilities | Architecture design related to scalability review |

### Relationship Rules

- Relationships are directional and typed
- `depends_on` and `composes` must not create cycles
- `adaptation` units may `composes` or `references` canonical units; canonical units must not `depends_on` adaptations
- `fulfilled_by` and `primary_fulfillment` originate from Capabilities; modules must not depend on Capabilities for validity
- Capability-to-Capability hard dependency DAGs are forbidden; use `related_capability` or unit-level composition instead
- Prefer a small set of precise relationships over many vague “related” links
- Every relationship should be explainable in one sentence

### Cross References

Cross references exist at two levels:

1. **Typed relationships in metadata** — for AI retrieval, validation, and composition
2. **Human-readable links in the body** — for navigation while reading

Both should agree. If they diverge, metadata wins for machine behavior; the body must be corrected.

---

## Discovery

Discovery answers: *What exists that might help?*

### Discovery Surfaces (Target)

| Surface | Role |
|---|---|
| Capability catalog | Primary product surface: what intent classes Engineering OS fulfills |
| Unit metadata | Filter fulfillment units without loading bodies |
| Type directories | Browse by module kind |
| Domain / tags | Faceted findability |
| Relationship graph | Navigate from Capability → units → neighbors |
| Catalog indexes | Optional generated lists by situation |

### Situational Discovery

Users and AI often start from a situation, not a filename:

- “We need to introduce a risky production change”
- “We need to review a design under uncertainty”
- “We need a definition of done”

Primary path: map the situation to one or more **Capabilities**, then resolve fulfillment bindings.

Fallback path: rank knowledge units by `applicability` and `tags` when Capability routing is inconclusive.

### Anti-Patterns

- Discovery that requires reading every file
- Discovery that depends on one AI vendor’s memory or project feature
- Undocumented “everyone knows it’s in that playbook” lore
- Skipping Capabilities and forcing consumers to learn the full module inventory

---

## Retrieval

Retrieval answers: *What should be loaded now?*

### Retrieval Principles

1. **Minimum sufficient context** — load only what the task needs
2. **Metadata first** — route with summaries before bodies
3. **Progressive disclosure** — expand along relationships only as required
4. **Deterministic preference** — prefer explicit IDs and graphs over fuzzy recall when correctness matters
5. **Human inspectability** — any AI-loaded set should be listable as unit IDs

### Retrieval Modes

| Mode | When | Behavior |
|---|---|---|
| **Capability** | Caller has an intent/goal | Rank Capability candidates; select; resolve `fulfilled_by` / `primary_fulfillment` |
| **Direct** | Caller knows a unit or Capability ID | Load that object’s metadata + body |
| **Situational fallback** | Capability routing inconclusive | Rank units by type, tags, applicability |
| **Compositional** | A unit is selected | Load the unit plus `depends_on` targets; optionally offer `composes` targets |
| **Comparative** | Decision among options | Load a framework plus `alternative_to` peers |
| **Delta** | Evolution / migration | Load object + `supersedes` chain |

### Context Packaging

A **context package** is the set of addressable objects assembled for a task:

```text
context_package = {
  capability: [capability IDs],
  primary:    [unit IDs],
  required:   [depends_on closure],
  optional:   [composes / references suggestions],
  excluded:   [deprecated / conflicting IDs]
}
```

Rules:

- Prefer small packages
- Never silently include deprecated Capabilities or units
- If `conflicts_with` appears, surface the conflict to the human before proceeding
- Adaptations are included only when the runtime environment requires them

### What AI Must Not Do

- Treat the entire repository as mandatory context
- Invent Capability IDs, unit IDs, or relationships
- Override `limits` without human acknowledgment
- Substitute an adaptation for a canonical unit or Capability as if they were the same authority
- Skip Capability routing at scale by dumping module catalogs into context

---

## AI Consumption Model

### Roles

| Role | Responsibility |
|---|---|
| Human | Selects goals, accepts risk, owns outcomes |
| Orchestrator / AI runtime | Routes to Capabilities, retrieves units, follows skills/workflows, drafts artifacts |
| Engineering OS | Provides Capability catalog, portable knowledge, and consumption rules |

### Consumption Protocol (Logical)

This protocol is vendor-neutral. Any AI system can implement it:

1. **Frame** — capture goal, constraints, and environment (language of conversation may be any language)
2. **Route** — propose candidate Capability IDs for the intent class
3. **Select** — human or policy selects Capability (and disambiguates if needed)
4. **Bind** — resolve `primary_fulfillment` / `fulfilled_by` to unit IDs using arbitration guidance
5. **Assemble** — build a context package via unit relationship rules
6. **Execute** — follow the unit’s method; for `skill` units, honor inputs/outputs
7. **Emit** — produce outputs defined by the unit
8. **Verify** — apply linked checklists/standards; request human review where required
9. **Record** — note Capability IDs and unit IDs that governed the work (for auditability)

Steps 1–3 are detailed in [Intent Resolution](INTENT-RESOLUTION.md). Candidate Capabilities are not the same as selected Capabilities. Insufficient catalog coverage is a valid outcome.

### Portability Requirement

An AI system consumes Engineering OS correctly when it can:

- resolve Capabilities and units by ID
- read metadata without proprietary extensions
- traverse declared relationships
- operate on English canonical bodies while conversing in the user’s language

Tool-specific features (rules files, custom agents, plugin formats) belong in `adaptation` units that **reference** this protocol — they do not replace it.

### Skills vs Prompts

A `skill` is a knowledge unit with operable structure (inputs, steps, outputs, limits).  
A prompt is an ephemeral instruction.

Do not confuse `skill` with Capability. Skills are procedures. Capabilities are intent-class offers.

Engineering OS stores skills. Adaptations may derive prompts from skills. Derived prompts are never canonical.

---

## Versioning

### Levels

| Level | What Changes | How |
|---|---|---|
| Repository | The whole system | Git history (see Engineering Workflow) |
| Foundation | Kernel documents | Rare, explicit migration notes |
| Capability | Intent-class offer and bindings | Slow definition changes; faster rebinding; see Capability Model |
| Knowledge unit | One unit’s meaning or interface | `status`, relationships (`supersedes`), and later a unit `version` field |

### Unit Lifecycle

```text
draft → active → deprecated → retired
```

- `draft` — not ready for general consumption
- `active` — approved for use
- `deprecated` — usable transiently; successor should be preferred
- `retired` — retained for history; not loaded for new work

### Compatibility Expectations

- Additive metadata and new optional relationships are non-breaking
- Changing `id`, removing required inputs/outputs, or reversing core guidance is breaking
- Breaking changes SHOULD create a new unit that `supersedes` the old one when callers depend on prior behavior
- Exact semver policy for units is deferred to contracts/longevity phases; lifecycle + `supersedes` is mandatory now at the design level

---

## Extensibility

### First-Party Extension

New units enter the system by:

1. Fitting an existing type, or justifying a new type against System Architecture
2. Providing full required metadata
3. Declaring relationships
4. Passing the quality bar defined in future contracts

### Private / Organizational Extension

Organizations may add private units that:

- use a distinct ID namespace (for example `acme.*` or `eos.org.<org>.*`)
- reference public `eos.*` units
- do not rewrite foundation documents without deliberate fork governance

Private adaptations may package public units for internal toolchains.

### Extension Boundaries

Allowed:

- new units
- new relationships among units
- new adaptations
- new discovery indexes

Not allowed without foundation change:

- weakening AI-agnostic core rules
- making adaptations authoritative over canonical units
- introducing vendor-required metadata into core schemas

---

## Consistency at Scale

To keep hundreds of playbooks coherent:

| Mechanism | Effect |
|---|---|
| Capability catalog | Keeps consumer surface coarse as units multiply |
| Typed units | Prevents category collapse (“everything is a doc”) |
| Stable IDs | Enables durable references across renames |
| Required metadata | Enables routing without full reads |
| Typed relationships | Enables composition without copy-paste |
| Lifecycle states | Prevents zombie guidance |
| Context packages | Prevents context bloat for AI |
| Contracts | Make the above enforceable |

---

## Encoding and Validation

Contracts implement the encoding details previously deferred here:

- On-disk metadata syntax: YAML front matter — see [contracts/SPEC.md](../contracts/SPEC.md)
- Validation tooling: [contracts/validate.py](../contracts/validate.py)
- Formal schema mirror: [contracts/unit.schema.json](../contracts/unit.schema.json)

Still deferred beyond Phase 1 contracts:

- Generated catalogs and situation indexes
- Unit-level semver policy (lifecycle + `supersedes` remain mandatory)
- Body ↔ metadata cross-reference linting
- Context package runtime schema

This document remains the architectural authority those contracts implement.

---

## Why This Knowledge Architecture

| Decision | Rationale | Rejected Alternative |
|---|---|---|
| Capability-first routing + unit fulfillment | Matches how users ask for help; scales orchestration | Playbook-first navigation — inventory becomes the UX |
| Knowledge unit as atomic fulfillment unit | Scales composition and retrieval | Monolithic guidebooks — unmaintainable and unroutable |
| Stable IDs separate from paths | Survives reorganization | Path-based identity — brittle |
| Typed relationships | Enables deterministic assembly | Wiki-style links only — ambiguous for AI |
| Metadata-first retrieval | Controls context cost and precision | “Dump the repo into the prompt” — does not scale |
| Vendor-neutral consumption protocol | Keeps core AI-agnostic | Tool-native memory/rules as source of truth |
| Lifecycle over instant deletion | Supports migration and audit | Silent edits in place — breaks dependents |

The knowledge architecture exists so Engineering OS can grow without becoming a pile of documents that only their authors know how to use.
