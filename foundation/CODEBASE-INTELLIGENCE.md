# Codebase Intelligence (Foundation)

Specifies how Engineering OS should treat a repository as **evidence**, not as a prompt dump.

**Phase 3 does not implement a full indexer.** This document defines the contract for later phases.

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Analyze/refactor/migrate intents need structured repo understanding. |
| Problem avoided | Guessing architecture from filenames alone. |
| If absent | Agency scenarios stay abstract forever. |

---

## Evidence Surfaces

| Surface | Questions answered |
|---|---|
| Structure | packages, services, boundaries |
| Dependencies | internal/external coupling |
| Git history | churn, ownership hints, regression risk |
| Architecture | documented vs observed |
| Conventions | lint, style, patterns |
| Tests | coverage shape, critical paths |
| CI/CD | gates already enforced |
| Configuration | envs, feature flags, secrets handling |
| Documentation | claimed behavior |
| Technical debt | known hotspots |

---

## Rules

1. Repository evidence is first-class for Analysis/Audit/Refactor intents.
2. Claims about the codebase must cite evidence (path, test, CI job, commit) when available.
3. Absence of evidence is a gap — not permission to invent.
4. Codebase Intelligence feeds Plan Generation; it is not a Capability by itself until intentionally catalogued.
5. Vendor tools (IDE indexers) are Adapters — Core remains vendor-neutral.

---

## Non-Goals (Phase 3)

- Full semantic index
- Continuous repo watching
- Automatic PR writing runtime
