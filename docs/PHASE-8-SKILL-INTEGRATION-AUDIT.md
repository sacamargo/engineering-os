# Phase 8 — Skill Integration Architecture Audit

**Status:** Audit only. No implementation in this document’s commit.  
**Date context:** After Phase 7 Delivery closeout (`main` tip at audit start).  
**Rule:** Do not weaken Capability / Role / Agent / Knowledge / Delivery boundaries to accommodate Skills.

---

## 1. Current architecture (as implemented)

```text
Intent
  → Orchestration (intent intake, capability resolution, roles, knowledge, plan)
  → Codebase Intelligence (evidence when analyze intents require it)
  → Agents (execute tasks with tools, ChangeSet, evidence, gates)
  → Delivery (build / validate / artifact / release readiness; no real deploy)
```

| Layer | Home | Role |
|---|---|---|
| Foundation / kernel | `foundation/` | Models, principles, boundaries |
| Capabilities | `capabilities/` | Intent-class offers (demand side) |
| Knowledge units | `playbooks/`, `frameworks/`, `skills/`, … | Fulfillment methods (`type: skill` = AI-operable **procedure**) |
| Contracts | `contracts/` | Knowledge + execution + codebase + delivery validators |
| Orchestration | `orchestration/` | Planning facade; thin modules; no vendor CI |
| Codebase Intelligence | `codebase/` | Observation → snapshot evidence (not a Capability) |
| Agents | `agents/` | Executors; sandbox; permissions; context builder (partial) |
| Delivery | `delivery/` | ReleaseCandidate readiness; deployment adapter boundary |
| Cursor adaptation | `.cursor/skills/engineering-os-agency/`, `adaptations/cursor/` | Thin entry; must not fork canonical knowledge |

Hard invariants already encoded:

```text
Capability ≠ Role ≠ Agent ≠ Knowledge Unit ≠ Tool ≠ Artifact ≠ Evidence
Delivery ≠ Deployment
Codebase Intelligence ≠ Capability
claim ≠ evidence
```

---

## 2. Existing Skill-related concepts (must not be collapsed)

### 2.1 Knowledge Unit `type: skill`

- Location: `skills/**/*.md` (today: `skills/agency/capability-routing.md`)
- ID pattern: `eos.skill.<domain>.<name>`
- Meaning: portable **procedure** (inputs / steps / outputs / limits)
- Validated by: `contracts/validate.py` + `unit.schema.json`
- Documented in: `foundation/KNOWLEDGE-ARCHITECTURE.md` (“Skills vs Prompts”)
- Explicit rejection in Capability Model: **Skills must not be the primary entry point**

### 2.2 Cursor project skill

- `.cursor/skills/engineering-os-agency/SKILL.md` + adaptation unit
- Meaning: **tool packaging / entrypoint**, not a catalog Capability and not an Agent
- Must continue to call into Capabilities/units by ID

### 2.3 Portable Skills principle (P14)

- Skills encode reusable methodology, not vendor prompt tricks
- Does **not** define Phase 8 integration contracts

### 2.4 Agent context builder

- `agents/context.py` already rejects “dump entire repo”
- Incomplete relative to Phase 8 Context Engineering goals (no skill metadata, provenance, invalidation, decision freshness)

### 2.5 What does **not** exist yet

| Gap | Notes |
|---|---|
| First-class Integrated Skill model | Distinct from knowledge unit `skill` |
| Skill registry / discovery | Data-driven; Orchestrator must not hardcode packs |
| Skill routing after Capability resolution | Intent → Capability → **Skill candidates** → Roles → … |
| Controlled Skill composition | primary / supporting / transversal without hidden DAG |
| Skill↔Capability / Skill↔Role bindings | Associations, not identity |
| Skill evidence / gates / failures | Reuse Evidence/Gate/Failure models; extend fields |
| Skill security (deny privilege escalation) | Skill instructions must not grant tools/deploy |
| Source packs for external Skills | **No Marketing / Stop Slop / UI UX PRO MAX / Context Engineering source trees in this repository** |

---

## 3. Naming collision — architectural decision (required)

**Problem:** The word “Skill” already means knowledge-unit procedure (`eos.skill.*`).  
Phase 8 needs a **first-class integration object** that is:

```text
Capability ≠ Skill ≠ Role ≠ Agent ≠ Knowledge ≠ Tool ≠ Artifact ≠ Evidence
```

If Phase 8 reuses `type: skill` knowledge units for Marketing / Stop Slop / etc., the system collapses Skill into Knowledge and cannot enforce Skill-specific routing, composition, provenance, and security.

### Decision (for Phase 8 implementation)

| Concept | Name in docs | ID namespace | Package / path |
|---|---|---|---|
| Knowledge procedure | Knowledge Unit (`type: skill`) | `eos.skill.*` | `skills/` (unchanged) |
| Integrated expertise pack | **Skill** (Phase 8 Skill Model) | `eos.skillpack.*` | **`skillpacks/`** + `contracts/skills/` |

Rationale:

- Preserves existing contracts and catalog validation
- Avoids a giant `skills.py` god module
- Allows `skills/` to remain knowledge userland
- Makes Orchestrator discover packs via registry data, not hardcoded lists
- ID prefix `skillpack` is explicit and searchable; human docs still say “Skill”

**Rejected:** Overloading knowledge `type: skill` for external packs.  
**Rejected:** Renaming all existing knowledge skills in Phase 8 (unnecessary churn).  
**Rejected:** Putting pack definitions under `skills/` without a separate validator (would break unit validation or silently skip files).

---

## 4. Where Skills integrate (boundary map)

```text
Intent
  → Capability resolution          (unchanged primary router)
  → Skill candidate resolution     (NEW — registry-driven)
  → Role resolution                (may prefer roles compatible with selected Skills)
  → Knowledge resolution           (knowledge units still fulfill Capabilities)
  → Plan generation                (tasks may reference skillpack IDs)
  → Agent assignment               (Agent uses Skills; Skill ≠ Agent)
  → Context assembly               (Context Engineering skillpack / module)
  → Evidence + Gates               (skill evidence fields; skill gates)
  → Delivery                       (unchanged; Skills must not grant deploy)
```

| Integration point | Do | Do not |
|---|---|---|
| `orchestration/` | Add thin `skill` module + facade field; load registry from disk | Hardcode the four packs in facade |
| `skillpacks/` | Registry, pack manifests, routing signals, composition rules | Embed Orchestrator logic |
| `contracts/skills/` | Schemas + `validate_skills.py` | Duplicate knowledge unit schema |
| `agents/` | Record skill_id/version/provenance on evidence; consume assembled context | Let Skill definitions mutate permissions |
| `delivery/` | No Skill-based privilege escalation | Treat Skill pass as release success |
| `codebase/` | Context Engineering may select **relevant** evidence | Auto-run analysis on quotation/assessment intents |
| Knowledge `skills/` | Leave agency routing skill intact | Convert packs into knowledge units blindly |

---

## 5. What must remain unchanged

1. Capability as primary intent-class navigation surface  
2. Role ≠ Agent ≠ Capability  
3. Deny-by-default tools / delivery / deploy boundaries  
4. Knowledge unit contracts and ID grammar for `eos.skill.*`  
5. Delivery ≠ Deployment; no auto production approval  
6. Codebase Intelligence invoked only when intent/context warrants it  
7. Evidence required for claims; Skill authority ≠ evidence  
8. Vendor neutrality of core (no Claude-/GitHub-specific Skill runtime APIs)

---

## 6. New contracts required

Under `contracts/skills/` (names illustrative):

| Contract | Purpose |
|---|---|
| Skillpack manifest schema | Required fields, status, provenance, version |
| Registry schema | Discovery index; unique IDs; availability |
| Binding schema | Skill↔Capability, Skill↔Role associations |
| Composition schema | primary / supporting / transversal; no hidden DAG |
| Selection record schema | confidence, trigger evidence, negative evidence, conflicts |
| Skill evidence extension | skill_id, version, provenance, inputs/outputs, uncertainty |
| Failure codes | `SKILL_*` taxonomy integrated with Failure Model |

Validation must reject: unknown capability/role/tool refs, missing provenance, duplicate IDs, circular composition where prohibited, privilege-granting fields, fabricated licenses.

---

## 7. The four nominated Skills — source reality

| Skill | Repo source found? | Phase 8 honest status at integration |
|---|---|---|
| Marketing Skills / Corey Haines | **No** | Manifest + provenance; `status: unavailable` until source is added |
| Stop Slop | **No** | Same; define **boundaries** (what it is not) without inventing methodology body |
| UI UX PRO MAX | **No** | Same; modes DESIGN / REVIEW / IMPROVEMENT as **contract slots** only if declared without fabricated method content |
| Context Engineering | **No Claude/vendor pack in repo** | Implement **Engineering OS–native** context assembly adapted for Cursor/EOS (vendor-neutral), with provenance = EOS adaptation — **not** a copy of a Claude runtime |

Rule: **Do not invent missing source content.** Unavailable skills remain selectable as candidates but must fail closed (`SKILL_UNAVAILABLE` / `SKILL_SOURCE_MISSING`) rather than silently fabricating guidance.

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| Skill becomes hidden Capability | Capabilities remain sole intent-class router; Skills are candidates **after** |
| Skill becomes god-object | Split registry / router / composition / security; no monolith `skills.py` |
| Skill grants permissions | Schema forbids permission elevation; attack tests |
| Keyword-only routing | Structured signals + negative evidence (e.g. payment gateway ≠ physical gate) |
| All projects select all Skills | Scoring + applicability; Marketing not forced on pure engineering intents |
| Context dump | Bound context assembly; relevance + max budget; provenance |
| Stop Slop as universal truth | Explicit: review findings ≠ product correctness; cannot replace domain review |
| UI UX pack becomes frontend coding | Modes + permissions; no code mutation without Agent tool rights |
| Marketing becomes PM / architecture | Limits field; cannot own architecture/deploy decisions |
| Quotation treated as codebase | Assessment scenario must not call Codebase Intelligence |
| Roadmap collision | Current roadmap labels Phase 8 as “Production Operations”; Phase 8 Skill Integration **resequences** roadmap in a later docs task |

---

## 9. Rejected designs

1. **Hardcoding four Skills in Orchestrator** — violates extensibility (Skill #5/#100).  
2. **One giant `skills.py`** — god-object; rejected.  
3. **Skill = Role** or **Skill = Capability** — collapses architecture.  
4. **Skill = Agent** — Agent executes; Skill defines method/expertise.  
5. **Copying external material blindly** — provenance/license/adaptation required.  
6. **Fabricating missing methodology** — unavailable, not invented.  
7. **Claude-specific Context Engineering APIs** — vendor lock-in; forbidden in core.  
8. **Skill composition as hidden task DAG** — composition ≠ task dependency.  
9. **Silent fallback when Skill unavailable** — must surface failure / NEEDS_INPUT.  
10. **Overloading knowledge `type: skill`** — see §3.

---

## 10. Architectural boundary (summary)

```text
Capability     — WHAT intent class the system offers
Skill (pack)   — HOW specialized expertise/method is applied (data-driven)
Role           — WHO specialization/authority is required
Agent          — runtime EXECUTOR
Knowledge unit — catalog METHOD modules (including type:skill procedures)
Tool           — WHAT the Agent is allowed to invoke
Artifact       — inspectable work product
Evidence       — inspectable justification for claims
```

Phase 8 success is **not** “four prompts landed.”  
Success is a **contract-driven Skill layer** that discovers, selects, composes, invokes, validates, and audits packs without collapsing those boundaries.

---

## 11. Implementation order (aligned to Phase 8 task list)

1. Skill model + `foundation/SKILL-MODEL.md`  
2. Contracts + validator  
3. Registry + discovery  
4. Routing module (Orchestrator thin wiring)  
5. Composition  
6–9. Four pack manifests (honest availability)  
10–20. Bindings, agent boundary, gates, evidence, failure, escalation, versioning, provenance, security, conflicts  
21–27. Scenarios + scalability fixture  
28–30. Docs, self-refutation, final validation  

**Stop after Phase 8.** Do not start Production Operations / Phase 9 until this phase is critically reviewed.
