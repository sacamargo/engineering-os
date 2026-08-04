# Engineering Workflow

This document defines how **Engineering OS itself** is developed.

Engineering OS is built like a professional software product: deliberate changes, reviewable history, and repository discipline — even though the product is a knowledge system rather than an application binary.

---

## Purpose

The workflow exists to ensure:

- every change has a clear intent
- history remains readable years later
- foundation changes stay rare and explicit
- knowledge units can evolve without chaotic commits
- AI-assisted contributions follow the same bar as human ones

---

## Branching Model

Use **feature branches**. Do not develop directly on the default branch once Git history exists.

### Branch Types

| Branch | Purpose | Naming |
|---|---|---|
| Default branch (`main`) | Stable, accepted state of the system | `main` |
| Feature / change branch | One logical unit of work | `feat/<short-slug>`, `fix/<short-slug>`, `docs/<short-slug>`, `refactor/<short-slug>`, `chore/<short-slug>` |

### Rules

1. Create a branch from an up-to-date default branch
2. Keep the branch scoped to one concern
3. Prefer short-lived branches
4. Merge only when the change set is coherent and complete for its stated intent
5. Do not mix unrelated foundation edits with unrelated module drafts on the same branch

### Examples

```text
feat/knowledge-architecture
docs/system-architecture-rename
fix/principle-p19-wording
chore/ignore-editor-files
```

---

## Commit Standard — Conventional Commits

All commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```text
<type>(<optional-scope>): <description>

[optional body]

[optional footer(s)]
```

### Allowed Types

| Type | Use for |
|---|---|
| `feat` | A new capability of the system or a new knowledge unit |
| `fix` | Correction of incorrect content, structure, or workflow guidance |
| `docs` | Documentation-only changes that do not alter system meaning materially |
| `refactor` | Restructure without changing intended meaning |
| `chore` | Maintenance that does not change product knowledge (ignore files, housekeeping) |
| `revert` | Revert of a previous commit |

Use `docs` for purely editorial clarity. Use `fix` when prior content was wrong. Use `feat` when the platform gains new durable capability (including new foundation architecture documents or new knowledge units).

### Scopes (Recommended)

Scopes should name the area touched:

```text
foundation, system, knowledge, capability, workflow, roadmap,
playbook, skill, standard, framework, checklist,
template, workflow-module, adaptation, contracts
```

Examples:

```text
feat(capability): define intent-class routing model
feat(knowledge): define AI consumption protocol
fix(system): correct adaptation dependency direction
docs(workflow): clarify branch naming examples
refactor(foundation): split architecture into system and knowledge
```

### Description Rules

- Imperative mood: `define`, `add`, `remove`, `rename` — not `defined` or `adds`
- Lowercase description (unless proper nouns / IDs)
- No trailing period
- Maximum ~72 characters for the subject line when practical
- Describe **why-facing intent** briefly; put detail in the body when needed

### Body Rules

Use a body when the subject is not enough:

- What problem motivated the change
- Trade-offs considered
- Migration notes for breaking foundation changes
- Related unit IDs (once units exist)

---

## Small Commits — One Logical Change

### Definition

One commit = one logical change that can be reasoned about, reverted, or reviewed independently.

### Do

- Rename a document in a commit dedicated to that rename (or a tightly coupled rename + reference update set)
- Add one architecture concern per commit when changes are separable
- Keep reference updates with the change that invalidates old paths

### Do Not

- Combine “rewrite philosophy” + “add twelve playbooks” in one commit
- Mix formatting churn with semantic changes
- Hide deletions inside unrelated feature commits
- Produce kitchen-sink commits such as `feat: update everything`

### Practical Test

If the commit message needs “and” to list unrelated concerns, split the commit.

---

## Change Workflow

1. **Frame** — state the problem and the intended outcome
2. **Branch** — create a named feature branch
3. **Change** — edit only what the outcome requires
4. **Commit** — small Conventional Commits as logical steps land
5. **Review** — check principles, architecture fit, and deferred-decision honesty
6. **Integrate** — merge to the default branch when the branch intent is complete

AI assistants contributing to this repository must follow the same workflow. Generated bulk dumps are not acceptable history.

---

## Repository Organization Principles

These principles govern how the repository is shaped over time.

### R1 — Purpose-Bearing Paths Only

Every file and directory must have an immediate purpose. No placeholder folders. No empty scaffolds. No “reserved for later” files.

### R2 — Kernel Stability

`foundation/` changes slowly. Prefer additive clarification over silent reinterpretation. Breaking changes require migration notes in the commit body.

### R3 — Architecture Before Inventory

Declare structure in architecture documents before creating module directories. Create a directory only when the first real knowledge unit of that type arrives.

### R4 — Names Encode Responsibility

Prefer explicit names over generic ones when ambiguity is costly:

- `SYSTEM-ARCHITECTURE.md` over `ARCHITECTURE.md`
- `PROJECT-ROADMAP.md` over `ROADMAP.md`
- `KNOWLEDGE-ARCHITECTURE.md` for the knowledge substrate

### R5 — Canonical English Knowledge

Canonical files are professional English. Conversation about changes may occur in any language; landed artifacts remain English.

### R6 — No Ceremony Files Without Need

Do not add common open-source files (`LICENSE`, `CONTRIBUTING.md`, code-of-conduct, templates, CI) until the project need is real. Premature ceremony creates false readiness.

### R7 — History Is Part of the Product

Commit history is a knowledge artifact about how the system evolved. Optimize for future readers, not for local convenience.

### R8 — Align With Knowledge Architecture

Once module content exists, organization must honor knowledge unit identity, metadata, and relationships — not ad-hoc document piles.

---

## Review Bar for Changes

Before integrating a change, verify:

1. Does it serve a stated purpose?
2. Does it comply with Principles and both architecture documents?
3. Is it the minimal change that achieves the intent?
4. Are deferred decisions still explicit?
5. Would the commit history explain this a year from now?

---

## Current Phase Constraints

While the project remains in foundation / pre-contracts work:

- Do not land playbooks, skills, templates, or adaptations yet
- Prefer improving kernel clarity over expanding surface area
- Knowledge Architecture, Capability Model, and System Architecture outrank local convenience

When Git is initialized, this workflow becomes mandatory for all subsequent history.
