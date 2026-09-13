# 23 — Content Factory Operating Model

This document integrates the current system, flow, control and semantic models into one operating model.

## 1. Four layers

```text
CONTENT ECOSYSTEM
│
├── STRATEGIC INTENT
├── AUDIENCE / MARKET CONTEXT
├── CONTENT FACTORY
├── EXPERIENCE / CHANNELS
└── PRODUCT / BUSINESS OUTCOMES

CONTENT FACTORY
│
├── VALUE FLOW
│   ├── Input
│   ├── Knowledge
│   ├── Editorial
│   ├── Production
│   ├── Quality
│   ├── Distribution
│   └── Learning
│
├── FACTORY CONTROL
│   ├── demand / priority
│   ├── intake / routing
│   ├── WIP / queues
│   ├── capacity / resources
│   ├── scheduling
│   ├── ownership / service expectations
│   ├── orchestration
│   └── bottleneck management
│
└── SHARED SEMANTIC SUBSTRATE
    ├── structured content
    ├── knowledge graph
    ├── identity / revisions
    ├── evidence / claims
    ├── provenance
    ├── dependencies
    ├── taxonomy / audience metadata
    └── reusable components
```

## 2. Factory purpose

The Content Factory converts bounded demand and evidence-backed knowledge into verified, authorized and externally releasable content products while preserving provenance and reusable meaning.

It does not own the entire ecosystem outcome.

## 3. Factory flow

```text
STRATEGIC DEMAND + EXTERNAL CONTEXT
                ↓
             INPUT
                ↓
           KNOWLEDGE
                ↓
           EDITORIAL
                ↓
           PRODUCTION
                ↓
             QUALITY
                ↓
          DISTRIBUTION
                ↓
          EXTERNAL EFFECT
                ↓
            LEARNING
                ↓
      knowledge / editorial / production updates
                ↺
```

This is a value-flow projection, not one global object lifecycle.

## 4. Work package

The operational unit is a bounded `Content Work Item` / `Work Package`.

```text
WORK ITEM
├── work_item_id
├── strategic_intent_ref
├── audience_context_ref
├── objective
├── requested_outcome
├── input_refs
├── knowledge_basis_refs
├── dependencies
├── required_capabilities
├── risk / review class
├── owner
├── priority
├── constraints
├── acceptance criteria
├── release requirements
└── success signals
```

A work item is not an asset, release, request, or publication.

## 5. Control-plane function

Factory Control acts on work items and flow, not on the truth of content.

For a work item it determines:

```text
should it enter?
→ should it wait?
→ where should it route?
→ what capability should process it?
→ is capacity available?
→ what is blocking it?
→ which dependency is constraining it?
→ when should it be released?
```

Factory Control must not silently change claims, knowledge or accepted content.

## 6. Semantic substrate function

The semantic substrate ensures that systems share identity and meaning rather than copying uncontrolled text.

```text
ENTITY
→ REVISION
→ STATE
→ PROVENANCE
→ DEPENDENCY
→ AUTHORITY
→ TRANSITION
```

The current ontology candidate, state model, dependency/provenance model and authority model are separate representations over this substrate.

## 7. Decision boundaries

```text
Strategy
  → strategic intent

Input
  → admission / routing candidate

Editorial
  → proceed / hold / reject / update + specification

Production
  → asset revision

Verification
  → conformity assessment

Acceptance
  → exact revision accepted / rejected

Distribution
  → release / publication effect

Learning
  → interpretation / experiment / update candidate
```

Authority is not inherited from process completion.

## 8. Flow metrics

The factory should be observable at the flow level:

```text
lead time
cycle time
queue time
blocked time
WIP
throughput
first-pass yield
rework
approval latency
release latency
```

Flow metrics must be interpreted with quality and outcome metrics.

## 9. Quality / governance metrics

```text
verification failures
revision count
acceptance rate
factual corrections
policy exceptions
dependency invalidations
publication incidents
```

## 10. Outcome metrics

```text
audience response
retention / engagement where meaningful
conversion / product outcome
experiment results
reuse rate
content decay / retirement
```

No metric is a goal merely because it is easy to measure.

## 11. Bottleneck principle

The factory's throughput is constrained by the current system bottleneck.

Therefore:

```text
identify constraint
→ protect constraint from excess WIP
→ feed it appropriate work
→ remove avoidable blockers
→ elevate capacity where justified
→ reassess constraint
```

Local utilization is not the primary optimization target.

## 12. Automation principle

Automation should be matched to task characteristics.

```text
repeatable + low ambiguity + reversible
    → automate freely within policy

ambiguous or evidence-dependent
    → assist / escalate

consequential / externally irreversible
    → explicit authority boundary
```

## 13. Ecosystem feedback

Factory Learning is not the same as ecosystem strategy learning.

```text
FACTORY LEARNING
→ improve knowledge, editorial choices, production and distribution

ECOSYSTEM LEARNING
→ may change audience assumptions, product strategy, portfolio,
  business objectives or investment
```

The second path crosses the factory boundary explicitly.

## 14. No silent cross-boundary promotion

The following are invalid by default:

```text
request → production
production → knowledge
metric → learning truth
learning → strategy
observation → accepted claim
verification → publication
history → current authority
```

Each requires an explicit transition and appropriate evidence/authority.

## 15. Integrated map

```text
                               CONTENT ECOSYSTEM
                                      │
              ┌───────────────────────┼─────────────────────────┐
              ▼                       ▼                         ▼
       STRATEGY / INTENT      AUDIENCE / MARKET          PRODUCT / BUSINESS
              │                       │                         │
              └───────────────┬───────┴───────────────┬─────────┘
                              ▼                       ▼
                        CONTENT DEMAND          PRODUCT CONTEXT
                              │                       │
                              └────────────┬──────────┘
                                           ▼
                                 ┌──────────────────┐
                                 │  CONTENT FACTORY │
                                 ├──────────────────┤
                                 │ VALUE FLOW       │
                                 │ CONTROL PLANE    │
                                 │ SEMANTIC LAYER   │
                                 └────────┬─────────┘
                                          │
                                          ▼
                                  CONTENT PRODUCTS
                                          │
                                          ▼
                                  EXPERIENCE / CHANNEL
                                          │
                                          ▼
                                    AUDIENCE RESPONSE
                                          │
                           ┌──────────────┴──────────────┐
                           ▼                             ▼
                     MARKET SIGNALS                BUSINESS OUTCOMES
                           │                             │
                           └──────────────┬──────────────┘
                                          ▼
                                   STRATEGY UPDATE
                                          ↺
```

## 16. Implementation status

`PHASE 1 COMPLETE / PHASE 2 IN PROGRESS`

The repository contains a coherent executable bounded runtime, explicit zone operating contracts, a capability/integration boundary, durable workspace artifact materialization, durable runtime control state, and CI verification for the repository test suite.

Phase 1 adds durable runtime control state: SQLite-backed work-item state and an append-only event journal are committed atomically, and a new runtime instance reconstructs the persisted state and event history after restart. This is distinct from `ArtifactStore`: runtime persistence is recovery/control state, while artifact materialization is repository evidence projection.

Phase 2 now has a concrete OpenAI Responses provider adapter with an explicit `OPENAI_API_KEY` secret boundary and an opt-in external execution test. Unit tests verify the provider boundary and mapping into `ExecutionResult`. Phase 2 is not complete until a real credential is available in an execution environment and a real provider call, connectivity result and revision-bound verification are observed.

The following remain outside the completed phases: real external publication destination, independently verified external effect, external-operation idempotency/reconciliation, queues/leases, broader control-plane operations, operations/governance and the learning loop.

Phase sequence:

```text
1 durable runtime                COMPLETE
2 real execution                 IN PROGRESS
3 real external effect           NOT STARTED
4 reliability and control        NOT STARTED
5 factory control plane          NOT STARTED
6 operations and governance      NOT STARTED
7 learning loop                  NOT STARTED
```

Completion of a phase requires executable evidence and CI verification where code changes are involved; documentation alone does not advance phase status.