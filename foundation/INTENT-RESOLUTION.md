# Intent Resolution

This document defines how Engineering OS should move from a human request to **Capability candidates** and a provisional selection.

It formalizes steps **Frame → Route → Select** from [Knowledge Architecture](KNOWLEDGE-ARCHITECTURE.md) without implementing an Orchestrator, embeddings, or vendor-specific routing.

Architectural companions:

- [Capability Model](CAPABILITY-MODEL.md) — what a Capability is
- [System Architecture](SYSTEM-ARCHITECTURE.md) — where routing sits
- Experiment: `experiments/intent-disambiguation/`

---

## Problem

Users do not know the Capability catalog.

They express outcomes in any language. Engineering OS must interpret demand into supply-side intent classes **already offered** by the catalog.

Engineering OS must also recognize when the catalog cannot honestly fulfill a request.

---

## Non-Goals

This document does **not**:

- implement an Orchestrator
- define LLM prompts as source of truth
- reduce routing to keyword → Capability maps
- invent Capabilities at runtime
- retrieve Knowledge Unit bodies before Capability selection (except metadata needed for routing)

---

## Core Distinctions

| Concept | Meaning |
|---|---|
| **Utterance** | Raw user text (any language) |
| **Intent frame** | Structured reading of the request |
| **Candidate Capabilities** | Catalog offers that *might* fit |
| **Selected Capabilities** | Provisional primary (+ optional secondary) after disambiguation |
| **Related Capabilities** | Soft adjacency via `related_capability`, not an execution DAG |
| **Fulfillment preview** | Bound units suggested after selection |
| **Insufficient coverage** | Honest gap when no catalog Capability fits |

Candidates are not selections. Selections are not fulfillment execution.

---

## Intent Frame

Before matching Capabilities, frame the request along multiple axes.

Keyword presence alone is never sufficient.

| Axis | Question |
|---|---|
| Desired outcome | What should be true when the work succeeds? |
| Object of work | What is being acted on (app, architecture, change, incident…)? |
| Intent class hint | Is the user asking to design, review, fix, optimize, build, investigate…? |
| Domain hints | Security, architecture, data, performance… (hints, not verdicts) |
| Constraints | Hard limits (scale, offline, compliance, deadline) |
| Risk signals | Safety, abuse, trust-boundary, production impact |
| Context sufficiency | What is unknown that changes routing? |
| Multi-intent? | Are multiple distinct outcomes bundled? |

### Framing Rules

1. Separate **outcome verbs** from **domain nouns**.  
   “Build a secure SaaS” is not automatically Security Review.
2. Separate **review/audit** from **design/build** and from **fix/implement**.
3. Treat constraints as selectors among candidates, not as Capability inventers.
4. When multiple outcomes are bundled, prefer multiple candidates over one mega-Capability.
5. Conversation language may differ from canonical English knowledge.

---

## Candidate Resolution

### Inputs

- Intent frame
- Active Capability catalog metadata (`summary`, `purpose`, `applicability`, `limits`, `entry_signals`, relationships)

### Outputs

```text
resolution = {
  utterance,
  frame,
  candidates: [{ id, rationale, confidence }],
  primary: id | null,
  secondary: [id...],
  related_suggested: [id...],
  insufficient_coverage: [{ missing_intent_class, reason }],
  clarifying_questions: [string...],
  fulfillment_preview: { primary_unit, also: [unit ids] } | null
}
```

### Resolution Rules

1. **Catalog-bound** — every selected or candidate ID must already exist and be `active` (or explicitly `deprecated` with warning). Never invent IDs.
2. **Primary ⊆ candidates** — primary must appear in candidates when set.
3. **Secondary ⊆ candidates** — secondary capabilities must also be candidates.
4. **Limits matter** — if the request matches a Capability’s `limits` more than its `applicability`, do not select it as primary.
5. **Related is soft** — `related_capability` may populate `related_suggested`; it never implies order, ownership, or mandatory co-execution.
6. **Insufficient coverage is success** — refusing to fake a Capability is correct behavior.
7. **Clarify when ambiguous** — low-confidence multi-intent cases should ask before pretending certainty.
8. **Fulfillment after selection** — bind `primary_fulfillment` / `fulfilled_by` only after primary is chosen.

### Confidence

| Level | Meaning |
|---|---|
| `high` | Frame strongly matches applicability; limits do not dominate |
| `medium` | Plausible fit; ambiguity or partial overlap remains |
| `low` | Weak fit; include only to surface alternatives or ask questions |

---

## Worked Routing Patterns

### Clear primary

Utterance centers on one intent class offered by the catalog → one high-confidence candidate → primary set → fulfillment preview from bindings.

### Primary + related

Utterance is a security review *of architecture* → Security Review primary; System Architecture may be secondary or related_suggested via adjacency, not a hard prerequisite.

### Multi-intent / ambiguous build

“Build a secure scalable SaaS…” bundles design, security, scale, availability. Candidates may include Architecture and Security. Primary may remain unset pending clarifying questions. Do not collapse into one Capability.

### Catalog gap

Performance/database diagnosis with no matching Capability → `insufficient_coverage`. Do not invent `eos.capability.performance.*` at runtime.

---

## Anti-Patterns

| Anti-pattern | Why it fails |
|---|---|
| Keyword → Capability | “secure” would always route to Security Review |
| Inventory browsing as UX | Forces users to learn internal taxonomy |
| Inventing Capabilities | Breaks catalog governance and auditability |
| Capability DAG execution | Recreates a second orchestration graph |
| Selecting fulfillment before Capability | Skips intent routing; collapses into document search |
| Silent overconfidence on multi-intent builds | Hides missing coverage and needed clarification |

---

## Relationship to Future Orchestrator

A future Orchestrator may automate framing and candidate proposal.

This document remains the vendor-neutral contract for what “correct routing” means:

- frame before match
- candidates before selection
- catalog before invention
- related ≠ required
- insufficient coverage is first-class

Runtime techniques (LLM classification, embeddings, rules) are adaptations of this protocol — not replacements for it.

---

## Experiment

Concrete authored cases and a structural evaluator live in:

`experiments/intent-disambiguation/`

The evaluator checks resolution-record integrity against the live Capability catalog. It does **not** classify free text automatically.
