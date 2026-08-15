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

## Phase 3 — Execution Model

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

Implement a minimal **Planning Orchestrator** that coordinates plans without becoming a god object.

- [x] Intent Intake
- [x] Capability Resolution + multi-capability arbitration
- [x] Role + Knowledge resolution
- [x] Plan generation with artifact-based dependencies
- [x] Readiness / gaps / escalation / gates evaluation
- [x] Evidence/decision/failure/replan/impact models (planning-time)
- [x] Codebase / Agent / Delivery / Adapter boundaries
- [x] Behavioral agency scenarios + anti-god-object guard
- [ ] Live Orchestrator engine that executes tasks against real repos (Phase 6+)
- [ ] Agent fleet runtime
- [ ] CI/CD delivery automation

**Exit criteria:** High-level intents produce valid Execution Plans with honest gaps and human stops — without pretending autonomous coding.

**Not a full autonomous coding agency yet.**

---

## Phase 5 — Codebase Intelligence (current complete)

Treat repositories as evidence sources for analyze/refactor/migrate/audit intents.

- [x] Conceptual model (observation ≠ interpretation ≠ decision)
- [x] Immutable Codebase Snapshot + reproducibility fingerprint
- [x] Filesystem index + read boundary
- [x] Extensible language parsers (Python + JS/TS lite)
- [x] Symbol index, dependency graph, tests, configuration
- [x] Architecture signals, findings, evidence, change impact
- [x] CLI + human report + machine JSON
- [x] Orchestrator `codebase_analysis` task + readiness gating
- [x] Rivallium / Padel IoT / legacy fixtures + agency scenarios
- [x] Security/performance static heuristics (epistemic labels)
- [x] Incremental snapshot diff + git provenance + metrics
- [x] Contracts/validators + Phase 5 validation docs

**Exit criteria:** A real repository can be analyzed into a structured snapshot that feeds Orchestration without inventing architecture or becoming a Capability.

**Non-goals:** agent fleets, autonomous mutation, CI/CD autonomy, mandatory LLM, full polyglot semantic perfection.

Evidence: [docs/PHASE-5-VALIDATION.md](../docs/PHASE-5-VALIDATION.md)

---

## Phase 6 — Agent Execution (current complete)

Flexible executors that run tasks using authorized tools, evidence, and gates.

- [x] Execution audit (reuse Task/Evidence/Gate/Failure; new agents runtime)
- [x] Agent Definition vs Runtime Instance
- [x] Agent lifecycle + task state integration
- [x] Tool model, permissions, risk
- [x] Sandboxed local tool runtime + allowlisted commands
- [x] Execution loop (assign→execute→evidence→gate→retry/replan/escalate)
- [x] ChangeSet, rollback, dry-run, cancellation
- [x] Deterministic coding agent (LLM optional boundary only)
- [x] Agency scenarios + security tests
- [x] Orchestrator assignment wiring (`execute_task` delegates to agents/)
- [x] Phase 6 validation docs

**Exit criteria:** A Task can be executed by an Agent with tools against a fixture repo, producing ChangeSet + test evidence + gate outcome — or fail/escalate honestly.

**Non-goals:** swarm, deploy, CI/CD autonomy, mandatory LLM, production ops.

Evidence: [docs/PHASE-6-VALIDATION.md](../docs/PHASE-6-VALIDATION.md)

---

## Phase 7 — Delivery / CI/CD (current complete)

Validate that Agent ChangeSets can pass controlled quality gates and become release-ready.

- [x] Delivery audit + model (Build, ValidationRun, Pipeline, Environment, ReleaseCandidate)
- [x] State machine + gates (NOT_RUN ≠ PASSED; no release without evidence)
- [x] Local delivery runtime + allowlisted executors + artifacts with digest
- [x] Security/risk integration + Codebase Intelligence signals
- [x] Deployment boundary (READY_FOR_DEPLOYMENT only; no real deploy)
- [x] Approvals, rollback model, CLI, contracts, agency scenarios
- [x] Self-refutation + validation docs

**Exit criteria:** ChangeSet → Build → Tests → Security → Artifact → Gates → ReleaseCandidate → Readiness, with honest NOT READY.

**Non-goals:** real cloud deploy, auto-prod approval, vendor CI inside core, swarm.

Evidence: [docs/PHASE-7-VALIDATION.md](../docs/PHASE-7-VALIDATION.md)

---

## Phase 8 — Skill Integration Layer (current complete)

Integrate specialized expertise packs without collapsing Skill into Capability/Role/Agent.

- [x] Skill Integration audit (`docs/PHASE-8-SKILL-INTEGRATION-AUDIT.md`)
- [x] Canonical Skill model (`eos.skillpack.*`) distinct from knowledge-unit `eos.skill.*`
- [x] Contracts + registry + discovery/routing + composition
- [x] Marketing / Stop Slop / UI UX PRO MAX (unavailable until source) + Context Engineering (EOS-native)
- [x] Capability/Role bindings, agent boundary, gates, evidence, failures, security, conflicts
- [x] Electrolinera + quotation assessment scenarios
- [x] Self-refutation + validation docs

**Exit criteria:** Skills are discoverable, selectable, composable, auditable — with honest unavailable handling and preserved architectural boundaries.

**Non-goals:** fabricating external methodology; Skill marketplace; Production Ops.

Evidence: [docs/PHASE-8-VALIDATION.md](../docs/PHASE-8-VALIDATION.md)

### Phase 8.1 — Skill Source Ingestion & Activation (current complete)

- [x] Source model, contracts, registry, ingestion pipeline
- [x] Hashing / revisions / extraction / CAN_ACTIVATE_SKILL / status transitions
- [x] Honest NEEDS_SOURCE for Marketing / Stop Slop / UI UX PRO MAX
- [x] Context Engineering activated via EOS-native verified source
- [x] Bounded agent skill context + invocation evidence
- [x] Electrolinera 8.1 + role discovery + UX skeleton contracts
- [x] Self-refutation + validation docs

Evidence: [docs/PHASE-8.1-VALIDATION.md](../docs/PHASE-8.1-VALIDATION.md)

---

## Phase 9 — Production Operations

Incident, reliability, and operational loops as first-class agency work.

Expected work:

- Incident investigation execution paths
- SLO/error-budget tied observability
- Change management under production constraints

**Not started.** Do not begin until Phase 8 review completes.

---

## Phase 10 — Continuous Evolution

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
