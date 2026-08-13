# Rivallium Execution Plan (Narrative)

This document is the human-readable companion to the machine bundle under `examples/rivallium/`.

It demonstrates that Engineering OS can turn a high-level intent into a coherent Execution Plan **without** the user naming specialists, Capabilities, Playbooks, or task order.

---

## Intent

> Build Rivallium — a court-booking SaaS with strong uniqueness guarantees, security review, test strategy, and observability.

User does **not** say: “Act as Architect + Security + QA + DevOps.”

---

## Capability Resolution

### Known (live catalog)

| Capability | Why |
|---|---|
| `eos.capability.design.system-architecture` | System shape for booking authority, clients, integrations |
| `eos.capability.security.review` | Threat model for auth, payment, booking abuse |
| `eos.capability.quality.test-planning` | Concurrency / double-booking validation strategy |
| `eos.capability.operations.observability` | Booking SLIs, alerts, traces |

### Insufficient coverage (do not invent IDs)

| Area | Needed for | Escalation |
|---|---|---|
| database_engineering | Schema / uniqueness | human_or_future_capability |
| backend_implementation | Booking API / services | human_or_future_capability |
| frontend_implementation | Player / venue UI | human_or_future_capability |
| devops_delivery | CI/CD / deploy topology | human_or_future_capability |

Roles still compose for those areas (`database-engineer`, `backend-engineer`, `frontend-engineer`, `devops-engineer`) — **Role ≠ Capability**.

---

## Artifacts

| Artifact | Type | Notes |
|---|---|---|
| `eos.artifact.rivallium.architecture` | architecture | Primary design artifact |
| `eos.artifact.rivallium.threat-model` | threat_model | Depends on architecture |
| `eos.artifact.rivallium.test-strategy` | test_strategy | Depends on architecture |
| `eos.artifact.rivallium.observability-plan` | observability_plan | Depends on architecture |
| `eos.artifact.rivallium.database-schema` | database_schema | Gap-aware (blocked) |
| `eos.artifact.rivallium.api-contract` | api_contract | Gap-aware (blocked) |
| `eos.artifact.rivallium.frontend-plan` | ui_plan | Gap-aware (blocked) |
| `eos.artifact.rivallium.deployment-plan` | deployment_plan | Gap-aware (blocked) |

Artifacts are **results**, not Knowledge Units.

---

## Tasks

### Executable with live Capabilities

```text
design-architecture (ready)
        ├─► security-review (pending)
        ├─► test-planning (pending)
        └─► observability-design (pending)
```

These three dependents are **parallel** after architecture completes.

### Blocked on coverage gaps

```text
design-architecture
        ├─► database-schema (blocked: missing_capability_coverage)
        │         └─► api-contract (blocked)
        │                   └─► frontend-plan (blocked)
        └─► deployment-plan (blocked)
```

Blocked tasks remain in the plan for honesty and replanning — they are not silently invented as Capabilities.

---

## Execution Dependencies (not knowledge links)

| From | Depends on | Kind |
|---|---|---|
| security-review | design-architecture | task_depends_on_task |
| test-planning | design-architecture | task_depends_on_task |
| observability-design | design-architecture | task_depends_on_task |
| database-schema | design-architecture | task_depends_on_task |
| api-contract | database-schema | task_depends_on_task |
| frontend-plan | api-contract | task_depends_on_task |
| deployment-plan | design-architecture | task_depends_on_task |
| security-review | architecture artifact | task_requires_artifact |

`Architecture references Security` (knowledge adjacency) is **not** the same as “Security must execute after Architecture.” Here the execution dependency is explicit and intentional.

---

## Validation Gates

| Gate | Evidence | On failure |
|---|---|---|
| Architecture Gate | architecture artifact + design task | block dependents |
| Security Gate | threat model + security task | block release-critical path |
| Test Gate | test strategy | block claiming readiness |

“Looks correct” is never sufficient when a gate defines verifiable evidence.

---

## Decision (example)

`eos.decision.rivallium.postgres-authority`

- **Choice:** PostgreSQL as booking authority  
- **Reason:** Strong uniqueness / transactional guarantees  
- **Alternatives:** Event sourcing; distributed locks only  
- **Validation:** Double-booking integration tests (when implementation coverage exists)

---

## What this proves

Engineering OS can answer, for Rivallium:

| Question | Answered by |
|---|---|
| What to build? | Project objective / intent |
| Why? | Constraints + decision reason |
| Which Capabilities? | `capability_ids` + gaps |
| Which knowledge? | Fulfillment under those Capabilities |
| Which specialists? | `role_ids` (composed, not user-selected) |
| Which artifacts? | Artifact set |
| Which tasks / order / parallel? | Task graph |
| What to validate? | Gates |
| What risks / human needs? | Gaps + blocked tasks |
| What’s done / blocked? | Status fields |

Machine validation:

```bash
python3 contracts/validate_execution.py --examples examples
```

Bundle: `project.json`, `plan.json`, `artifacts/`, `tasks/`, `gates/`, `decisions/`, `roles/`.
