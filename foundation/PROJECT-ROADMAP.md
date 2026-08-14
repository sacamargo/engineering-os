# Project Roadmap

This roadmap defines the long-term evolution of Engineering OS.

It is directional, not a delivery schedule. Dates are intentionally absent. Sequence matters more than calendar promises.

**Do not treat future phases as implemented.** Only checked items are landed.

---

## Phase 0 — Foundation

Establish the kernel of the system.

- [x] Vision, philosophy, principles
- [x] System architecture + knowledge architecture
- [x] Capability model
- [x] Engineering workflow (Git + repository discipline)
- [x] Project roadmap
- [ ] Public license decision (deferred)
- [ ] Public contribution guide (deferred)

**Exit criteria:** A new reader understands what Engineering OS is and is not.

---

## Phase 1 — Contracts

Enforceable Knowledge Architecture / Capability encoding.

- [x] Knowledge unit metadata schema + validator
- [x] Relationship and ID invariants
- [x] Live catalog validation

**Exit criteria:** Capabilities and units can be authored against explicit contracts.

---

## Phase 2 — Capability Proof

Minimum operational Capability catalog + agency MVP routing.

- [x] Architecture, security review, test planning, observability Capabilities
- [x] Fulfillment playbooks/frameworks
- [x] Intent resolution + agency routing skill
- [x] Cursor adaptation (thin)

**Exit criteria:** Multi-capability intents can be routed without inventing coverage.

---

## Phase 3 — Execution Model (current)

Architecture that turns Capabilities into coordinated engineering execution.

- [x] Execution Layer audit
- [x] Execution / Project / Task / Artifact / Dependency models
- [x] Validation gates, roles, bindings, plan generation, gaps, escalation
- [x] Evidence + decision models
- [x] Execution contracts + validator + tests
- [x] Rivallium + padel-iot fixtures
- [x] Agency / role / missing-capability tests
- [x] State / failure / replan / change-impact models
- [x] Codebase intelligence / delivery / orchestrator / agent / adapter boundaries
- [x] System architecture + README + roadmap alignment

**Exit criteria:** A project like Rivallium can be represented as Intent→Capabilities→Artifacts→Tasks→Gates with honest gaps — without a production orchestrator.

**Non-goals for Phase 3:** autonomous runtime, deep Cursor integration, production delivery control plane.

---

## Phase 4 — Orchestration

Implement a minimal Orchestrator that coordinates plans without becoming a god object.

Expected work:

- Plan generation assistance against live catalog
- Task readiness evaluation
- Gate evaluation hooks
- Explicit replan / escalate paths

**Not started.**

---

## Phase 5 — Codebase Intelligence

Treat repositories as evidence sources for analyze/refactor/migrate intents.

Expected work:

- Structure/dependency/test/CI evidence extraction
- Claim→evidence linking
- Integration with plan generation

**Not started** (foundation doc only).

---

## Phase 6 — Agent Execution

Flexible executors that run tasks using knowledge units and role metadata.

Expected work:

- Agent runtime boundary implementation
- Avoid one-agent-per-role zoo
- Tool-use policies + failure handling

**Not started** (boundary doc only).

---

## Phase 7 — Delivery / CI/CD

Land changes through repository, tests, pipelines, deploy, release, rollback.

Expected work:

- Delivery adapters (GitHub/CI/cloud)
- Map gates to pipeline evidence
- Rollback playbooks bound to Capabilities as warranted

**Not started** (boundary doc only).

---

## Phase 8 — Production Operations

Incident, reliability, and operational loops as first-class agency work.

Expected work:

- Incident investigation execution paths
- SLO/error-budget tied observability
- Change management under production constraints

**Not started.**

---

## Phase 9 — Continuous Evolution

Operate Engineering OS for decades: prune, version, learn, extend.

Expected work:

- Knowledge lifecycle operations
- Catalog growth without Role/Capability collapse
- Stewardship model

**Not started.**

---

## Explicit Non-Goals (Near Term)

- Building a commercial SaaS control plane now
- Creating hundreds of shallow prompts
- Ranking AI vendors
- Requiring a specific IDE/language/cloud
- 20 Capabilities because 20 roles exist
- 20 rigid agents because 20 roles exist
- Claiming future phases are done

---

## Change Policy

Roadmap changes should record what shifted, why, and which principles remain intact.
