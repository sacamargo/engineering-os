# Gap Detection

Engineering OS must detect what it **does not cover** before inventing work or Capabilities.

This extends Intent Resolution’s `insufficient_coverage` into Execution planning.

Authorities: [Intent Resolution](INTENT-RESOLUTION.md), [Plan Generation](PLAN-GENERATION.md), [Human Escalation](HUMAN-ESCALATION.md)

---

## Gap Types

| Gap type | Meaning |
|---|---|
| `missing_capability` | No catalog Capability for an intent class |
| `missing_knowledge` | Capability exists but required Knowledge Units are absent/weak |
| `missing_artifact` | Plan requires an artifact that cannot yet be produced |
| `missing_specialist` | Required role/professional expertise unavailable |
| `missing_validation` | No evidence path/gate can verify a claim |

---

## Detection Rules

1. Compare framed intent classes to active Capabilities.
2. For selected Capabilities, check whether fulfillment bindings exist.
3. During plan generation, mark artifacts/tasks that cannot be created due to gaps.
4. Distinguish software-reasoning gaps from professional/legal/physical gaps.
5. **Never invent** Capability IDs, unit IDs, or fake specialist authority.

---

## Example — Padel facility automation

Intent may imply needs across:

```text
Software architecture
Security
IoT / device integration
Networking
Reliability / observability
Cloud / mobile remote access
Physical access control
Electrical engineering
```

Engineering OS may cover some via landed Capabilities (architecture, security, observability, testing).

It must emit gaps / escalations for areas without catalog coverage — especially electrical and regulated physical work — instead of fabricating Capabilities.

---

## Plan Consequences

| Gap | Typical plan effect |
|---|---|
| Missing capability | `insufficient_coverage`; blocked milestone or narrowed scope |
| Missing knowledge | Task blocked or research/escalation task |
| Missing specialist | Human escalation |
| Missing validation | Gate cannot pass |

---

## Anti-Patterns

- Silent omission of gaps
- Inventing temporary Capabilities in the plan
- Treating related software Capabilities as covering physical engineering
