# Phase 8.1 — Skill Source Ingestion

## Problem

Phase 8 registered SkillPacks, but external methodology sources were missing. Without a Source layer, activation would either invent content or stay permanently opaque.

## Architecture

```text
SOURCE (hashed, versioned)
  → Extraction (bounded knowledge slices)
  → SkillPack (eos.skillpack.*)
  → Invocation evidence
  → Agent bounded context
```

```text
SOURCE ≠ SKILLPACK ≠ KNOWLEDGE UNIT ≠ EVIDENCE
```

Pipeline:

```text
discover → verify → ingest → normalize → provenance → validate → activate
```

Any stage can stop. Invalid sources never become `active`.

## Key modules

| Module | Role |
|---|---|
| `skillpacks/sources/model.py` | SkillSource |
| `skillpacks/sources/registry.py` | Data-driven multi-source registry |
| `skillpacks/sources/pipeline.py` | Ingestion stages + evidence |
| `skillpacks/sources/revision.py` | Immutable revisions |
| `skillpacks/sources/extraction.py` | Raw → extracted knowledge |
| `skillpacks/sources/activation.py` | `CAN_ACTIVATE_SKILL` |
| `skillpacks/sources/status.py` | SkillPack status transitions |
| `skillpacks/sources/staleness.py` | Hash mismatch → stale |
| `skillpacks/invocation.py` | Bounded context + invocation evidence |

## Activation honesty

| Pack | Status |
|---|---|
| Marketing / Stop Slop / UI UX PRO MAX | `unavailable` + `NEEDS_SOURCE` |
| Context Engineering | `active` (EOS-native source hashed) |

## Security

Sources are untrusted by default. Extraction rejects privilege/injection markers. Skills still cannot grant tools or deploy rights.

## Limitations

- External methodology corpora not present in repo
- UX skeleton is structural only while UI UX source missing
- Scale to thousands of sources not measured (see validation doc)

**Do not start Phase 9 from this document.**
