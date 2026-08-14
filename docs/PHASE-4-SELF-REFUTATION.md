# Phase 4 Self-Refutation

Attack the Planning Orchestrator design. Fix real defects before closing.

| # | Attack | Verdict |
|---|---|---|
| 1 | Orchestrator too coupled? | **Held** — thin facade; logic in modules; anti-god-object test |
| 2 | Add Capability without core edits? | **Mostly held** — catalog markdown discovery + templates.json/bindings.json; optional affinity boost only |
| 3 | Add Role without orchestrator edits? | **Held** — `role/bindings.json` |
| 4 | Add Knowledge Unit without code? | **Held** — Capability `fulfilled_by` / `primary_fulfillment` bindings |
| 5–7 | 100 / 1k / 10k Capabilities | **Plausible** via filesystem catalog; unscored scale risk deferred (no DB index yet) |
| 8 | Multiple intents | **Held** — multi candidates + arbitration notes |
| 9 | Ambiguous intents | **Held** — clarifying questions / uncertainties |
| 10 | Missing Capability | **Held** — gaps + no invented IDs |
| 11 | Task failure | **Modeled** — classify_failure + replan revision bump |
| 12 | Decision change | **Modeled** — change impact walks artifact deps |
| 13 | Human approval days | **Held** — blocked/partially_ready; parallel software work may continue |
| 14 | Agent disappears | **N/A runtime** — boundary only; assignment hints |
| 15 | Evidence contradicts claim | **Held** — claim ≠ evidence rule |
| 16 | Irreversible action | **Partial** — decisions carry reversibility; no execution runtime yet |
| 17 | Role overlap | **Held** — multiple roles allowed; not Capabilities |
| 18 | Competing Capabilities | **Held** — arbitration marks + audit vs build preference |
| 19 | Cross-domain project | **Held** — padel scenario |
| 20 | Regulated professional work | **Held** — human escalations / professional gates |

## Defects fixed during Phase 4

| Defect | Fix |
|---|---|
| Artifact deps failed when Capability order ≠ architecture-first | Two-pass plan generation |
| Build SaaS selected test-planning as primary | Arbitration prefers architecture for build/design |
| “Audita este sistema” falsely marked build via “sistema” | Removed broad system/sistema build signals; audit prefers security |
| CLI used wrong repo root | Default `--repo-root` to repository root |

No Phase 3 rollback required.
