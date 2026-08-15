# Skill Contracts (Phase 8)

Canonical contracts for Integrated Skills (`eos.skillpack.*`).

These are **not** knowledge-unit contracts (`eos.skill.*` / `contracts/unit.schema.json`).

## Artifacts

| Path | Purpose |
|---|---|
| `skillpack.schema.json` | Manifest shape |
| `../validate_skills.py` | Validator CLI |
| `fixtures/` | Valid / invalid examples |

## Invariants

- Provenance required
- Duplicate IDs rejected
- Unknown capability / role / tool references rejected (when catalog provided)
- Privilege-granting fields rejected
- `unavailable` requires `provenance.unavailable_source_content: true`
- Composition must not imply hidden task DAG (`implies_task_dependency` must be false)
