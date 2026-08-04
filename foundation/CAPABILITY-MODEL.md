# Capability Model

## Purpose

This document defines **Capability** as a first-class concept in Engineering OS.

It exists to answer one architectural question:

> What should humans and AI select when they need help — a document type, or a durable class of engineering intent?

Engineering OS is an AI-native engineering decision system. Users do not ask for playbooks. They ask to achieve outcomes: design an architecture, review security, choose a database, plan testing.

A Capability is the stable object that represents those intent classes. Playbooks, standards, checklists, frameworks, workflows, templates, and skills remain the knowledge that fulfills a Capability. They are not the primary navigation surface.

This concept was not accepted because it sounded useful. It was accepted only after alternatives were compared and the failure modes of playbook-first organization were judged worse at decade scale.

---

## Justification (Earn-Its-Place Test)

| Question | Answer |
|---|---|
| What problem does it solve? | The gap between user/AI **intent** and typed **knowledge units**. |
| What problem does it prevent? | Orchestrators selecting among hundreds of playbooks/skills by filename or type; product surface collapsing into document inventory. |
| What happens if it does not exist? | Discovery stays scattered across `applicability`/`tags`; routing quality degrades as the catalog grows; no stable “what Engineering OS can fulfill.” |
| Does it simplify the system? | It simplifies **consumption and orchestration**. It adds authoring complexity. Net acceptable only if Capabilities stay coarse and rare compared to units. |
| Does it introduce unnecessary complexity? | It can — if Capabilities become a second deep taxonomy, 1:1 aliases of playbooks, or enterprise-architecture bureaucracy. Those are rejected below. |
| Can another concept already solve this? | Partially: domains, tags, and situational discovery. They categorize and hint. They do not provide a governed, versioned fulfillment facade with arbitration. |

---

## Definition

A **Capability** is a durable, named class of engineering intents that Engineering OS is designed to fulfill.

It is:

- a **routing and fulfillment facade**
- a **stable product entry point** for humans and AI
- a **binding** from an intent class to the knowledge units that implement it

It is not:

- an enterprise “business capability map” in the TOGAF/CMMI sense
- a document genre
- a prompt
- a replacement for playbooks or skills
- a runtime service

### Precise Boundary

| Concept | Side | Nature |
|---|---|---|
| User utterance / goal | Demand | Ephemeral, any language |
| Capability | Supply catalog | Durable canonical intent class (English) |
| Knowledge unit | Implementation | Method, standard, skill, checklist, etc. |

The Orchestrator (future) matches demand → Capability → knowledge units → context package.

### Identity

```text
eos.capability.<domain>.<name>
```

Illustrative only (no catalog entries exist yet):

```text
eos.capability.design.system-architecture
eos.capability.security.review
eos.capability.data.database-selection
eos.capability.delivery.deployment-strategy
eos.capability.quality.test-planning
eos.capability.performance.optimization
eos.capability.api.design
eos.capability.scalability.review
```

---

## Responsibilities

A Capability owns:

1. **Intent definition** — what class of engineering work this fulfills
2. **Boundaries** — what is in scope and explicitly out of scope
3. **Entry signals** — how intents map here (synonyms, situations, triggers) without requiring English prompts from users
4. **Fulfillment binding** — which knowledge units primarily fulfill it (`fulfilled_by`)
5. **Arbitration guidance** — how to choose among bound units when several apply
6. **Outcome expectations** — what “done” roughly means at the capability level (not detailed standards)
7. **Discovery metadata** — enough for routing without loading all modules
8. **Lifecycle of the offer** — whether Engineering OS still claims to fulfill this intent class

---

## Non-Responsibilities

A Capability must not own:

1. **Step-by-step method** — that belongs to playbooks and workflows
2. **Quality bars in detail** — that belongs to standards and checklists
3. **AI operable procedures** — that belongs to skills
4. **Artifact skeletons** — that belongs to templates
5. **Tool packaging** — that belongs to adaptations
6. **Kernel principles** — that belongs to foundation documents
7. **Deep execution graphs of other Capabilities** — composition of work happens through knowledge-unit relationships inside fulfillment, not through a Capability call stack
8. **Organizational politics** — Capability catalogs must not become maps of teams, funding, or reporting lines

If a Capability file starts containing a full method, it has absorbed a playbook and must be split.

---

## Relationship to Knowledge Architecture

Capabilities use the same **identity, metadata, lifecycle, and relationship machinery** as knowledge units so there is one addressing system.

They are a distinct **kind**:

| | Capability | Method / content units |
|---|---|---|
| Primary question | What intent class can we fulfill? | How do we fulfill it well? |
| Body content | Boundaries, signals, arbitration, bindings | Methods, criteria, procedures, structures |
| Selected by Orchestrator first? | Yes | After Capability selection |
| Expected count at scale | Tens (coarse) | Hundreds |

### Representation Rule

A Capability is addressable as `type: capability`.

It is **not** interchangeable with `playbook`, `skill`, or `standard`. Treating Capability as “just another document in the pile” recreates the problem it exists to solve.

### New Relationship Types (Capability-Aware)

| Relationship | Meaning |
|---|---|
| `fulfilled_by` | Capability → unit that implements part or all of the intent |
| `primary_fulfillment` | Capability → preferred default unit when context is thin |
| `related_capability` | Soft adjacency; often used together; not a hard dependency |

Existing unit relationships (`depends_on`, `composes`, …) remain the mechanism for assembling execution context **after** fulfillment units are chosen.

### Consumption Protocol Impact

Logical order becomes:

1. **Frame** intent (any language)
2. **Route to Capabilities** (canonical intent classes)
3. **Select Capability** (human or policy)
4. **Bind** — resolve `fulfilled_by` / `primary_fulfillment`
5. **Assemble** context package from bound units and their graph
6. **Execute / Verify / Record** — record Capability ID **and** unit IDs

Situational discovery over raw units remains useful as a fallback and for authors. It is not the primary long-term product surface.

---

## Relationship to System Architecture

Capability sits as a **catalog layer** between contracts and modules:

```text
Adaptations
Modules (playbooks, skills, standards, …)
Capability Catalog          ← intent routing surface
Contracts
Foundation
```

Dependency rules:

```text
Capabilities  →  may depend on Foundation and Contracts
Capabilities  →  may bind to Modules via fulfilled_by
Modules       →  must not depend on Capabilities for their own validity
Adaptations   →  may package Capabilities or Modules; never become source of truth
```

A playbook must remain meaningful if discovered directly. Capabilities optimize routing; they do not imprison knowledge.

Planned directory (created only when the first Capability lands): `capabilities/`.

---

## Relationship to the Future Orchestrator

The Orchestrator should reason primarily over **Capabilities**, not over document genres.

Expected Orchestrator responsibilities (future; not implemented here):

- classify user intent into one or more Capability candidates
- disambiguate with questions when confidence is low
- select fulfillment units using Capability bindings + context
- assemble minimum context packages
- refuse or escalate when no Capability fits (instead of improvising methodology)

Expected non-responsibilities:

- inventing Capabilities at runtime
- bypassing Capability limits silently
- loading the entire module catalog “to be safe”

---

## Lifecycle

```text
draft → active → deprecated → retired
```

Same states as knowledge units, with Capability-specific meaning:

| State | Meaning |
|---|---|
| `draft` | Intent class proposed; not offered for general routing |
| `active` | Engineering OS claims it can help fulfill this intent class |
| `deprecated` | Still routable transiently; successor Capability preferred |
| `retired` | Not offered for new work; retained for audit/history |

Withdrawing a Capability means Engineering OS no longer claims that product entry point — even if underlying units remain for other bindings.

---

## Composition

### Allowed

- **Co-use**: Capability A is often used with Capability B (`related_capability`)
- **Specialization**: a narrower Capability may `specializes` a broader one when the intent class is truly narrower, not merely a different playbook
- **Multi-bind**: one Capability may be `fulfilled_by` several units with arbitration rules

### Forbidden / Strongly Discouraged

- Deep Capability dependency DAGs that mimic function calls
- Capability inheritance trees that restate organizational hierarchy
- “Mega-Capabilities” that bind dozens of unrelated units without arbitration
- Capability composing another Capability’s method body by copy-paste

### Design Rule

Compose **work** through knowledge units.  
Relate **offers** through Capabilities.  
Do not build two competing execution graphs.

---

## Discovery

Discovery priority for consumers:

1. Capability catalog (intent classes)
2. Bound fulfillment units
3. Unit graph expansion
4. Fallback: raw situational search over unit applicability/tags

Capability discovery metadata should include:

- intent summary
- trigger situations
- exclusions
- domain
- status
- primary fulfillment (if any)

User language may be any language. Capability definitions remain English. Matching may use translation, embeddings, or rules in the runtime — those mechanisms are adaptations/runtime concerns, not canonical knowledge.

---

## Versioning

| Layer | Stability | Change mode |
|---|---|---|
| Capability ID | Immutable after publish | Never rename identity |
| Intent definition / boundaries | Slow | Breaking change → new Capability + `supersedes` |
| Fulfillment bindings | Fast | Additive/rebinding without new ID when intent is unchanged |
| Arbitration guidance | Medium | Revise in place when advice improves without changing intent |

Capabilities should be versioned as **offers**.  
Knowledge units should be versioned as **implementations**.

A Capability does not need a new identity every time a checklist improves.

---

## Future Extensibility

Allowed without foundation redesign:

- adding Capabilities
- rebinding fulfillment units
- private organizational Capabilities in a separate ID namespace
- runtime classifiers that map utterances → Capability IDs

Requires foundation change:

- making Capabilities own methods
- requiring vendor-specific Capability metadata in the core
- replacing knowledge units with Capabilities as the only artifact type

Uncertainty (explicit): whether Capability specialization should be rare or common will only be known after a real catalog exists. Default stance: **prefer flat coarse catalogs**; specialize only with evidence.

---

## Examples (Illustrative)

These examples define shape, not content. No Capability files are created by this document.

### Example A — Security Review

- **ID:** `eos.capability.security.review`
- **Intent class:** Assess security posture of a design, change, or system under review
- **Out of scope:** Performing penetration tests; operating a SOC
- **Primary fulfillment:** a security review playbook (future)
- **Also bound:** threat-modeling framework, security checklist, relevant standards
- **Arbitration:** prefer checklist-led path for small changes; playbook-led path for new trust boundaries

### Example B — Database Selection

- **ID:** `eos.capability.data.database-selection`
- **Intent class:** Choose a data store under stated constraints
- **Out of scope:** Schema design deep-dive (related capability), vendor contract negotiation
- **Primary fulfillment:** decision framework for data store selection
- **Also bound:** quality attributes standard, ADR template

### Example C — Invalid Alias

- **Bad:** `eos.capability.delivery.change-introduction` that only wraps a single identically scoped playbook with no arbitration, no multi-bind, and no product-surface value
- **Why invalid:** pure alias; adds a layer without reducing routing ambiguity

---

## Anti-Patterns

| Anti-pattern | Why it harms the system |
|---|---|
| Capability = renamed playbook | Double maintenance; no routing value |
| Fine-grained explosion (“Review JWT expiry claim”) | Catalog becomes unnavigable; Orchestrator noise |
| Enterprise capability cartography | Political maps unrelated to engineering decision quality |
| Capability owns the method | Duplicates playbooks; destroys modularity |
| Hard Capability call stacks | Second execution graph; fragile orchestration |
| Vendor-named Capabilities (`cursor-review`) | Breaks AI-agnostic core |
| Mandatory Capability for every unit | Bureaucracy; units must remain directly usable |
| Capability per team or org chart node | Couples knowledge to structure that changes often |

---

## Alternatives Considered and Rejected

### 1. Organize only around Playbooks

**Rejected.** Playbooks are the right carrier for methods, not for product entry. At scale, “pick a playbook” forces consumers to understand the inventory taxonomy. Orchestration quality collapses into search over methods.

### 2. Domains + tags + applicability only

**Rejected as sufficient.** Necessary for faceting; insufficient as a governed offer layer. No arbitration owner, no stable product surface, no explicit “we fulfill this intent class.”

### 3. Intent objects without Capability catalog

**Rejected.** Raw intents are ephemeral and multilingual. The system needs canonical **intent classes** on the supply side. That supply-side object is what this document names Capability.

### 4. Skills as the primary entry point

**Rejected.** Skills are too fine-grained for “design an architecture” and too procedural for decision routing. Skills fulfill Capabilities; they should not define the catalog grain.

### 5. Enterprise Architecture capability maps

**Rejected.** Those models optimize portfolio and org alignment. Engineering OS optimizes engineering decision quality. Importing EA bureaucracy would freeze the catalog and misalign incentives.

### 6. Rename to “Intent Class” and avoid “Capability”

**Rejected as the document title, retained as the definitional core.** “Intent class” is more precise philosophically; “Capability” is the clearer product term for what the system offers. This document defines Capability **as** a canonical intent class to prevent EA semantic drift.

---

## Self-Review — Risks and Uncertainties

### Weak assumptions

1. **Orchestrator will exist and will benefit from a coarse catalog.** If Engineering OS remains human-browsed docs only, Capability value is lower (still useful as TOC, but weaker justification). Current vision assumes AI participation; this assumption must be revisited if that changes.
2. **Authors will keep Capabilities coarse.** Social pressure often pushes taxonomies toward fine grain. Process and review bar must resist that; contracts alone may not.
3. **One English catalog can serve multilingual matching.** Runtimes must handle language mapping. If they fail, users may experience Capability routing as English-centric despite policy.

### Ambiguities still open

1. Exact cardinality target (for example “20–40 active Capabilities”) — defer until evidence from first catalog drafts.
2. Whether `primary_fulfillment` should be mandatory — lean optional; mandatory rules can force fake defaults.
3. How often `specializes` should appear — default rare.
4. Whether Capabilities should live as files under `capabilities/` or also emit a generated catalog index — encoding deferred to Contracts.

### Scalability issues

- Two graphs (Capability relations + unit relations) can diverge. Mitigation: Capability graph stays shallow; unit graph does execution composition.
- Binding drift: units evolve, Capability arbitration goes stale. Mitigation: Capability review when bound units change status.

### Maintenance risks

- Orphan Capabilities with empty bindings.
- Orphan units never bound to any Capability (allowed, but then hard to discover via primary surface).
- Duplicate Capabilities with overlapping intent classes.

### Honesty statement

Capability is the **strongest long-term routing abstraction evaluated**, not a risk-free one. Its value is conditional on restraint. If the catalog becomes political or fine-grained, removing or freezing Capabilities will be healthier than pretending the model is succeeding.

---

## Summary Decision

**Accepted:** Capability is a foundation concept.

**Constrained meaning:** durable canonical intent class + fulfillment facade.

**Not accepted:** Capability as document replacement, enterprise map, or execution engine.
