# 30 — Digital Product Development Lifecycle

Status: `CURRENT / GOVERNING PRODUCT PROCESS`

This document defines the canonical stage-gated lifecycle for developing a digital product across the ecosystem. It is a process boundary, not a repository map. Repositories implement capabilities or surfaces; they do not become owners merely because they contain an artifact.

## 1. Governing principle

A product may advance only when the current stage exit criteria are satisfied and the transition decision is explicit.

```text
STAGE
  ↓
WORK ALLOWED WITHIN STAGE
  ↓
EVIDENCE / ARTIFACTS
  ↓
EXIT GATE
  ↓
EXPLICIT DECISION
  ↓
NEXT STAGE
```

A stage may terminate as:

```text
PROCEED
RETURN
HOLD
STOP
```

No stage may silently promote an observation, hypothesis, research result, prototype, verification result or metric into authority for the next stage.

## 2. Canonical lifecycle

```text
0 PRODUCT BRIEF
        ↓
1 DISCOVERY
        ↓
2 PROBLEM / OPPORTUNITY
        ↓
3 PRODUCT DECISION
        ↓
4 SOLUTION DESIGN & VALIDATION
        ↓
5 PRODUCT SPECIFICATION
        ↓
6 BUILD & INTEGRATION
        ↓
7 RELEASE & LIVE OPERATION
        ↓
8 LEARNING / EVOLUTION / RETIREMENT
        ↺
```

The lifecycle is gated, but work inside a stage can iterate. The permitted iteration is local to the current stage unless the exit evidence demonstrates that a prior-stage assumption must be reopened.

The lifecycle deliberately separates problem validation, product decision, solution validation, specification, implementation, and real-world operation. User research is continuous across the lifecycle rather than a one-time activity.

## 3. Stage 0 — Product Brief

### Purpose

Establish why the product initiative exists and bound the problem space before discovery work begins.

### Inputs

- business or organizational intent
- known constraints
- existing context and evidence, if any

### Allowed work

- define desired business/product outcome
- identify initial target users or affected parties
- define scope and explicit non-goals
- identify known constraints
- define initial success signals
- identify critical unknowns to investigate

### Required outputs

- product brief
- target outcome
- initial user/context boundary
- constraints
- non-goals
- initial success signals
- initial unknowns

### Exit gate

The team can state, without solution-specific ambiguity:

1. why the initiative exists;
2. who or what is in scope;
3. what outcome is sought;
4. the material constraints;
5. what is explicitly out of scope;
6. what must be learned in Discovery.

### Forbidden advancement

Do not commit to a product solution, architecture, UI or implementation merely because a plausible idea already exists.

## 4. Stage 1 — Discovery

### Purpose

Build an evidence-backed understanding of users, context, current experience, market/domain conditions, alternatives and constraints.

### Allowed work

- user interviews and observation
- existing-data analysis
- current-experience / journey mapping
- market research
- competitor intelligence
- domain research
- accessibility and inclusion research
- review of existing products and workflows
- evidence synthesis
- identification of needs, barriers, patterns and unknowns

Personas, journey maps and similar artifacts are optional instruments. They are created when they improve understanding or decision quality, not as mandatory checklist outputs.

### Required outputs

- evidence set with provenance
- user/context findings
- current-experience understanding
- market/alternative findings where relevant
- needs and barriers
- constraints
- opportunities/candidate problems
- explicit unknowns

### Exit gate

There is sufficient evidence to explain:

1. who the relevant users/actors are;
2. what they are trying to accomplish;
3. how they do it now;
4. where meaningful problems or unmet needs occur;
5. what evidence supports those findings;
6. what alternatives or competing approaches exist;
7. what constraints materially affect the opportunity;
8. which unknowns remain critical.

If a critical answer is missing, return to Discovery. Do not proceed to solution design.

### Evidence boundary

Research is evidence. It is not automatically a product decision, claim of causality, or authorization to build.

## 5. Stage 2 — Problem / Opportunity Definition

### Purpose

Convert Discovery evidence into an explicit, bounded problem/opportunity model without prematurely selecting a solution.

### Allowed work

- cluster and interpret evidence
- formulate problem statements
- identify user needs
- define opportunity areas
- formulate hypotheses
- identify assumptions
- define desired outcomes and measurable success conditions
- identify alternative interpretations

### Required outputs

```text
Problem Statement
Target User / Actor
Evidence Basis
Desired Outcome
Key Assumptions
Known Alternatives
Critical Unknowns
Candidate Opportunity
```

### Exit gate

A decision-maker can distinguish:

- observed evidence from interpretation;
- problem from proposed solution;
- desired outcome from feature;
- supported assumptions from untested assumptions.

The problem is bounded enough that alternative solutions can be evaluated against it.

If the problem cannot be stated without embedding a predetermined solution, return to Discovery or reformulate the problem.

## 6. Stage 3 — Product Decision

### Purpose

Make the explicit decision whether and why the organization should invest in solving the defined problem.

### Allowed work

- compare opportunity against business/product intent
- evaluate evidence strength
- compare alternative directions
- assess expected value and material risks
- identify feasibility constraints at the level necessary for the decision
- define investment/scope boundary
- authorize or reject the next stage

### Decision outcomes

```text
STOP
RESEARCH MORE
PROCEED
```

### Required output

An explicit decision record containing:

- decision
- problem/opportunity reference
- evidence basis
- alternatives considered
- chosen direction or bounded exploration
- tradeoffs
- constraints
- confidence
- authority
- conditions for reversal

### Exit gate

There is an explicit authorized decision to investigate/build a bounded product solution, with a defined desired outcome and scope.

For Content Factory integration, the downstream representation may be `ContentDemand`; for a broader digital product it may be a product-specific demand/specification object. The producer-side decision lifecycle remains outside Content Factory unless an explicit ownership decision changes that boundary.

## 7. Stage 4 — Solution Design & Validation

### Purpose

Explore solution alternatives and validate the riskiest solution assumptions before committing to production implementation.

### Allowed work

- information architecture
- user flows
- service/process design
- interaction design
- UX/UI concepts
- technical feasibility experiments
- prototypes
- usability testing
- accessibility validation appropriate to the prototype
- comparison of solution alternatives
- iterative refinement

### Required outputs

- selected solution direction
- validated critical user flows
- prototype or equivalent testable representation
- tested assumptions
- unresolved risks
- explicit rejected alternatives where decision-relevant

### Exit gate

Evidence is sufficient to state that:

1. the proposed solution addresses the defined problem;
2. critical user flows are understandable and usable enough for the intended next step;
3. the highest-risk assumptions have been tested to the required confidence;
4. material feasibility constraints are understood;
5. remaining risks are explicit and accepted for the next stage.

If the solution fails validation, remain in Stage 4 or return to Stage 2. Do not compensate for failed validation by writing more production code.

## 8. Stage 5 — Product Specification

### Purpose

Translate the validated solution into an executable product boundary.

### Allowed work

- functional requirements
- acceptance criteria
- non-functional requirements
- data contracts
- integration contracts
- technical architecture
- security/privacy requirements
- observability requirements
- release requirements
- decomposition into bounded Work Items

### Required outputs

- product specification
- architecture decisions where required
- acceptance criteria
- release criteria
- dependency map
- Work Items
- authority requirements
- success measurement plan

### Exit gate

A competent delivery team can determine:

- what must be built;
- what must not be built;
- how each material requirement will be verified;
- what dependencies exist;
- what constitutes acceptance;
- what authority is required for release/effects.

If requirements are still being discovered through basic user research or solution exploration, return to Stage 4 rather than hiding uncertainty inside implementation tickets.

## 9. Stage 6 — Build & Integration

### Purpose

Produce the product according to the approved specification and verify that the implementation satisfies its contracts.

### Allowed work

- implementation
- integration
- test automation
- security testing
- accessibility testing appropriate to implementation maturity
- performance/reliability testing where required
- production-like validation
- defect correction
- controlled iteration against acceptance criteria

### Required outputs

- implementation revisions
- test evidence
- verified artifacts
- resolved or explicitly accepted defects/risks
- release candidate

### Exit gate

The release candidate:

1. satisfies the approved acceptance criteria;
2. has required verification evidence;
3. has required operational/security/accessibility checks;
4. has known residual risks explicitly recorded;
5. is linked to the exact revision being considered for release.

Execution success is not acceptance. Verification is not publication. Authority is not inherited from implementation completion.

## 10. Stage 7 — Release & Live Operation

### Purpose

Move the accepted product into an authorized real environment and observe its actual effects.

### Allowed work

- release preparation
- authorization checks
- deployment/publication
- staged rollout
- monitoring
- support
- incident response
- real-user research
- performance and outcome measurement
- controlled improvement

### Required outputs

- release/effect record
- externally observable deployment or publication evidence
- operational observations
- outcome measurements
- incidents and corrective actions where applicable

### Exit gate

A release is complete only when:

- the exact accepted revision is identified;
- release authority is explicit;
- the external effect is observable or its absence is explicitly recorded;
- operational state is known;
- measurement/observation mechanisms are active.

Publication/delivery is not proof of product success.

## 11. Stage 8 — Learning / Evolution / Retirement

### Purpose

Convert real-world observation into bounded learning and explicit future decisions.

### Allowed work

- analyze product outcomes
- conduct live user research
- compare results with success signals
- identify new problems or opportunities
- formulate learning candidates
- run controlled experiments
- update product decisions
- prioritize improvements
- supersede or retire obsolete functionality
- retire the product when justified

### Required outputs

- observations
- interpreted findings
- learning candidates
- explicit decisions
- revised product direction, if warranted
- retirement decision where applicable

### Exit gate

A learning claim is separated from raw measurement and tied to evidence and scope. Any material change to the product direction is an explicit decision, not an automatic consequence of a metric.

The next cycle returns to the earliest stage actually invalidated by the new evidence. It does not automatically restart from Stage 0.

## 12. Stage movement rule

The default movement is exactly one stage forward or one stage backward.

```text
CURRENT
  ├── PROCEED → CURRENT + 1
  ├── RETURN  → CURRENT - 1
  ├── HOLD    → remain
  └── STOP    → terminate initiative / preserve record
```

A return may skip only a stage whose assumptions are explicitly demonstrated to remain valid and whose reopening is unnecessary. Such a skip must be recorded in the decision. The default operating rule remains one-step movement.

No work should be performed solely because it belongs to a later stage.

## 13. Cross-stage contracts

The canonical transition objects are:

```text
ProductBrief
    ↓
DiscoveryResult
    ↓
ProblemOpportunity
    ↓
ProductDecision
    ↓
AuthorizedProductDemand
    ↓
ValidatedSolution
    ↓
ProductSpecification / WorkItems
    ↓
VerifiedReleaseCandidate
    ↓
AuthorizedRelease / Effect
    ↓
Observation / Learning
```

These names are conceptual contracts. Existing repositories may use narrower domain-specific representations. A new ontology class or implementation primitive requires a demonstrated semantic need.

## 14. Existing repository mapping

The current ecosystem is mapped by capability, not by forced one-to-one stage ownership.

| Lifecycle stage | Primary current implementation surfaces | Boundary |
|---|---|---|
| Product Brief | Content Factory / product-specific surfaces | intent/context |
| Discovery | AI Creative OS, Research Radar, Whisper Studio | research/evidence |
| Problem / Opportunity | Discovery layer + Content Factory semantic substrate | interpretation |
| Product Decision | Atlas Records + upstream product/discovery owner | authority |
| Solution Design & Validation | Whisper Studio + product-specific surfaces | solution validation |
| Product Specification | Content Factory + product-specific surfaces | executable specification |
| Build & Integration | Atlas Agent + controlled-agent-executor + product implementations | execution |
| Release & Live | product-specific effect surfaces + Atlas authority/effect boundary | external effect |
| Learning / Evolution / Retirement | Content Factory + Creative OS + Whisper + Atlas Records | evidence → learning → decision |

This table does not establish canonical ownership where the inspected repositories do not prove it.

## 15. Current ownership gaps

The most important unresolved cross-stage boundary is:

```text
DiscoveryResult
    ↓
ProductDecision
    ↓
AuthorizedProductDemand
```

The current Content Factory model already defines the factory-side `ContentDemand` boundary. The upstream producer of the canonical Discovery decision lifecycle remains unresolved. This is an ownership/contract gap, not evidence that another repository should be created.

The next implementation work for this gap is therefore blocked until the lifecycle itself is accepted and a bounded real case identifies the required producer-side contract.

## 16. Relationship to Content Factory

Content Factory begins at bounded demand and converts it through knowledge, editorial, production, quality, distribution and learning. Discovery/Decision is an upstream ecosystem function. This document therefore extends the ecosystem lifecycle without moving Discovery into Content Factory.

The existing Content Factory rules remain authoritative for epistemic boundaries, provenance, authority, verification, acceptance and publication.

## 17. Completion discipline

A stage is not complete because its documents exist.

For implementation-bearing stages, completion requires executable evidence appropriate to the stage. For research/decision stages, completion requires traceable evidence and an explicit decision record. A written artifact may describe a candidate state but cannot silently promote it to verified state.

The project must preserve:

- current stage
- current checkpoint
- proven state
- unproven state
- blockers
- next legitimate step
- return point

## 18. Terminal conditions

A lifecycle cycle may end only as:

```text
PROCEED
RETURN
HOLD
STOP
COMPLETED
INSUFFICIENT_EVIDENCE
USER_DECISION_REQUIRED
```

No automatic transition is implied by elapsed time, artifact creation, implementation completion, verification, publication or metric movement.
