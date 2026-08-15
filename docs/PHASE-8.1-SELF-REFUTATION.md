# Phase 8.1 Self-Refutation

| # | Attack | Result | Evidence | Mitigation | Residual risk |
|---|---|---|---|---|---|
| 1 | Inventing Skills | **Held** | External packs `unavailable`; NEEDS_SOURCE docs | No fabricated methodology | Temptation to fill slots later |
| 2 | Fake provenance | **Held** | Source contracts require origin/locator/hash for active | Validator + activation gate | Spoofed files if attacker writes repo |
| 3 | Privilege escalation via Skill | **Held** | Security + forbidden metadata | Deny-by-default | Social engineering of humans |
| 4 | Skills as prompts only | **Held** | Contract model + evidence | Structured packs | Thin packs if sources stay empty |
| 5 | God-skill | **Held** | Composition + Stop Slop limits | Transversal ≠ authority | Mis-routing |
| 6 | Skill=Capability | **Held** | Separate IDs/namespaces | Routing after Capabilities | Naming confusion |
| 7 | Skill=Role | **Held** | Bindings associations only | Role discovery separate | |
| 8 | Context dump | **Held** | Bounded skill context; `full_skill_dumped=false` | Budget + slices | Large slice growth |
| 9 | Reconstruct why Skill used | **Held** | Invocation evidence + source_versions | record_invocation | Incomplete if bridge bypassed |
| 10 | Stale source stays active | **Held** | `detect_staleness` hash mismatch | stale→reverify path | Operator must run check |
| 11 | Conflicting Skills | **Held** | `arbitrate_conflicts` escalates | SKILL_CONFLICT | Resolution rules sparse |
| 12 | Agent auto-approves Skill | **Held** | No auto_approve; gates | | |
| 13 | Orchestrator hardcodes Skills | **Held** | Registry-driven; facade has no pack IDs | | |
| 14 | Skill alters permissions | **Held** | Security checker | | |
| 15 | Skill executes tools | **Held** | Skills are knowledge; Agents own tools | | |
| 16 | Skill invents requirements | **Held** | UX skeleton marks UNKNOWN | Electrolinera tests | |
| 17 | Unknown treated as false | **Held** | Epistemic labels in UX/role discovery | | |
| 18 | Roles without hardcoding all | **Partial** | `discover_roles_for_intent` heuristics | Not a full HR catalog | Heuristic coverage UNKNOWN at scale |
| 19 | UI/UX really active? | **Held** | Still `unavailable` | NEEDS_SOURCE | |
| 20 | Marketing without need? | **Held** | Negative triggers + electrolinera | | |
