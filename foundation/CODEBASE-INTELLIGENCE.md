# Codebase Intelligence Model

Defines how Engineering OS observes and represents a software repository as **structured evidence**.

This document supersedes the Phase 3 boundary stub for meaning. Runtime lives in `codebase/` (Phase 5). Orchestration consumes snapshots; it does not own indexing.

**Codebase Intelligence ≠ Capability.**  
**Codebase Intelligence ≠ Orchestrator.**  
**Observation ≠ Interpretation ≠ Decision.**

Authorities: [EVIDENCE-MODEL](EVIDENCE-MODEL.md), [CHANGE-IMPACT-MODEL](CHANGE-IMPACT-MODEL.md), [ORCHESTRATOR-MODEL](ORCHESTRATOR-MODEL.md), [ADAPTER-MODEL](ADAPTER-MODEL.md)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Analyze/refactor/migrate/audit intents need verifiable repo understanding. |
| Problem avoided | Inventing architecture from filenames or chat folklore. |
| If absent | Plans stay abstract; readiness cannot demand codebase evidence. |
| Why not a Capability? | It is infrastructure for evidence, not an intent class offered to users. |
| Why not Orchestrator? | Indexing/observation must stay swappable and vendor-neutral. |

---

## Epistemic Levels (mandatory)

| Level | Meaning | Allowed language |
|---|---|---|
| **Observation** | Directly measured from files/Git/parsers | “Exists”, “contains”, “imports” |
| **Interpretation** | Provisional reading of observations | “Appears to”, “inferred”, “signal” |
| **Decision** | Planning/execution choice (owned elsewhere) | Recorded as Decision / Task / Gate |

Findings may mix observation + interpretation but must label confidence (`observed` \| `inferred` \| `unknown`).

Never promote interpretation to fact without evidence.

---

## Core Concepts

For each concept: problem solved, problem avoided, contents, consumers, if absent.

### Repository

| | |
|---|---|
| **Solves** | Name the durable workspace under analysis (path + VCS identity). |
| **Avoids** | Treating “folder on disk” as identical to a Git revision. |
| **Contains** | Root path, optional remotes, ignore rules, access boundary. |
| **Consumers** | Snapshot builder, CLI, Orchestrator tasks. |
| **If absent** | No stable target for analysis. |

### Codebase

| | |
|---|---|
| **Solves** | Name the software system(s) inside a repository (may be monorepo). |
| **Avoids** | Assuming one package ≡ one repository. |
| **Contains** | Logical product/package set discovered under a repo. |
| **Consumers** | Architecture signals, impact analysis. |
| **If absent** | Monorepos collapse incorrectly into a single blob. |

### File

| | |
|---|---|
| **Solves** | Atomic on-disk unit with path, size, hash, kind. |
| **Avoids** | Treating every file as source code. |
| **Contains** | Path, extension, size, content hash, binary?, ignored?, generated?, sensitive?. |
| **Consumers** | Index, parsers, security signals. |
| **If absent** | No reproducible inventory. |

**file ≠ module.** A file may host zero/many modules; a module may span files.

### Directory

| | |
|---|---|
| **Solves** | Structural grouping and package roots. |
| **Avoids** | Flattening trees and losing layout conventions. |
| **Contains** | Path, children counts, role hints (observed/inferred). |
| **Consumers** | FS index, architecture signals. |
| **If absent** | Layer/package heuristics fail. |

### Symbol

| | |
|---|---|
| **Solves** | Addressable code entity (function/class/type/…). |
| **Avoids** | Line-only references without identity. |
| **Contains** | Id, kind, name, file, span, exports?, evidence. |
| **Consumers** | Dependency edges, impact, findings. |
| **If absent** | Change impact stays file-granular only. |

### Module

| | |
|---|---|
| **Solves** | Logical compilation/import unit (language-specific). |
| **Avoids** | Equating path segments with modules blindly. |
| **Contains** | Module id, files, language, entry?, evidence. |
| **Consumers** | Dependency graph, architecture signals. |
| **If absent** | Graphs become path spaghetti. |

### Dependency

| | |
|---|---|
| **Solves** | Declared or observed coupling edge (import/package/runtime-inferred). |
| **Avoids** | Treating every textual mention as a hard dependency. |
| **Contains** | From, to, kind (`import`\|`package`\|`inferred_runtime`), certainty. |
| **Consumers** | Graphs, impact, findings. |
| **If absent** | No fan-out analysis. |

**dependency ≠ reference.** A reference may be documentation/comment; a dependency participates in build/runtime coupling with stated certainty.

### Reference

| | |
|---|---|
| **Solves** | Soft/link mention without proven coupling. |
| **Avoids** | Inflating dependency graphs. |
| **Contains** | Source location, target hint, kind. |
| **Consumers** | Optional enrichment. |
| **If absent** | Acceptable; deps remain primary. |

### Entry Point

| | |
|---|---|
| **Solves** | Identify executables/apps/CLIs/servers. |
| **Avoids** | Treating all modules as equal roots. |
| **Contains** | Path/symbol, kind, evidence, certainty. |
| **Consumers** | Impact, architecture. |
| **If absent** | Harder to prioritize blast radius. |

### Configuration

| | |
|---|---|
| **Solves** | Capture manifests/tooling/env templates/CI/infra files. |
| **Avoids** | Mixing detected files with guessed settings. |
| **Contains** | Path, type, detected vs inferred fields. |
| **Consumers** | Security/config intelligence, planning. |
| **If absent** | Auth/build/runtime assumptions go blind. |

### Test

| | |
|---|---|
| **Solves** | Locate tests and approximate code links. |
| **Avoids** | Inventing coverage percentages. |
| **Contains** | Path, framework?, linked targets?, coverage=`unknown` unless measured. |
| **Consumers** | Impact, quality planning. |
| **If absent** | Refactor readiness understates risk. |

### External Dependency

| | |
|---|---|
| **Solves** | Package/ecosystem dependencies outside the repo. |
| **Avoids** | Confusing internal modules with npm/PyPI crates. |
| **Contains** | Name, ecosystem, version constraint if present, evidence. |
| **Consumers** | Security/performance signals. |
| **If absent** | Supply-chain gaps invisible. |

### Runtime Boundary

| | |
|---|---|
| **Solves** | Separate static structure from runtime behavior. |
| **Avoids** | Claiming live performance/auth behavior from AST alone. |
| **Contains** | Declared process/service boundaries when observed; else `unknown`. |
| **Consumers** | Findings language, escalation. |
| **If absent** | Static analysis overclaims production truth. |

### Evidence

| | |
|---|---|
| **Solves** | Anchor claims to path/line/symbol/commit/config/edge/command. |
| **Avoids** | Orphan conclusions. |
| **Contains** | Pointers + epistemic level. |
| **Consumers** | Findings, Orchestrator, humans. |
| **If absent** | Agency invents. |

Uses [EVIDENCE-MODEL](EVIDENCE-MODEL.md); Codebase Intelligence produces evidence records, not Knowledge Units.

### Finding

| | |
|---|---|
| **Solves** | Structured suspicion/issue with severity + confidence. |
| **Avoids** | Turning hunches into decisions. |
| **Contains** | Id, kind, severity, confidence, evidence, location, impact potential, status. |
| **Consumers** | Reports, gates, humans. |
| **If absent** | Analysis has no actionable outputs. |

**finding ≠ decision.** Decisions belong to Decision/Execution layers.

### Codebase Snapshot

| | |
|---|---|
| **Solves** | Immutable, comparable result of one analysis run. |
| **Avoids** | Mutating “live views” without provenance. |
| **Contains** | Timestamp, git revision, included/excluded files, parser set, indexes, findings, errors, metrics. |
| **Consumers** | Orchestrator, CLI, incremental diff. |
| **If absent** | No reproducibility. |

**repository ≠ codebase snapshot.** Repo is the subject; snapshot is a dated observation.

**source code ≠ runtime behavior.** Snapshots are static unless a measured runtime artifact is attached as evidence.

---

## Placement in the Agency Loop

```text
Intent
  → Capability / Role / Knowledge
  → Execution Plan
       ↳ Task: codebase_analysis   ← Codebase Intelligence produces Snapshot + Evidence
  → Artifacts (analysis report / JSON)
  → Dependencies / Gates / Readiness
  → Decisions (separate)
```

Orchestrator may require `codebase_analysis` before implementation/refactor tasks when repo context is missing.

---

## Non-Goals (Phase 5)

- LLM-mandatory understanding
- Full polyglot semantic perfection
- Autonomous code mutation
- CI/CD / deploy
- Agent fleets
- Cursor-specific indexing
- Claiming runtime performance without runtime evidence

---

## Extensibility

Parsers implement a narrow interface. Adding a language must not require editing Orchestrator or inventing Capabilities.
