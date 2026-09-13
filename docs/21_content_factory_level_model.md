# 21 — Content Factory Level Model

This document defines the current candidate architecture of the `Content Factory` as a functional production subsystem inside a larger `Content Ecosystem`.

## 1. Boundary

```text
CONTENT ECOSYSTEM
│
├── STRATEGY / INTENT
├── AUDIENCE / MARKET
├── PRODUCT / BUSINESS
│
└── CONTENT FACTORY
    │
    ├── VALUE FLOW
    ├── FACTORY CONTROL
    └── SHARED SEMANTIC SUBSTRATE
```

Strategy / Portfolio Intent is therefore **upstream of the factory**, not a sequential factory stage.

## 2. Factory architecture

```text
                         CONTENT FACTORY
                                │
        ┌───────────────────────┼────────────────────────┐
        │                       │                        │
        ▼                       ▼                        ▼
   VALUE / FLOW          FACTORY CONTROL          SHARED SUBSTRATE
        │                       │                        │
        │                priority / routing       content graph
        │                WIP / queues             provenance
        │                capacity / scheduling    identity / revisions
        │                ownership / SLA          dependencies
        │                orchestration            reusable components
        │                bottleneck management    evidence / claims
        │                       │                        │
        └───────────────────────┼────────────────────────┘
                                │
                                ▼
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
                                ↺
```

The seven systems are the value-flow backbone. Factory Control is a cross-cutting control plane. Shared Semantic Substrate is a cross-cutting meaning/provenance layer.

## 3. Factory input boundary

The factory accepts bounded inputs from the ecosystem:

```text
strategic demand
+
audience / market context
+
source / evidence-backed knowledge
+
requests / signals / observations
```

The factory does not automatically accept every incoming signal as production demand.

## 4. Input System

```text
signal / source / request / observation
        ↓
 capture → classify → normalize → triage → route
```

Output may be:

```text
work candidate
research need
editorial opportunity
hold / reject
```

## 5. Knowledge System

```text
research
→ source
→ evidence
→ claim
→ context / relation
→ knowledge revision
```

The Knowledge System provides reusable evidence-bearing memory for multiple work items.

## 6. Editorial System

```text
opportunity
→ audience + objective
→ priority
→ editorial decision
→ content specification
```

The specification is a bounded production contract.

## 7. Production System

Production is a capability network:

```text
content specification
→ capability selection
→ production
→ asset revision
→ channel adaptation
```

Capabilities may include text, image, video, audio, localization, design, research assistance and data visualization.

## 8. Quality System

```text
production result
→ verification
→ review / revision
→ acceptance
→ release eligibility
```

Verification is a conformity assessment. Acceptance is an authority-bearing decision.

## 9. Distribution System

```text
accepted revisions
→ release bundle
→ channel configuration / adaptation
→ authorization
→ publish / deliver
→ external effect
```

A release may bundle multiple dependent revisions.

## 10. Learning System

```text
external effect
→ observation
→ measurement
→ interpretation
→ experiment / decision
→ learning
→ knowledge / editorial / production update
```

Learning is not automatically truth.

## 11. Work item

The primary flow unit is a bounded `Content Work Item` / `Work Package`.

```text
WORK ITEM
├── work_item_id
├── strategic_intent_ref
├── audience_context_ref
├── objective
├── requested_outcome
├── inputs
├── knowledge_basis
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

One work item can produce multiple asset revisions. One release can contain multiple work-item outputs.

## 12. Factory Control

Factory Control operates across the whole value flow:

```text
priority
intake / routing
WIP / queues
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

Factory Control does not determine content truth.

## 13. Shared Semantic Substrate

```text
structured content
knowledge graph
identity
revisions
claims / evidence
provenance
dependencies
audience / taxonomy metadata
reusable components
```

This layer lets systems share meaning without uncontrolled copies.

## 14. Flow geometry

The factory is not a single linear pipeline.

```text
KNOWLEDGE
   ↙   ↓   ↘
product-A product-B product-C
    ↘  ↓  ↙
   shared learning

REQUESTS → WORK ITEMS → CAPABILITIES → RELEASES → EFFECTS
                 ↑             │
                 │             └── dependencies
                 │
           FACTORY CONTROL
```

## 15. Factory metrics

### Flow

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

### Quality / governance

```text
verification failures
revision count
acceptance rate
factual corrections
policy exceptions
dependency invalidations
publication incidents
```

### Outcomes

```text
audience response
retention / engagement where meaningful
conversion / product outcome
experiment results
reuse rate
content decay / retirement
```

Metrics must answer management questions. Volume is not inherently success.

## 16. Control principles

1. Pull work through the factory from real demand and available capacity.
2. Limit WIP at constraining stages.
3. Route by capability, risk, dependencies and constraints.
4. Reuse semantic content where meanings are shared.
5. Bind verification and acceptance to exact revisions.
6. Use release bundles where a common readiness boundary exists.
7. Automate repeatable bounded work; escalate ambiguous or consequential decisions.
8. Treat bottleneck management as continuous.
9. Preserve provenance and dependencies through every transformation.
10. Do not optimize local utilization at the expense of overall flow.

## 17. Status

`candidate / research-derived`

The factory architecture must be validated against real work items and cases before implementation hardening.
