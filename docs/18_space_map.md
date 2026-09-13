# 18 — Space Map

This map is the primary semantic navigation instrument for `content_factory`.

The repository is a bounded model of a larger Content Ecosystem and, within it, a Content Factory.

## 1. Highest-level space

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
    │   INPUT
    │   → KNOWLEDGE
    │   → EDITORIAL
    │   → PRODUCTION
    │   → QUALITY
    │   → DISTRIBUTION
    │   → LEARNING
    │
    ├── FACTORY CONTROL
    │   priority / routing / WIP / capacity / scheduling /
    │   ownership / orchestration / bottlenecks
    │
    └── SEMANTIC SUBSTRATE
        identity / revisions / provenance / dependencies /
        evidence / claims / structured content / reusable components
```

## 2. Space dimensions

Every significant item should be locatable on:

```text
SYSTEM LEVEL
  ecosystem / factory / repository

OBJECT
  what kind of thing is it?

STATE / REVISION
  what lifecycle condition and exact revision?

EPISTEMIC POSITION
  observed / supported / derived / interpreted / decided / unknown

DEPENDENCIES
  what must remain valid?

AUTHORITY
  what may it cause?

TIME
  historical / current / proposed / superseded
```

## 3. Primary repository spaces

```text
S1  00_inbox/             demand and unclassified input
S2  01_observation/       observed external signals/effects
S3  02_memory/            reusable evidence-backed knowledge
S4  03_working_context/   active work item context
S5  04_reasoning/         interpretation and comparison
S6  05_decision/          authority-bearing decisions
S7  06_production/        production work and revisions
S8  07_verification/      conformity assessment
S9  08_effects_feedback/  external effects and immediate feedback
S10 09_learning/          learning candidates and adaptation proposals
S11 10_records/           durable history
S12 ontology/             semantic domain model
S13 model/                current system model
S14 docs/                 explanations and research
S15 templates/            capture contracts
S16 archive/              inactive historical material
```

## 4. Factory routing

```text
incoming demand
→ INPUT
→ candidate / research need / opportunity

knowledge need
→ KNOWLEDGE

what should be made?
→ EDITORIAL

how should it be made?
→ PRODUCTION

does it conform?
→ QUALITY

how does it leave the factory?
→ DISTRIBUTION

what happened afterward?
→ LEARNING
```

## 5. Control-plane routing

Factory Control is not one repository folder. It is a cross-cutting operating function.

```text
priority
→ 05_decision / strategy records
routing
→ working context / production plans
WIP
→ records / flow metrics
capacity
→ records / capability data
scheduling
→ work item planning
ownership
→ decisions / work items
orchestration
→ process / transition records
bottlenecks
→ flow analysis / records
```

Implementation can later project these into dedicated operational storage without changing the conceptual boundary.

## 6. Semantic substrate routing

The shared semantic substrate is also cross-cutting:

```text
identity / revision
→ object models
provenance
→ records / evidence bindings
dependency
→ dependency model
claims / evidence
→ memory / ontology
structured content
→ production models
reusable components
→ production library
```

## 7. Decision navigation

```text
What outcome are we trying to create?
→ STRATEGY / ECOSYSTEM

What does the audience or market indicate?
→ AUDIENCE / MARKET

What work should enter the factory?
→ INPUT + FACTORY CONTROL

What do we know?
→ KNOWLEDGE / MEMORY

What should be made?
→ EDITORIAL

How should it be made?
→ PRODUCTION

Can it advance?
→ QUALITY

Can it leave the factory?
→ DISTRIBUTION

What happened?
→ EFFECTS / OBSERVATION

What changed?
→ LEARNING

Where did the current model come from?
→ RECORDS / DOCS / RESEARCH
```

## 8. Forbidden shortcuts

```text
request → production
production → knowledge truth
metric → strategy truth
learning → accepted policy
observation → interpretation
verification → publication
acceptance → outcome
history → current authority
folder → authority
```

## 9. Navigation invariant

Use:

```text
SYSTEM LEVEL
→ OBJECT
→ STATE / REVISION
→ EVIDENCE
→ DEPENDENCIES
→ AUTHORITY
→ NEXT LEGITIMATE TRANSITION
→ REQUIRED RECORD
```

before deciding which file or folder to change.
