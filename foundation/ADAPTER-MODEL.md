# Adapter Model

Adapters connect Engineering OS Core to external tools and environments.

```text
Core ≠ Adapter
```

Engineering OS must not depend on Cursor — or any single vendor — to remain coherent.

---

## Possible Adapters (non-exhaustive)

| Adapter target | Example use |
|---|---|
| Cursor | Skills / rules bridges |
| Claude / ChatGPT | Prompt/tool bridges |
| CLI | Local operator interface |
| GitHub | PRs, issues, checks |
| CI/CD | Pipeline evidence |
| Cloud | Deploy/observe hooks |

---

## Rules

1. Core models (Foundation, Contracts, Capabilities, Execution objects) stay vendor-neutral.
2. Adaptations may translate IDs and workflows; they must not redefine Core semantics.
3. If an adapter disappears, Core scenarios (Rivallium, padel-iot) remain meaningful.
4. Prefer thin adapters over forking playbooks per vendor.

---

## Relation to Layers

```text
Foundation / Contracts / Capabilities / Execution
                 ↑
            Adapters (optional)
                 ↑
         Vendor tools / runtimes
```
