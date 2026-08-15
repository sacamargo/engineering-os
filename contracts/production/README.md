# Production Operations Contracts

Validate environments, operations, incidents, alerts, health, approvals, permissions,
rollback, and evidence payloads for Phase 9.

```bash
python3 contracts/validate_production.py --self-check
```

Rules encoded:

- production environment ⇒ high/critical risk + human_required approval
- succeeded + unknown health ⇒ invalid
- resolved incident without resolution evidence ⇒ invalid
- secret-like strings in payloads ⇒ invalid
- Alert ≠ Incident (separate shapes)
