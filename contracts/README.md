# Contracts

Contracts make Engineering OS models **enforceable**.

## Knowledge Layer

| Artifact | Role |
|---|---|
| [SPEC.md](SPEC.md) | Knowledge unit/capability invariants |
| [unit.schema.json](unit.schema.json) | Single-unit metadata shape |
| [validate.py](validate.py) | Knowledge catalog validator (+ calls execution validator) |
| `fixtures/` | Knowledge fixtures |
| `tests/` | Knowledge contract tests |

## Execution Layer

| Artifact | Role |
|---|---|
| [execution/SPEC.md](execution/SPEC.md) | Project/task/artifact/plan/gate contracts |
| `execution/schemas/` | JSON Schema mirrors |
| [validate_execution.py](validate_execution.py) | Execution bundle validator |

## Delivery Layer

| Artifact | Role |
|---|---|
| [delivery/SPEC.md](delivery/SPEC.md) | Delivery/build/validation/release invariants |
| [validate_delivery.py](validate_delivery.py) | Delivery result validator |

## Validate

```bash
python3 contracts/validate.py
python3 contracts/validate_execution.py
python3 contracts/validate_codebase.py --self-check
python3 contracts/validate_delivery.py --self-check
python3 -m unittest discover -s contracts/tests -v
```

With no module directories / no example bundles, validators succeed with zero objects (progressive adoption).
