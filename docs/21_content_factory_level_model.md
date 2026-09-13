# 21 — Content Factory Level Model

This document evolves the previous eight-system graph into a multi-plane model of a Content Factory.

The purpose is not to add boxes for completeness. The purpose is to distinguish:

- value creation;
- factory control;
- shared semantic/data substrate;
- external outcomes.

## 1. The evolved model

```text
                                      CONTENT FACTORY
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
             VALUE / FLOW PLANE       FACTORY CONTROL          SHARED SUBSTRATE
                    │                        │                        │
                    │                portfolio / priority       content graph
                    │                intake / routing           provenance
                    │                WIP / queues              identity / revisions
                    │                capacity / scheduling     dependencies
                    │                ownership / SLA           policy metadata
                    │                orchestration             reusable components
                    │                bottleneck mgmt           evidence / claims
                    │                        │                        │
                    └────────────────────────┼────────────────────────┘
                                             │
                                             ▼
                               STRATEGY / PORTFOLIO INTENT
                                             │
                                             ▼
                                       INPUT SYSTEM
                                             │
                                             ▼
                                     KNOWLEDGE SYSTEM
                                             │
                                             ▼
                                     EDITORIAL SYSTEM
                                             │
                                             ▼
                                     PRODUCTION SYSTEM
                                             │
                                             ▼
                                      QUALITY SYSTEM
                                             │
                                             ▼
                                   DISTRIBUTION SYSTEM
                                             │
                                             ▼
                                      EXTERNAL EFFECT
                                             │
                                             ▼
                                      LEARNING SYSTEM
                                             │
                          ┌──────────────────┼──────────────────┐
                          ▼                  ▼                  ▼
                      KNOWLEDGE          EDITORIAL          PRODUCTION
                          │                  │                  │
                          └──────────────────┴──────────────────┘
                                             │
                                             ▼
                                      NEXT FACTORY CYCLE
```

The previous seven production-flow systems remain. `Factory Control` is not a sequential eighth stage; it is the control plane over the flow.

A new strategic layer is added above intake because current content-supply-chain practice explicitly links planning to business objectives, KPIs, budget and prioritization rather than beginning with raw requests alone.

A shared semantic substrate is also made explicit because structured content systems rely on reusable, linked, channel-neutral content, versions, metadata and provenance rather than isolated files.

## 2. Strategy / Portfolio Intent

This layer answers:

```text
What outcomes are we trying to create?
For whom?
Why now?
Which content bets are worth capacity?
What constraints or policies apply?
```

It produces portfolio-level intent rather than individual assets.

Typical objects:

```text
business objective
content objective
audience
initiative
campaign / program
portfolio priority
budget / capacity envelope
success hypothesis
```

Editorial decisions must be traceable to this layer when the work is strategic rather than purely reactive.

## 3. Input System

Input is not an inbox. It is the controlled entry point for demand and signals.

```text
signal
source
request
observation
external event
        ↓
 capture
        ↓
 classify
        ↓
 normalize
        ↓
 triage
        ↓
 route
```

Input produces work candidates, research needs, or editorial opportunities. It does not create production work merely because an item arrived.

## 4. Knowledge System

Knowledge is the factory's reusable evidence-bearing memory.

```text
research
  ↓
source
  ↓
evidence
  ↓
claim
  ↓
context / relation
  ↓
knowledge revision
```

The key property is reuse. The same knowledge revision may inform multiple content products while maintaining provenance to the underlying evidence.

## 5. Editorial System

Editorial transforms opportunity plus knowledge plus strategy into a bounded production intention.

```text
opportunity
  ↓
audience + objective
  ↓
priority
  ↓
editorial decision
  ↓
content specification
```

The specification is a production contract. It should state intended audience, objective, required claims, constraints, format/capability needs, channel assumptions and acceptance criteria.

## 6. Production System

Production is a capability network rather than four isolated media departments.

```text
content specification
        ↓
capability selection
        ↓
production work
        ↓
asset revision
        ↓
channel adaptation
```

Capabilities may include:

```text
text
image
video
audio
translation / localization
layout / design
research assistance
data visualization
```

The reusable content model should remain channel-neutral where possible. Channel-specific presentation should be added as context rather than copied into the semantic source.

## 7. Quality System

Quality is a control system at the point where representations are allowed to advance.

```text
production result
        ↓
verification
        ↓
review / revision
        ↓
acceptance
        ↓
release eligibility
```

Verification evaluates conformity against exact inputs and criteria. Acceptance is an authority-bearing decision. Release eligibility is not publication.

Review depth should be risk- and dependency-sensitive rather than identical for every content type.

## 8. Distribution System

Distribution converts accepted material into an externally delivered release.

```text
accepted revisions
        ↓
release bundle
        ↓
channel adaptation / configuration
        ↓
authorization
        ↓
publish / deliver
        ↓
external effect
```

A release may contain multiple dependent artifacts or channel variants that must reach a common readiness point.

## 9. Learning System

Learning closes the factory loop.

```text
external effect
        ↓
observation
        ↓
measurement
        ↓
interpretation
        ↓
experiment / decision
        ↓
learning
        ↓
knowledge / editorial / production update
```

A metric is not automatically a learning. A learning is not automatically truth. Evidence from experiments and observations should be evaluated before it changes reusable knowledge or policy.

## 10. Factory Control Plane

Factory Control operates across all value-flow stages.

```text
portfolio / priority
intake / routing
WIP limits
queues
capacity
scheduling
ownership
service expectations
resource allocation
orchestration
bottleneck management
```

Its core question is:

> Given current demand, state, dependencies and available capacity, what work should move next, through which capability, under which policy?

Factory Control must not become the source of content truth. It controls flow around content objects.

## 11. Shared semantic substrate

The factory needs a common substrate used by all systems.

```text
content / knowledge graph
├── identity
├── revisions
├── structured content
├── claims / evidence
├── provenance
├── dependencies
├── reusable components
├── audience / taxonomy metadata
└── lifecycle references
```

This substrate is not another workflow stage. It is the semantic layer through which systems share state without copying meaning between them.

## 12. The atomic unit of factory flow

The factory should not treat a file as its primary unit of work.

The more useful unit is a bounded `Work Package` or `Content Work Item`:

```text
WORK ITEM
├── intent / objective
├── audience
├── requested outcome
├── inputs
├── knowledge basis
├── dependencies
├── required capabilities
├── owner
├── priority
├── constraints
├── acceptance criteria
├── release requirements
└── success signals
```

One work item may produce many asset revisions and one release may contain many work-item outputs.

## 13. Flow geometry

The system is not a single linear pipeline.

```text
                         KNOWLEDGE
                       ↙     ↓      ↘
                  product-A  product-B  product-C
                       ↘     ↓      ↙
                      shared learning

REQUESTS ─→ WORK ITEMS ─→ CAPABILITIES ─→ RELEASES ─→ EFFECTS
                    ↑          │               │
                    │          └─ dependencies ┘
                    │
             FACTORY CONTROL
```

One input can lead to multiple outputs.
One knowledge revision can serve multiple products.
One production job can create multiple assets.
One release can bundle multiple assets.
One observation can affect many future work items.

## 14. Control principles

1. Pull work through the factory from real demand and available capacity.
2. Limit WIP at the constraining stages instead of maximizing local utilization everywhere.
3. Route work by required capability, risk and constraints.
4. Prefer reusable semantic content over duplicated channel-specific copies.
5. Bind review and acceptance to exact revisions.
6. Bundle related changes into releases when they share a readiness boundary.
7. Automate repeatable work; escalate uncertain or consequential choices to the appropriate authority.
8. Use measurement to improve decisions, not to create dashboard volume.
9. Treat bottleneck management as a continuous activity.
10. Preserve provenance and dependencies across every transformation.

## 15. Metrics of the factory

The factory needs three metric families.

### Flow metrics

```text
lead time
cycle time
WIP
throughput
queue time
blocked time
first-pass yield
rework rate
approval latency
```

### Quality / governance metrics

```text
verification failure rate
revision count
acceptance rate
factual correction rate
policy exceptions
dependency failures
publication incidents
```

### Outcome metrics

```text
audience response
engagement / retention where meaningful
conversion / business outcome
experiment lift
reuse rate
content decay / retirement signals
```

A factory metric must be tied to a management question. Raw volume is not success.

## 16. New top-level model

The resulting architecture is therefore:

```text
CONTENT FACTORY
│
├── STRATEGY / PORTFOLIO INTENT
│
├── VALUE FLOW
│   ├── INPUT
│   ├── KNOWLEDGE
│   ├── EDITORIAL
│   ├── PRODUCTION
│   ├── QUALITY
│   ├── DISTRIBUTION
│   └── LEARNING
│
├── FACTORY CONTROL
│   ├── priority
│   ├── routing
│   ├── WIP
│   ├── capacity
│   ├── scheduling
│   ├── orchestration
│   └── bottleneck management
│
└── SHARED SEMANTIC SUBSTRATE
    ├── structured content
    ├── knowledge graph
    ├── provenance
    ├── revisions
    ├── dependencies
    └── reusable components
```

The seven original production-flow systems remain intact. The model is elevated by making explicit the strategic intent above them, the control plane around them, and the semantic substrate beneath them.

## 17. Evidence basis

The model was evolved against current content-operations and content-supply-chain practice, structured-content architectures, provenance standards, flow-management methods, and experimentation/measurement practice.

Primary references include:

- Adobe, Content Supply Chain: workflow, planning, metadata, capacity, objectives, KPIs and bottlenecks.
- Contentful, Content Operations and Content Lifecycle: strategy, planning, creation, review, reuse, experimentation, retirement and optimization.
- Sanity, Content Operations and Editorial Workflows: structured content, governance, automation, shared process state, ownership, dependencies and agent participation.
- Sanity, Content Releases: multi-document release bundles, preview, validation and coordinated publication.
- W3C PROV: entities, activities, agents, derivation and provenance validation.
- Kanban Guide: WIP, flow, service expectations and flow metrics.
- Lean Enterprise Institute / Theory of Constraints: constraint identification, exploit, subordinate, elevate and continuous reassessment.
- Team Topologies: flow-oriented boundaries, capabilities and service interaction models.
- Google / Contentful experimentation guidance: hypothesis, experiment, measurement and validated learning.

## Status

`candidate / research-derived`

This document is a system-level hypothesis. It should be validated against real Content Factory cases before being treated as a final operating model or implementation architecture.
