# Engineering OS Agency — Use Cases

These scenarios test the **functional MVP** of Engineering OS as an agency.

How to run in Cursor:

1. Open this repository
2. Start a chat that can use project skills
3. Invoke or allow `engineering-os-agency`
4. Paste one use case prompt below
5. Verify the response includes an **Engineering OS Routing** record

Expected catalog Capabilities:

- `eos.capability.design.system-architecture`
- `eos.capability.security.review`
- `eos.capability.quality.test-planning`
- `eos.capability.operations.observability`

---

## UC-01 — Architecture only

**Prompt**

```text
Design the architecture for a multi-tenant SaaS notes app.
I need clear service boundaries and a local-dev friendly design.
```

**Expected routing**

- Primary: `eos.capability.design.system-architecture`
- Fulfillment includes `eos.playbook.design.system-architecture`

**Pass criteria**

- Routing record present
- Architecture recommendation with boundaries
- Does not pretend to be a full security audit

---

## UC-02 — Security audit only

**Prompt**

```text
Audit this application for security vulnerabilities.
Focus on authentication, authorization, and admin surfaces.
```

**Expected routing**

- Primary: `eos.capability.security.review`
- Fulfillment includes `eos.playbook.security.application-review`

**Pass criteria**

- Security review structure and prioritized next actions
- Does not redesign the whole system unless asked

---

## UC-03 — Architecture reviewed for security risk

**Prompt**

```text
Review this architecture and determine whether it introduces security risks:
an edge controller is authoritative offline, and a cloud gateway provides remote phone control for a facility automation system.
```

**Expected routing**

- Primary: `eos.capability.security.review`
- Secondary or related: `eos.capability.design.system-architecture`

**Pass criteria**

- Security-first analysis of trust boundaries
- Architecture used as object of review, not silently replaced
- No Capability DAG language (“must call architecture first”)

---

## UC-04 — Multi-viewpoint greenfield app (core agency test)

**Prompt**

```text
I want to build a SaaS booking platform for sports courts.
It must be secure, testable, and observable in production.
Start by telling me which Engineering OS Capabilities apply, then produce the first architecture, security review plan, test plan, and metrics design.
```

**Expected routing**

Candidates should include:

- System Architecture Design
- Application Security Review
- Test Planning
- Observability and Metrics Design

**Pass criteria**

- Multi-Capability routing record
- Distinct outputs per Capability (not one blended mega-doc with no ownership)
- Honest sequencing by artifact dependency
- No invented Capabilities

---

## UC-05 — Metrics / observability focused

**Prompt**

```text
What metrics and alerts should this checkout API expose?
We care about latency, errors, and payment failures.
```

**Expected routing**

- Primary: `eos.capability.operations.observability`

**Pass criteria**

- Golden signals / actionable alert intent
- Vanity metrics rejected or deprioritized

---

## UC-06 — Test planning focused

**Prompt**

```text
Plan the tests for a new checkout redesign before release.
We have one week and payment risk is high.
```

**Expected routing**

- Primary: `eos.capability.quality.test-planning`

**Pass criteria**

- Risk-based plan
- Explicit deferred tests with residual risk

---

## UC-07 — Catalog gap (must not invent Capabilities)

**Prompt**

```text
My checkout is extremely slow and I suspect the database indexes are wrong.
Optimize this for me end-to-end.
```

**Expected routing**

- `insufficient_coverage` for performance and/or deep database optimization
- Primary may be null

**Pass criteria**

- Does **not** invent `eos.capability.performance.*` or similar
- Explains gap and asks how to proceed
- May suggest adjacent existing Capabilities only if honestly partial (optional), without claiming full coverage

---

## UC-08 — Spanish utterance, English canonical knowledge

**Prompt**

```text
Diseña la arquitectura de una app SaaS de reservas y dime cómo la observaríamos en producción.
```

**Expected routing**

- Candidates include architecture and observability
- Response may be in Spanish
- Canonical IDs and unit references remain English catalog IDs

**Pass criteria**

- Language of conversation ≠ forced English
- Routing still uses canonical Capability IDs

---

## UC-09 — Padel court facility automation (regression)

**Prompt**

```text
I want complete automation for a padel court: access, lighting, and related systems.
It must keep working locally if internet is lost, and authorized users must control it remotely from a phone when connected.
Design the architecture and call out security and professional-validation boundaries.
```

**Expected routing**

- Primary: `eos.capability.design.system-architecture`
- Related/secondary may include security review

**Pass criteria**

- Local autonomy preserved
- Remote path not authoritative for offline-required functions
- Explicit professional physical validation escalation

---

## Quick verification checklist

After each use case, confirm:

1. `## Engineering OS Routing` section exists
2. Capability IDs exist in `capabilities/`
3. Fulfillment IDs exist in `playbooks/` or `frameworks/`
4. No invented Capabilities
5. Multi-intent cases do not collapse into one fake mega-Capability
