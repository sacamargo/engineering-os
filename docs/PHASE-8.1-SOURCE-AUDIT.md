# Phase 8.1 — Skill Source Ingestion Audit

**Status:** Audit only (no implementation in this commit).  
**Base:** `main` @ `15d47bb` (Phase 8 Skill Integration complete).  
**Rule:** Do not invent Skills or methodology. Do not start Phase 9.

---

## 1. What exists (reuse)

| Area | Location | Notes |
|---|---|---|
| SkillPack model | `skillpacks/model.py`, `foundation/SKILL-MODEL.md` | `eos.skillpack.*`; status; provenance object |
| Registry | `skillpacks/registry.json`, `registry.py` | Data-driven discovery |
| Routing / composition | `routing.py`, `composition.py` | Post-Capability; not Orchestrator-hardcoded |
| Bindings | `bindings/` | Skill↔Capability, Skill↔Role |
| Runtime | evidence, gates, failures, security, conflicts, agent_bridge | Claim ≠ evidence; no privilege elevation |
| Context Engineering | `context_engineering.py` + pack | EOS-native `experimental` |
| Contracts | `contracts/skills/`, `validate_skills.py` | Manifest validation |
| Docs | `docs/PHASE-8-*.md` | Phase 8 closeout |

### Current pack inventory

| SkillPack | Status | Source reality |
|---|---|---|
| `eos.skillpack.marketing.corey-haines` | `unavailable` | No methodology body in repo |
| `eos.skillpack.quality.stop-slop` | `unavailable` | No methodology body in repo |
| `eos.skillpack.design.ui-ux-pro-max` | `unavailable` | No methodology body in repo |
| `eos.skillpack.context.engineering` | `experimental` | EOS-native code + manifest |
| `eos.skillpack.quality.fixture-review` | `experimental` | Test fixture only |

### Status semantics (SkillPack today)

| Status | Meaning (Phase 8) |
|---|---|
| `unavailable` | Manifest present; source missing; **not selectable**; fail closed / `NEEDS_SOURCE` |
| `experimental` | Selectable with caution; EOS-native or partial |
| `active` | Source available; may be selected and applied |
| `deprecated` | Selectable only with explicit override (declared; little runtime use yet) |

### Provenance today

`SkillProvenance` fields: `origin`, `source`, `version`, `license`, `adaptation_status`, `modifications`, `limitations`, `unavailable_source_content`.

**Gap:** Provenance is **pack-level metadata**, not a first-class **Source** object with hash, revisions, ingestion pipeline, or Source→Extraction→SkillPack chain.

---

## 2. What is missing (Phase 8.1)

| Gap | Planned home |
|---|---|
| Source Model (distinct from SkillPack) | `skillpacks/sources/` + contracts |
| Source registry (multi-source per Skill) | `skillpacks/sources/registry.json` |
| Ingestion pipeline stages + evidence | `skillpacks/sources/pipeline.py` |
| Content hash + immutable revisions | `skillpacks/sources/hashing.py`, `revision.py` |
| Extraction boundary (raw → knowledge → pack) | `skillpacks/sources/extraction.py` |
| Provenance chain to invocation | extend evidence / agent_bridge |
| `CAN_ACTIVATE_SKILL` gate | `skillpacks/activation.py` |
| Formal SkillPack status transitions tied to sources | `skillpacks/status.py` |
| Source priority / staleness | `skillpacks/sources/priority.py`, `staleness.py` |
| Bounded skill context for agents | extend `agent_bridge.py` |
| Electrolinera + role discovery upgrades | `examples/agency/`, scenarios |

---

## 3. What must not be touched / weakened

1. Capability as primary intent router  
2. Skill ≠ Role ≠ Agent ≠ Knowledge Unit (`eos.skill.*`)  
3. Deny-by-default: Skills cannot grant tools/deploy/approvals  
4. Orchestrator must not hardcode Skill or Source lists  
5. Delivery / Agents / Codebase packages’ core contracts (extend via bridges only)  
6. Phase 9 Production Operations — **do not start**

---

## 4. Source availability finding (pre-implementation)

Workspace / Cursor skills search for real **UI UX PRO MAX**, **Stop Slop**, and **Marketing / Corey Haines** methodology corpora: **not found** as ingestible source trees inside this repository or standard Cursor skill packs.

Therefore Phase 8.1 **must**:

- Keep Marketing / Stop Slop / UI UX PRO MAX as **`unavailable`** unless a real source is later placed under `skillpacks/sources/` (or explicitly provided)
- Emit / preserve **`NEEDS_SOURCE`**
- **Not** fabricate methodology content
- Allow Context Engineering to pursue controlled `experimental` → `active` only via activation gate against its EOS-native source (code + manifest), not by inventing external content

---

## 5. Distinctions Phase 8.1 must keep hard

```text
SOURCE          — external/internal methodology material (hashed, versioned)
SKILLPACK       — integrated skill definition (eos.skillpack.*)
KNOWLEDGE UNIT  — catalog type:skill / playbook / … (eos.skill.* etc.)
EVIDENCE        — inspectable justification for claims
EXTRACTION      — derived knowledge slices with source refs
INVOCATION      — use of a SkillPack by an Agent (evidence-bearing)
```

```text
unavailable ≠ experimental ≠ active
Source.status ≠ SkillPack.status (related, not identical)
Activation requires verified source evidence — never silent
```

---

## 6. Rejected approaches

- Inventing “UI UX PRO MAX” / “Stop Slop” / Marketing bodies  
- Parallel Skill system replacing `skillpacks/`  
- Hardcoding sources in Orchestrator  
- Dumping full sources into agent context  
- Treating unavailable as active  
- Auto-approving human gates via Skills  

---

## 7. Implementation order

1. Source model + contracts + registry  
2. Pipeline (hash, revision, extract, provenance, activate)  
3. Status transitions + activation gate  
4. Pack-specific ingestion (honest unavailable vs Context Engineering)  
5. Conflicts / priority / staleness / bridge / routing polish  
6. Electrolinera / role discovery / UX contracts / tests / docs  

**Stop after Phase 8.1.** Do not begin Phase 9.
