# Project Roadmap

This roadmap defines the long-term evolution of Engineering OS.

It is directional, not a delivery schedule. Dates are intentionally absent. Sequence matters more than calendar promises.

---

## Phase 0 — Foundation (Current)

Establish the kernel of the system.

- [x] Project vision
- [x] Philosophy
- [x] Engineering principles
- [x] System architecture
- [x] Knowledge architecture
- [x] Capability model
- [x] Engineering workflow (Git + repository discipline)
- [x] Project roadmap
- [ ] Public license decision (deferred — see below)
- [ ] Public contribution guide (deferred — see below)

**Exit criteria:** A new reader can understand what Engineering OS is, what it is not, how system/knowledge/capability layers relate, how the repository will be developed, and what must be built before modules exist.

### Deferred on Purpose in Phase 0

| Deferred item | Why deferred |
|---|---|
| `LICENSE` | Licensing is a distribution decision. A knowledge system may need different terms than a typical software project. Choosing too early risks relicensing cost. |
| `CONTRIBUTING.md` | Contribution process without contracts, Git history norms in use, and a distribution posture is ceremonial. Workflow + roadmap carry interim constraints. |

---

## Phase 1 — Contracts

Implement Knowledge Architecture and Capability Model as enforceable authoring contracts.

Expected work:

- [x] On-disk metadata schema for knowledge units and Capabilities
- [x] Validation rules for IDs, required fields, and relationship types (including `fulfilled_by`)
- [x] Naming identity conventions aligned to `eos.<type>.<domain>.<name>`
- [x] Structural quality rules that prevent Capability relationship anti-patterns (method I/O on Capabilities; module-owned `fulfilled_by`)
- [x] Deprecation / `supersedes` policy at lifecycle + relationship level
- [ ] Path layout enforcement (deferred — IDs remain authoritative)
- [ ] Cross-reference consistency rules for body links vs metadata (deferred)
- [ ] Automated detection of Capability 1:1 playbook aliases (deferred until catalog evidence)

**Exit criteria:** The first Capability and its fulfillment units can be created against explicit contracts, and an AI system can route intent → Capability → units without repository folklore.

Phase 1 contract machinery is landed in `contracts/`. Content catalog creation remains Phase 2.

---

## Phase 2 — Core Methodology Spine

Introduce the minimum set of Capabilities and knowledge units that make the system operationally useful.

### Phase 2 Proof (landed)

- [x] First coarse Capability: `eos.capability.design.system-architecture`
- [x] Architecture fulfillment playbook + trade-off framework
- [x] Second coarse Capability: `eos.capability.security.review`
- [x] Security fulfillment playbook + risk-prioritization framework
- [x] Soft `related_capability` adjacency between architecture and security review
- [x] Contract validation over the live catalog directories
- [x] Intent Resolution protocol + disambiguation experiment (candidates vs selection vs insufficient coverage)

### Broader Phase 2 backlog

Priority order (subject to revision with evidence):

1. **Coarse Capability catalog** — add intent classes only where routing value is clear
2. **Decision frameworks** — expand beyond the architecture trade-off proof
3. **Engineering standards** — quality bars that raise the floor
4. **Playbooks** — end-to-end ways of working for high-frequency situations
5. **Checklists** — verifiable gates for readiness and risk
6. **Templates** — durable starting structures
7. **Workflows** — composable sequences with clear boundaries
8. **Skills** — portable AI-operable procedures

Early Capabilities and playbooks should target timeless engineering intents (for example: security review, change delivery, incident response, test planning), not tool onboarding.

**Exit criteria:** A team can adopt a coherent Capability subset and improve real delivery outcomes without adopting the entire catalog.

---

## Phase 3 — Skills System

Specialize the knowledge architecture for reliable AI execution.

Expected work:

- Skill contract specialization (inputs, outputs, failure modes)
- Composition rules between skills, playbooks, and checklists
- Context package patterns for common Capabilities and situations
- Guidance for evaluating skill quality across models and tools

**Exit criteria:** Skills are reusable across AI systems without rewriting the methodology for each vendor.

---

## Phase 4 — Adaptations

Add optional bridges to popular AI environments.

Expected work:

- Adaptation guidelines (translate/package, never fork truth)
- Reference adaptations for major tools as demand justifies
- Mapping from the vendor-neutral consumption protocol to tool mechanisms

**Exit criteria:** Users of specific tools can adopt Engineering OS quickly without making the core tool-dependent.

---

## Phase 5 — Organizational Scale

Support teams and organizations adopting Engineering OS as shared operating infrastructure.

Expected work:

- Adoption paths by team maturity
- Private extension namespaces and overlays
- Alignment with existing SDLC, compliance, and governance needs
- Patterns for measuring whether adoption improves outcomes
- Public license + contribution model once distribution is intentional

**Exit criteria:** Organizations can run Engineering OS as a living system, not a static document archive.

---

## Phase 6 — Longevity Operations

Operate Engineering OS for decades, not launches.

Expected work:

- Release and versioning model for knowledge units
- Continuous pruning of obsolete content
- Translation/derivation strategy if multilingual distributions are needed
- Stewardship appropriate to an open world-class framework

**Exit criteria:** The system remains coherent as contributors, tools, and engineering practice evolve.

---

## Explicit Non-Goals (Near Term)

- Building a commercial product platform
- Shipping a hosted SaaS control plane
- Creating hundreds of shallow prompts
- Ranking or endorsing AI vendors
- Requiring a specific IDE, language, or cloud
- Premature certification or badge systems
- Adding open-source ceremony files before distribution need

---

## Change Policy for This Roadmap

The roadmap may change when evidence demands it.

Changes should record:

1. What shifted
2. Why the previous sequence was insufficient
3. What principle or constraint remains intact

The foundation may evolve slowly. The roadmap may evolve faster. Knowledge units may evolve fastest — provided they honor the kernel.
