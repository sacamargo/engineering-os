# Phase 7 Delivery Audit

Audit before implementing Delivery / CI/CD runtime.

**Rule:** Reuse Phase 3–6 models. Do not invent a parallel Gate/Evidence/Failure/ChangeSet stack.

---

## What already exists (reuse)

| Concept | Location | Notes |
|---|---|---|
| Delivery boundary (doc) | `foundation/DELIVERY-MODEL.md` | Planning vs Execution vs Delivery; **extend** |
| Delivery stub | `orchestration/boundaries/delivery.py` | Replace stub with real coordinator call |
| Artifact (execution) | `foundation/ARTIFACT-MODEL.md`, contracts | Work-product artifacts; Delivery adds **build/package** artifacts |
| ChangeSet | `agents/changeset.py` | Source of delivery inputs |
| Evidence | Evidence Model + `agents/evidence.py` | Chain into Delivery |
| Gates | `foundation/VALIDATION-GATES.md`, `orchestration/gates/` | Reuse; add delivery-specific gate conditions |
| Failure / retry | `foundation/FAILURE-MODEL.md`, `agents/retry.py`, `agents/failures.py` | Extend classes for build/test/security/delivery |
| Approval | `agents/approval.py` | Reuse for high-risk release/deploy decisions |
| Sandbox / allowlist | `agents/sandbox.py`, `agents/tools/commands.py` | Build/test executors must reuse |
| Concurrency lock | `agents/concurrency.py` | One writer / delivery lock per workspace |
| Codebase Intelligence | `codebase/` | Risk + findings feed delivery readiness |
| Change impact | `codebase/impact.py` | Inform risk classification |
| Orchestrator | `orchestration/facade/` | May request delivery readiness; must not own CI vendors |
| Agent runtime | `agents/loop.py` | Produces ChangeSet; stops before Delivery |
| Decision model | `foundation/DECISION-MODEL.md` | Release decisions |

---

## What is missing (new in Phase 7)

| Gap | Planned home |
|---|---|
| Delivery / Build / ValidationRun / Pipeline / Environment / ReleaseCandidate models | `delivery/` + extend DELIVERY-MODEL |
| Delivery state machine | `delivery/states.py` |
| Local build/test/artifact executors (allowlisted) | `delivery/runtime/` |
| DeliveryAdapter boundary (no real cloud deploy) | `delivery/adapter.py` |
| Release readiness + decision | `delivery/release.py` |
| Deployment boundary (READY_FOR_DEPLOYMENT only) | `delivery/deployment.py` |
| Rollback model (traceability, not infra) | `delivery/rollback.py` |
| Delivery permissions | extend agent permission vocabulary |
| CLI `deliver` | `delivery/cli.py` |
| Contracts for delivery objects | `contracts/delivery/` |
| Phase 7 validation docs | `docs/PHASE-7-*.md` |

---

## Distinctions that must stay hard

```text
Delivery ≠ Deployment
CI ≠ CD
Build ≠ Release
Release ≠ Deployment
Artifact (build) ≠ Source code
Evidence ≠ Success
Approval ≠ Execution
Environment ≠ Cloud provider
ChangeSet (agent) → input to Delivery, not Delivery itself
```

---

## Out of scope (Phase 7+)

- Real production deploy
- Kubernetes / AWS / GCP / Azure / Vercel adapters beyond stubs
- Secret management
- Auto-approval of production
- Swarm / multi-writer delivery
- Mandatory LLM
- Vendor CI (GitHub Actions, Jenkins) inside core

---

## Package

New runtime package: **`delivery/`** (not inside Orchestrator or Agents).

Flow:

```text
ChangeSet → Build → Artifact → ValidationRun → Gates → ReleaseCandidate → Readiness
                                                                      ↘ DeploymentAdapter (boundary only)
```
