# Agency Scenario Tests

Conceptual agency cases for Engineering OS Phase 3.

These tests do **not** build products. They verify that each high-level intent can be represented as:

- intent recognized
- capabilities resolved (known catalog only)
- gaps detected (no invented Capability IDs)
- artifacts identified
- tasks generated (plan-level)
- validation required
- human escalation when necessary

Run:

```bash
python3 -m unittest discover -s tests/agency -v
```
