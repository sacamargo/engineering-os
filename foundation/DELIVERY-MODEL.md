# Delivery Model

Separates **Planning**, **Execution**, and **Delivery**.

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Keep “work coordination” distinct from “shipping to production”. |
| Problem avoided | Orchestrator owning CI/CD details; plans that pretend deploy happened. |
| If absent | False completion when code exists but is not releasable. |

---

## Layers

```text
Planning   → what should be true (Execution Plan)
Execution  → performing Tasks / producing Artifacts
Delivery   → landing change in the world (repo, CI, deploy, release)
```

---

## Delivery Eventually Covers

| Area | Notes |
|---|---|
| Repository | branches, commits, PRs |
| Code | implementation artifacts |
| Tests | automated verification |
| CI/CD | pipelines as gates |
| Deployment | environments |
| Release | versioning / notes |
| Rollback | recovery path |

---

## Rules

1. Delivery is not Knowledge.
2. Delivery adapters (GitHub Actions, cloud consoles) are replaceable.
3. Phase 3 defines the boundary only — no delivery runtime.
4. A project may be `completed` at planning/design scope without delivery; scope must be explicit.
