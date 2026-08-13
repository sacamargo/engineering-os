# Human Escalation

Engineering OS must know when it may **reason**, when it may **execute**, and when it **requires human/professional approval**.

Authority companions: [Gap Detection](GAP-DETECTION.md), [Validation Gates](VALIDATION-GATES.md), [Execution Model](EXECUTION-MODEL.md)

---

## Earn-Its-Place

| Question | Answer |
|---|---|
| Problem solved | Autonomous agency without stop conditions is unsafe and dishonest. |
| Problem avoided | Silent overreach into regulated/physical/legal domains. |
| If absent | Plans invent authority they do not have. |
| Why not only gaps? | Gaps mark missing catalog coverage; escalation marks required human authority. |

---

## Distinctions

| Mode | Meaning |
|---|---|
| **Can reason** | May analyze, design options, identify risks in software terms |
| **Can execute** | May perform work inside declared authority (e.g., draft artifacts, propose code) |
| **Requires professional approval** | Must not claim completion/install/certify without qualified human |

---

## Escalation Triggers (non-exhaustive)

- Electrical / energy systems
- Physical safety and physical access hardware
- Legal interpretation and contracts
- Certifications and regulated compliance attestations
- Medical/safety-critical domains outside software competence
- Destructive production changes without change control
- Specialized hardware where incorrect action causes harm
- Explicit user request for human sign-off

---

## Minimal Escalation Record

| Field | Purpose |
|---|---|
| `id` | Escalation id |
| `project_id` | Project |
| `reason` | Why autonomy stops |
| `scope` | What is blocked |
| `required_authority` | Who/what must approve |
| `status` | `open` \| `approved` \| `rejected` \| `withdrawn` |
| `blocking` | Whether work must halt |

---

## Plan Effects

- Open blocking escalations prevent dependent gates from passing.
- Reasoning artifacts may still be produced with explicit “not an approval” labeling.
- Approval evidence should link into the Evidence Model.

---

## Anti-Patterns

- Treating architectural recommendations as electrical certification
- Closing escalations without recorded authority
- Hiding escalations inside long prose
