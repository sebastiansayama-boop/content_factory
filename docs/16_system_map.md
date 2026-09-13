# 16 — System Map

This is the highest-level working map for `content_factory`.

## 1. Ecosystem map

```text
                              CONTENT ECOSYSTEM
                                     │
             ┌───────────────────────┼────────────────────────┐
             ▼                       ▼                        ▼
      STRATEGY / INTENT       AUDIENCE / MARKET        PRODUCT / BUSINESS
             │                       │                        │
             └───────────────┬───────┴───────────────┬────────┘
                             ▼                       ▼
                       CONTENT DEMAND          PRODUCT CONTEXT
                             │                       │
                             └───────────┬───────────┘
                                         ▼
                                  CONTENT FACTORY
                                         │
                                         ▼
                                  CONTENT PRODUCTS
                                         │
                                         ▼
                                EXPERIENCE / CHANNEL
                                         │
                                         ▼
                                   RESPONSE / OUTCOME
                                         │
                                         ▼
                                   STRATEGY UPDATE
                                         ↺
```

## 2. Factory map

```text
                         CONTENT FACTORY
                                │
            ┌───────────────────┼────────────────────┐
            ▼                   ▼                    ▼
       STRATEGIC          FACTORY CONTROL      SEMANTIC SUBSTRATE
        INTENT               CONTROL PLANE
            │                   │                    │
            └───────────────────┼────────────────────┘
                                ▼
                           VALUE FLOW
                                │
             INPUT → KNOWLEDGE → EDITORIAL
                                ↓
                         PRODUCTION → QUALITY
                                ↓
                        DISTRIBUTION → EFFECT
                                ↓
                           LEARNING ↺
```

## 3. Factory value flow

```text
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
  ├──→ KNOWLEDGE
  ├──→ EDITORIAL
  └──→ PRODUCTION
```

The sequence is a value-flow projection, not a single global object lifecycle.

## 4. Factory control plane

Factory Control cuts across every value-flow stage:

```text
portfolio priority
intake
routing
WIP / queues
capacity
scheduling
ownership
service expectations
resource allocation
orchestration
bottleneck management
```

It controls flow around content work items. It does not become the source of content truth.

## 5. Shared semantic substrate

Every factory system can use the same semantic substrate:

```text
identity
revisions
structured content
knowledge graph
claims / evidence
provenance
dependencies
taxonomy / audience metadata
reusable components
```

This layer prevents each system from maintaining incompatible copies of meaning.

## 6. Repository projection

```text
REPOSITORY ZONE              SYSTEM FUNCTION

00_inbox/                    input / intake
01_observation/              observations and external signals
02_memory/                   reusable knowledge
03_working_context/          active work item context
04_reasoning/                interpretation and comparison
05_decision/                 editorial / authority decisions
06_production/               production work and asset revisions
07_verification/             quality assessment
08_effects_feedback/         external effects and immediate feedback
09_learning/                 learning candidates and adaptation proposals
10_records/                  durable history
model/                       current working model
ontology/                    semantic domain model
docs/                        explanations and research
templates/                   capture contracts
archive/                     inactive historical material
```

## 7. Control loops

### Ecosystem loop

```text
STRATEGY → DEMAND → FACTORY → EXPERIENCE → OUTCOME → STRATEGY
```

### Factory loop

```text
INPUT → KNOWLEDGE → EDITORIAL → PRODUCTION → QUALITY → DISTRIBUTION → LEARNING
```

### Governance loop

```text
STATE → REVIEW → DECISION → AUTHORIZED TRANSITION → STATE
```

### Semantic loop

```text
OBJECT → REVISION → PROVENANCE / DEPENDENCY → RESULT
```

## 8. Highest-level questions

For ecosystem questions:

```text
What outcome are we trying to create?
For whom?
Why does content matter to that outcome?
```

For factory questions:

```text
What work should enter?
What knowledge is needed?
What should we produce?
Can it advance?
How should it be released?
What did we learn?
```

For repository questions:

```text
Where is the object?
What is its identity and revision?
What evidence supports it?
What does it depend on?
Who has authority?
What is the next legitimate transition?
```

## 9. Integrity condition

The system is coherent when a material case can be traced:

```text
strategic context
→ input
→ knowledge
→ editorial decision
→ work item
→ production
→ verification
→ acceptance
→ release
→ external effect
→ observation
→ learning
→ updated decision / knowledge / strategy
```
