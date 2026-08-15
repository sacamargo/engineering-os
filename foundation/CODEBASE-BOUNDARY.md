# Codebase Intelligence Read Boundary

Policy for what Phase 5 analysis may open.

## May inventoriable (path metadata)

- Source, config, docs, manifests inside the repository root
- Sensitive path **names** (listed as sensitive, content blocked)

## Must not read content

- `.env`, `.env.*` (except explicit `*.example` / `*.sample` templates)
- `credentials.json`, private keys (`*.pem`, `id_rsa`, …)
- Paths matching secret/password/credential heuristics

## Must not traverse as source roots

- `.git`, `node_modules`, virtualenvs, build/cache dirs (see `codebase/boundary.py`)

## Must not access

- Paths outside the requested repository root / workspace
- Network services or remote repos unless an explicit Adapter is introduced later

## Epistemic rule

Inventory of a sensitive path is **observation of existence**, not authorization to exfiltrate secrets.
