# Contracts Specification

This document is the **executable authority** for Knowledge Unit and Capability encoding in Engineering OS.

Architectural meaning remains in Foundation:

- [Knowledge Architecture](../foundation/KNOWLEDGE-ARCHITECTURE.md)
- [Capability Model](../foundation/CAPABILITY-MODEL.md)
- [System Architecture](../foundation/SYSTEM-ARCHITECTURE.md)

Contracts formalize invariants. They do not redefine intent.

---

## Scope (Phase 1)

In scope:

- On-disk metadata encoding (YAML front matter)
- Identity rules
- Required and optional metadata
- Lifecycle / status values
- Relationship types and structural constraints
- Catalog-level validation (duplicates, broken references, cycles)
- Capability-specific relationship ownership

Out of scope (deferred):

- Body ↔ metadata link consistency scanning
- Closed domain / tag taxonomies
- Unit-level semver policy
- Context package runtime schema
- Automated Capability anti-pattern detection beyond structural rules
- Multilingual retrieval / translation
- Generated catalogs and indexes
- Path-to-ID enforcement (paths may vary; IDs are authoritative)

---

## On-Disk Encoding

Knowledge units and Capabilities are Markdown files with YAML front matter:

```text
---
<metadata>
---
<body>
```

- Canonical body language is English (`language` defaults to `en` when omitted).
- Foundation documents under `foundation/` are kernel documents, not units. They are not validated as units.
- Module directories (`capabilities/`, `playbooks/`, …) appear only when real content lands.

---

## Identity

### Pattern (first-party)

```text
eos.<type>.<domain>.<name>
```

Where:

- `<type>` ∈ unit types below
- `<domain>` and `<name>` match `^[a-z][a-z0-9-]*$`
- Full ID match:

```text
^eos\.(capability|playbook|framework|standard|workflow|skill|template|checklist|adaptation)\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$
```

### Rules

1. `id` is required and immutable after publish.
2. The `<type>` segment MUST equal metadata `type`.
3. If metadata `domain` is present, it MUST equal the `<domain>` segment of `id`.
4. Duplicate `id` values across the validated catalog are forbidden.
5. Private / organizational namespaces (for example `acme.*`) are allowed later; Phase 1 validation covers first-party `eos.*` units only.

---

## Unit Types

| Type | Kind |
|---|---|
| `capability` | Intent-class routing facade |
| `playbook` | Fulfillment module |
| `framework` | Fulfillment module |
| `standard` | Fulfillment module |
| `workflow` | Fulfillment module |
| `skill` | Fulfillment module |
| `template` | Fulfillment module |
| `checklist` | Fulfillment module |
| `adaptation` | Peripheral packaging module |

---

## Lifecycle

`status` is required:

```text
draft | active | deprecated | retired
```

Deprecation policy:

- Prefer `supersedes` relationships for successors.
- `deprecated` and `retired` units remain addressable for history.
- Validators must still resolve their IDs when referenced.
- Runtime consumption rules (do not silently load deprecated/retired for new work) belong to the Orchestrator; contracts only encode status correctly.

---

## Required Metadata

### Universal (all types)

| Field | Type | Notes |
|---|---|---|
| `id` | string | Stable identity |
| `type` | string | Unit type |
| `title` | string | Non-empty |
| `summary` | string | Non-empty; routing-sized |
| `purpose` | string | Non-empty |
| `audience` | string | Non-empty; roles, not vendors |
| `status` | string | Lifecycle value |
| `applicability` | string | Non-empty |
| `limits` | string | Non-empty |

### Fulfillment modules (all types except `capability`)

| Field | Type | Notes |
|---|---|---|
| `inputs` | string[] | Non-empty list; each item non-empty |
| `outputs` | string[] | Non-empty list; each item non-empty |

Capabilities intentionally omit mandatory `inputs` / `outputs` so they do not absorb method I/O. Capability Model owns intent boundaries; modules own methods.

### Optional metadata

| Field | Type | Notes |
|---|---|---|
| `principles` | string[] | Principle IDs such as `P1` |
| `tags` | string[] | Open vocabulary |
| `domain` | string | Open vocabulary; must match ID domain if set |
| `complexity` | `low` \| `medium` \| `high` | Soft guidance |
| `estimated_effort` | string | Human guidance only |
| `language` | string | If present, must be `en` for canonical units |
| `version` | string | Free-form revision marker; semver policy deferred |
| `relationships` | object[] | See below |
| `entry_signals` | string[] | Capability-oriented; optional |
| `outcome_expectations` | string | Capability-oriented; optional |
| `arbitration` | string | Capability-oriented; optional |

Unknown fields are allowed (extensibility) unless they break typed fields above.

---

## Relationships

### Encoding

```yaml
relationships:
  - type: depends_on
    target: eos.checklist.review.pull-request-quality
```

Each item requires `type` and `target`.

### Allowed types

`references`, `depends_on`, `composes`, `specializes`, `alternative_to`, `supersedes`, `conflicts_with`, `fulfilled_by`, `primary_fulfillment`, `related_capability`

### Structural rules

1. Every `target` MUST exist in the validated catalog.
2. `depends_on` ∪ `composes` MUST be acyclic.
3. Only `type: capability` may declare `fulfilled_by`, `primary_fulfillment`, or `related_capability`.
4. `fulfilled_by` and `primary_fulfillment` targets MUST NOT be `capability`.
5. `related_capability` targets MUST be `capability`.
6. Non-`adaptation` units MUST NOT `depends_on` or `composes` an `adaptation`.
7. Modules (non-capabilities) remain valid without any Capability binding.

---

## Progressive Adoption

- A unit may exist without being bound to any Capability.
- A Capability may exist in `draft` with zero fulfillment bindings.
- Validators must not require a complete catalog, Orchestrator, or adaptations.

---

## Validation Tooling

Executable entrypoint:

```text
python3 contracts/validate.py
python3 contracts/validate.py --root <dir>
```

Exit codes:

- `0` — no violations (including zero units)
- `1` — one or more violations
- `2` — usage / IO error

Machine-readable schema mirror: `unit.schema.json` (single-unit metadata shape). Catalog rules (duplicates, references, cycles) are enforced by the validator beyond JSON Schema.

---

## Why These Contracts Exist

| Contract area | Problem solved | If absent |
|---|---|---|
| Stable IDs | Durable references across renames | Path folklore; broken orchestration |
| Required metadata | Route without reading bodies | Undifferentiated document pile |
| Typed relationships | Deterministic composition | Ambiguous wiki links for AI |
| Lifecycle | Prevent zombie guidance | Silent abandonment |
| Capability relationship ownership | Keep methods out of routing facades | Capabilities become playbooks |
| Catalog validation | Detect broken graphs early | Scale collapse under hundreds of units |

---

## Deferred Decisions

Recorded explicitly (P19):

1. Exact path layout per type/domain
2. Semver rules for `version`
3. Closed controlled vocabularies for `domain` / `tags`
4. Automated detection of Capability 1:1 playbook aliases
5. Body link linting against metadata relationships
6. Context package schema for Orchestrator runtimes
7. Validation policy for private ID namespaces
8. Whether `primary_fulfillment` becomes mandatory after catalog evidence
