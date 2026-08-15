# Delivery Model

Separates **Planning**, **Execution**, and **Delivery**.

Runtime: `delivery/` (Phase 7). Deployment remains an **adapter boundary** — not core execution.

Authorities: [ARTIFACT-MODEL](ARTIFACT-MODEL.md), [VALIDATION-GATES](VALIDATION-GATES.md), [EVIDENCE-MODEL](EVIDENCE-MODEL.md), [DECISION-MODEL](DECISION-MODEL.md), audit [`docs/PHASE-7-DELIVERY-AUDIT.md`](../docs/PHASE-7-DELIVERY-AUDIT.md).

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Keep “work coordination” distinct from “shipping readiness”. |
| Problem avoided | Orchestrator owning CI/CD vendors; plans that pretend deploy happened. |
| If absent | False completion when code exists but is not releasable. |

---

## Layers

```text
Planning   → what should be true (Execution Plan)
Execution  → performing Tasks / producing ChangeSets (agents/)
Delivery   → build → validate → artifact → gates → release readiness
Deployment → adapter boundary only (READY_FOR_DEPLOYMENT ≠ deployed)
```

---

## Hard distinctions

| Do not confuse | Meaning |
|---|---|
| Delivery ≠ Deployment | Delivery prepares/validates; Deployment lands in an environment via adapter |
| CI ≠ CD | Validation pipeline ≠ continuous deploy |
| Build ≠ Release | Compilation/package ≠ versioned release decision |
| Release ≠ Deployment | Approved candidate ≠ running in prod |
| Artifact ≠ Source | Build/package/report ≠ working tree files |
| Evidence ≠ Success | Logs/reports required; claims alone insufficient |
| Approval ≠ Execution | Human decision ≠ pipeline step running |
| Environment ≠ Provider | `staging` ≠ AWS/Vercel |

---

## Core flow

```text
ChangeSet
  → Build
  → DeliveryArtifact
  → ValidationRun(s)
  → Gates
  → ReleaseCandidate
  → DeliveryDecision / Readiness
  → (optional) DeploymentAdapter
```

---

## Rules

1. Delivery is not Knowledge and not a Capability.
2. Delivery adapters (GitHub Actions, clouds) are replaceable — core stays vendor-neutral.
3. Never `succeeded` / `released` without evidence and satisfied gates.
4. Agents cannot self-approve releases or execute production deploy.
5. Deny-by-default permissions for BUILD/RELEASE/DEPLOY.
6. Security status `unknown` blocks automatic release.
7. Zero tests executed ≠ tests passed.

---

## Out of scope (Phase 7)

Real cloud deploy, secret management, auto-prod approval, vendor CI inside core.
