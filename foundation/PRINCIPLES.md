# Principles

These principles are non-negotiable for Engineering OS itself and for content accepted into it.

They are written to remain valid as tools, languages, and AI capabilities change.

---

## System Principles

### P1 — Purpose Before Content

Every artifact must state the problem it solves and the decision or action it enables. Content without purpose is noise.

### P2 — Contracts Over Conventions Alone

Modules interact through explicit contracts: inputs, outputs, preconditions, and boundaries. Shared vocabulary matters; silent assumptions do not.

### P3 — Composition Over Coupling

Prefer small, composable units that can be combined. Avoid artifacts that force unrelated concerns to travel together.

### P4 — Stable Core, Flexible Edge

The foundation changes slowly and deliberately. Adaptations to specific tools, vendors, and environments change quickly and remain optional.

### P5 — Progressive Adoption

A team must be able to start with a single module and gain value. Full adoption must never be a prerequisite for usefulness.

---

## Engineering Principles

### P6 — Clarity Beats Cleverness

Prefer plain language, explicit trade-offs, and inspectable structure. Clever abstractions that obscure intent are liabilities.

### P7 — Evidence Over Opinion

Recommendations should be grounded in reasoned trade-offs, observed failure modes, or established engineering practice. Label opinions as opinions.

### P8 — Optimize for Change

Design guidance that helps systems evolve safely: boundaries, seams, versioning, migration paths, and reversible decisions where possible.

### P9 — Feedback Loops Are Mandatory

Every workflow should define how success and failure are detected. Work without feedback is hope, not engineering.

### P10 — Security and Reliability Are Defaults

Security, privacy, resilience, and operability are not optional later stages. They are part of competent engineering from the start.

---

## AI Collaboration Principles

### P11 — Human Accountability

AI may draft, propose, generate, and accelerate. Humans remain accountable for decisions that affect users, systems, and organizations.

### P12 — Spec Before Generation

Prefer stating intent, constraints, and acceptance criteria before asking AI to produce implementation. Generation without specification amplifies ambiguity.

### P13 — Review Is Part of the Workflow

AI output enters the engineering system through review, verification, and integration — never through blind trust.

### P14 — Portable Skills

Skills must encode reusable engineering capability, not proprietary prompt tricks for a single model or product.

### P15 — Determinism Where It Matters

When reproducibility, auditability, or safety matters, prefer explicit checklists, decision records, and verifiable steps over free-form improvisation.

---

## Content Principles

### P16 — One Source of Truth

Canonical knowledge lives in this repository in English. Duplication across tools is derived, not authoritative.

### P17 — Timeless Over Trendy

Prefer principles, patterns, and decision frameworks that survive fashion cycles. Version or isolate guidance that is inherently ephemeral.

### P18 — Minimal Necessary Surface

Do not add files, layers, or process for aesthetics of completeness. Complexity must justify itself.

### P19 — Explicit Deferred Decisions

What is intentionally undecided should be written down. Silence creates accidental architecture.

### P20 — Deprecation Is Design

Removal and retirement are first-class operations. Obsolete guidance must be marked, migrated, or deleted — not left to rot.
