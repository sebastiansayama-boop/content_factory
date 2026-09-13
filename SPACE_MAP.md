# Content Factory — Space Map

This is the primary navigation map for repository work.

Do not start from files. Locate the system situation first.

## 1. Top-level space

```text
                         CONTENT ECOSYSTEM
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
        STRATEGY / INTENT  AUDIENCE / MARKET  PRODUCT / BUSINESS
              │                 │                  │
              └─────────────────┼──────────────────┘
                                ▼
                         CONTENT FACTORY
                                │
          ┌─────────────────────┼──────────────────────┐
          ▼                     ▼                      ▼
      VALUE FLOW          FACTORY CONTROL       SEMANTIC SUBSTRATE
          │                     │                      │
          ▼                     │                      │
       INPUT                   WIP                    identity
          ↓                    capacity                revisions
      KNOWLEDGE               routing                  provenance
          ↓                    priority                dependencies
      EDITORIAL               scheduling               claims/evidence
          ↓                    ownership                structured content
     PRODUCTION               bottlenecks               reusable components
          ↓                     │                      │
      QUALITY                  │                      │
          ↓                     │                      │
    DISTRIBUTION  ←─────────────┘                      │
          ↓                                            │
    EXTERNAL EFFECT                                    │
          ↓                                            │
      LEARNING ────────────────────────────────────────┘
          │
          └────→ ecosystem / factory next cycle
```

## 2. Repository zones

```text
00_inbox/                    input and intake
01_observation/              observed signals/events/effects
02_memory/                   reusable evidence-backed knowledge
03_working_context/          active work item context
04_reasoning/                interpretation and comparison
05_decision/                 editorial and authority decisions
06_production/               production work and asset revisions
07_verification/             quality assessment
08_effects_feedback/         external effects and immediate feedback
09_learning/                 learning candidates and adaptation proposals
10_records/                  durable history
ontology/                    semantic domain model
model/                       current system model and machine-readable maps
docs/                        explanations and research
templates/                   capture contracts
archive/                     inactive historical material
```

## 3. Decision locator

```text
What is happening?                 → 01_observation
What do we know?                   → 02_memory
What work item is active?          → 03_working_context
How should evidence be interpreted?→ 04_reasoning
What should happen?                → 05_decision
How should it be made?             → 06_production
Does the result conform?           → 07_verification
What effect occurred?              → 08_effects_feedback
What was learned?                  → 09_learning
What happened historically?        → 10_records
What is the current system model?  → model/
What does a term mean?             → ontology/
Why does the model say this?       → docs/ + records
```

## 4. Five coordinates plus ecosystem level

For any significant item establish:

```text
ECOSYSTEM / FACTORY BOUNDARY
OBJECT
STATE / REVISION
EVIDENCE
DEPENDENCIES
AUTHORITY
NEXT LEGITIMATE TRANSITION
```

## 5. Core loops

Ecosystem:

```text
STRATEGY → DEMAND → FACTORY → EXPERIENCE → OUTCOME → STRATEGY
```

Factory:

```text
INPUT → KNOWLEDGE → EDITORIAL → PRODUCTION → QUALITY → DISTRIBUTION → LEARNING
```

Governance:

```text
STATE → REVIEW → DECISION → AUTHORIZED TRANSITION → STATE
```

## 6. Hard shortcuts to avoid

```text
request → production
production → knowledge
observation → learning truth
learning → strategy
verification → publication
acceptance → outcome
history → current authority
folder → authority
```

Each requires an explicit transition with evidence and appropriate authority.

## 7. Navigation question

Before changing the repository, answer:

```text
Which system is this problem in?
Is it ecosystem, factory, semantic, state, process or repository concern?
What object is involved?
Which revision?
What evidence?
Which dependencies?
Who has authority?
What transition is legitimate?
What record must remain recoverable?
```

See `docs/19_operator_navigation.md` for the full protocol.
