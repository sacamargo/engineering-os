# Phase 3 Self-Refutation

Attack the Execution Layer design. Record verdicts. Fix real defects before closing the phase.

---

## Problem 1 — Second Knowledge Architecture?

**Attack:** Execution docs could recreate playbooks/skills under new names.

**Verdict:** **Held.** Execution objects (Project/Task/Artifact/Plan/Gate) coordinate work; Knowledge Units remain methodology. Explicit non-goal language in EXECUTION-MODEL and contracts SPEC.

**Fix applied:** None required beyond existing boundaries.

---

## Problem 2 — Role became Capability?

**Attack:** ~20 roles tempt 20 Capabilities.

**Verdict:** **Held.** ROLE-MODEL + ROLE-CAPABILITY-BINDING + tests (`test_role_coverage`, fixtures) keep Role as specialization metadata. Rivallium/padel compose roles without inventing Capabilities.

---

## Problem 3 — Agent became Role?

**Attack:** Agent zoo mirrors roles.

**Verdict:** **Held (boundary).** AGENT-MODEL forbids one-agent-per-role; runtime not implemented (Phase 6).

---

## Problem 4 — Orchestrator god object?

**Attack:** Orchestrator absorbs knowledge.

**Verdict:** **Held (boundary).** ORCHESTRATOR-MODEL lists must-nots; no runtime in Phase 3.

---

## Problem 5 — Task duplicates Artifact?

**Attack:** Tasks store deliverables.

**Verdict:** **Held.** Tasks reference input/output artifact IDs; artifacts own result state.

---

## Problem 6 — Knowledge link vs execution dependency?

**Attack:** `related_capability` treated as scheduling.

**Verdict:** **Held.** DEPENDENCY-MODEL + plan `dependencies` kinds; Rivallium narrative distinguishes them.

---

## Problem 7 — Works with ~10 units?

**Verdict:** **Yes.** Live catalog (~14 units) + 4 Capabilities validates; fixtures use subset.

---

## Problem 8 — Works with 10,000?

**Verdict:** **Architecturally plausible, unproven.** ID namespacing + validators scale structurally; retrieval/indexing deferred (Phase 5). Risk accepted and deferred — not claimed solved.

---

## Problem 9 — Multi-capability?

**Verdict:** **Yes.** Rivallium + valid-multi-capability fixture + agency tests.

---

## Problem 10 — Detect missing Capabilities?

**Verdict:** **Yes.** `insufficient_coverage`, missing-capability tests, electrical certification scenario.

---

## Problem 11 — Stop for humans?

**Verdict:** **Yes (model).** HUMAN-ESCALATION + padel-iot professional gates; no autonomous electrical execution.

---

## Problem 12 — Recover from failure?

**Verdict:** **Modeled.** FAILURE-MODEL + REPLANNING-MODEL; runtime recovery not implemented.

---

## Problem 13 — Replan with traceability?

**Verdict:** **Modeled.** revision increments + supersede rules; runtime not implemented.

---

## Problem 14 — Vendor-neutral?

**Verdict:** **Held.** Core examples/contracts independent of Cursor; adapters optional.

---

## Defects found and fixed in this pass

| Issue | Fix |
|---|---|
| ROLE-MODEL still said Agent Model “boundary later” | Point to landed AGENT-MODEL |
| PROJECT-MODEL pointed to “detailed later” state machine | Link EXECUTION-STATE-MACHINE |

No architectural rollback required.
