# Plan Generation

This document defines how Engineering OS transforms a user intent into an Execution Plan.

It is a **generation protocol**, not a runtime Orchestrator and not a rigid template applied to every project.

Authorities: [Intent Resolution](INTENT-RESOLUTION.md), [Execution Plan](EXECUTION-PLAN.md), [Role ↔ Capability Binding](ROLE-CAPABILITY-BINDING.md)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Need a repeatable way to derive tasks/artifacts from resolved Capabilities. |
| Problem avoided | One mega SDLC checklist forced onto every request. |
| If absent | Plans become improvised and non-comparable. |
| Why not a single playbook? | Playbooks guide methods; generation composes many Capabilities situationally. |

---

## Inputs

1. Utterance + intent frame
2. Capability resolution record (candidates/primary/secondary/gaps)
3. Optional repository/system context
4. Role-capability binding defaults
5. Relevant Knowledge Unit metadata (not entire bodies until bound)

---

## Algorithm (Logical)

```text
1. Frame intent
2. Resolve Capabilities (and gaps)
3. If no selectable Capability and no clarifying path → stop with insufficient coverage
4. For each selected Capability:
   a. Identify expected artifact types from fulfillment guidance
   b. Create planning tasks to produce those artifacts
   c. Attach default roles from bindings
5. Add execution dependencies only where artifact/task semantics require them
6. Define gates for critical approvals
7. Mark parallelizable tasks (no dependency)
8. Attach escalations where professional validation is indicated
9. Emit Execution Plan revision 1
```

---

## Example (illustrative, not a fixed template)

Intent: “Build a booking SaaS”

Possible selected Capabilities (if present in catalog):

- Architecture
- Security Review
- Test Planning
- Observability

Possible artifacts:

- Architecture
- Security Review
- Test Strategy
- Observability Plan

Later phases may add Database/API/Implementation/Deployment Capabilities when they exist — generation must not invent them.

---

## Rules

1. **Need-based generation** — only include Capabilities that resolution selected (plus explicit related secondaries).
2. **No invented Capabilities** — gaps become `insufficient_coverage` + blocked/escalated work.
3. **No universal waterfall** — do not always insert every engineering discipline.
4. **Knowledge after selection** — load playbook/framework bodies when creating concrete task instructions.
5. **Dependencies are semantic** — Architecture artifact may precede security review of that architecture; related_capability alone does not force order.

---

## Output

An [Execution Plan](EXECUTION-PLAN.md) object (fixture or future store) plus clarifying questions when confidence is low.

---

## Non-Goals

- LLM prompt pack as source of truth
- Automatic coding of the product
- Guaranteed optimal task graphs
