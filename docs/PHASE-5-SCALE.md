# Phase 5 Scale Notes

Conceptual + measured notes for Codebase Intelligence indexing.

| Scale | Status | Notes |
|---|---|---|
| ~10 files | **Proven** | Unit tests + mini fixtures |
| ~100 files | **Proven** | `codebase/` package self-analysis in integration tests |
| ~1,000 files | **Plausible** | Linear walk + per-file parse; no hard blocker observed |
| ~10,000 files | **Unproven** | Likely OK with ignore rules; memory not measured |
| ~100,000 files | **Unproven** | Needs streaming/incremental strategy; not claimed |

## Measured (small)

Analysis metrics include `duration_seconds`, `files_processed`, `error_count`, `approx_max_rss_mb` on each snapshot.

On mini fixtures, duration is typically well under 1s on developer hardware.

## What is not claimed

- Sub-second analysis at 100k files
- Perfect incremental rebuilds
- Distributed indexing

Incremental snapshot diff exists for structural comparison after two analyses; it is not an optimized watcher.
