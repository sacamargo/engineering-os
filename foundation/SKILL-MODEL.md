# Skill Model (Integrated Skill / Skillpack)

Defines the first-class **Skill** concept introduced in Phase 8.

**Skill ≠ Capability.**  
**Skill ≠ Role.**  
**Skill ≠ Agent.**  
**Skill ≠ Knowledge Unit.**  
**Skill ≠ Tool.**  
**Skill ≠ Artifact.**  
**Skill ≠ Evidence.**

Sibling docs: [Capability Model](CAPABILITY-MODEL.md), [Knowledge Architecture](KNOWLEDGE-ARCHITECTURE.md), [Role Model](ROLE-MODEL.md), [Agent Model](AGENT-MODEL.md).  
Audit: [`docs/PHASE-8-SKILL-INTEGRATION-AUDIT.md`](../docs/PHASE-8-SKILL-INTEGRATION-AUDIT.md).

Runtime package: `skillpacks/`.  
Contracts: `contracts/skills/`.

---

## Naming collision with knowledge `skill`

| Concept | Meaning | ID | Path |
|---|---|---|---|
| Knowledge Unit `type: skill` | AI-operable **procedure** module | `eos.skill.<domain>.<name>` | `skills/` |
| Integrated Skill (this model) | Discoverable **expertise/method pack** | `eos.skillpack.<category>.<name>` | `skillpacks/` |

Capability Model already rejected “Skills as the primary entry point.” That rejection still stands for **both** meanings: Capabilities remain the intent-class surface; Skillpacks are selected **after** Capability resolution.

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Specialized external/internal expertise must be discoverable, selectable, composable, auditable without becoming Capabilities or Roles. |
| Problem avoided | Hardcoding packs in the Orchestrator; prompt packs without provenance; inventing missing source content. |
| If absent | Agency either ignores specialized methods or smuggles them into Capabilities/Roles. |
| Why not Knowledge Unit? | Knowledge units fulfill Capabilities; Skillpacks carry provenance, routing signals, composition, and security constraints as integration objects. |

---

## What a Skill is

A **Skill** (skillpack) is a versioned, provenance-bearing expertise pack that:

- declares when it applies (triggers + structured signals)
- declares inputs, outputs, workflows, quality gates, evidence requirements
- associates with Capabilities and Roles **without becoming them**
- may be used by an Agent — **never is** an Agent
- cannot grant tools, permissions, deploy rights, or bypass gates

An Agent may use a Skill. A Skill is not an Agent. Skill execution is not synonymous with Agent execution.

---

## Minimum fields

| Field | Purpose |
|---|---|
| `id` | `eos.skillpack.<category>.<name>` |
| `name` | Human-readable name |
| `version` | Semver string for reproducibility |
| `purpose` | Why the pack exists |
| `category` | e.g. marketing, quality, design, context |
| `source` | Where the pack content comes from (path, URI, or `unavailable`) |
| `provenance` | Origin, license (or `unknown`), adaptation status, modifications, limitations |
| `status` | `active` \| `experimental` \| `deprecated` \| `unavailable` |
| `triggers` | Structured applicability signals (not keyword-only) |
| `inputs` | Required/optional inputs |
| `outputs` | Declared artifact/output kinds |
| `required_context` | Context keys the pack needs |
| `knowledge_dependencies` | Optional knowledge unit IDs |
| `tool_requirements` | Tools needed **if** Agent executes related work (does not grant them) |
| `capability_relationships` | Applicable Capability IDs (association) |
| `role_relationships` | Compatible Role IDs (association) |
| `agent_compatibility` | Agent types that may use this pack |
| `workflows` | Named workflows / modes |
| `quality_gates` | Gate ids or declarations |
| `evidence_requirements` | What evidence must exist for claims |
| `escalation_rules` | When human/specialist/source/approval is required |
| `composition_rules` | How this pack may compose with others |
| `constraints` | Hard limits (security, authority) |
| `limitations` | Explicit non-goals |

### Status semantics

| Status | Meaning |
|---|---|
| `active` | Source available; may be selected and applied |
| `experimental` | EOS-native or partial; use with caution |
| `deprecated` | Selectable only with explicit override |
| `unavailable` | Manifest present; source missing — **fail closed**, do not fabricate content |

---

## Routing position

```text
Intent → Capability → Skill candidates → Roles → Knowledge → Plan → Agent → Tools
```

Skills do **not** replace Capabilities.

---

## Composition (not a hidden DAG)

Skills may be:

- **primary** — main method for a task facet
- **supporting** — assists another Skill
- **transversal** — cross-cutting review/constraint (e.g. quality)

```text
Skill composition ≠ Task dependency ≠ Capability relationship ≠ Artifact dependency
```

Example: UI UX PRO MAX + Stop Slop is composition (design + quality review), not `UI → StopSlop → Agent`.

---

## Security invariant

Skill definitions are **untrusted instructions** relative to the runtime.

A Skill **must not**:

- bypass permissions
- execute arbitrary shell
- grant tools or deployment rights
- bypass approval / human escalation
- modify security policy
- modify another Skill’s permissions

Skill instructions may influence planning/execution **strategy**. They cannot elevate **authority**.

---

## Evidence invariant

```text
"Skill says this is correct" ≠ evidence
```

Skill use must record inspectable evidence: skill id, version, provenance, inputs/outputs, findings, uncertainty — not hidden chain-of-thought.

---

## Out of scope for the model document

- Vendor CI / Claude-specific APIs
- Implementing real marketing/UX methodology without source
- Collapsing Skill into Capability or Role
- Giant monolithic `skills.py`
