# 15 — System-Level Model

The repository should be understood one level above folders and object lifecycles: as a bounded cognitive-production system interacting with an external world.

This is a functional analogy, not a biological claim. Neuroscience increasingly describes cognition as distributed, interacting networks rather than isolated modules; internal and externally oriented networks dynamically cooperate and switch according to task and context. citeturn349193search1turn349193search3turn349193search8

## 1. The system boundary

```text
                    EXTERNAL WORLD
                         ↓
                 SIGNALS / SOURCES
                         ↓
┌───────────────────────────────────────────────┐
│              CONTENT FACTORY                  │
│                                               │
│  SENSE → ATTEND → MODEL → WORK → DECIDE     │
│                    ↓          ↓              │
│                  LEARN ← ACT / PRODUCE       │
│                    ↑          ↓              │
│                    └──── FEEDBACK             │
│                                               │
└───────────────────────────────────────────────┘
                         ↓
                 EXTERNAL EFFECTS
                         ↓
                    WORLD RESPONSE
                         ↺
```

The system therefore has two sides:

```text
WORLD SIDE
  what arrives
  what is observed
  what changes externally

SYSTEM SIDE
  what is remembered
  what is inferred
  what is selected
  what is produced
  what is learned
```

## 2. Six system-level functions

The repository is organized around six functions rather than around departments.

### S1 — Sensing

Purpose: receive candidate signals from the external world.

Repository zones:

```text
00_inbox/
01_observation/
```

Output:

```text
signal / source / observation / question
```

### S2 — World modelling

Purpose: maintain the system's current, reusable representation of what is known and unknown.

Repository zones:

```text
02_memory/
04_reasoning/
```

Output:

```text
claims / evidence / relations / hypotheses / knowledge revisions
```

The default-mode network literature is useful here only as a functional analogy: internally oriented cognition integrates incoming information with prior memories and knowledge to construct context-dependent models. citeturn349193search8turn349193search2

### S3 — Executive state

Purpose: maintain the active task context, compare possibilities and select the next authorized move.

Repository zones:

```text
03_working_context/
05_decision/
```

Output:

```text
bounded work item / decision / authorization
```

Large-scale executive-control networks are associated with cognitive control, working memory and task coordination. citeturn349193search3

### S4 — Action

Purpose: transform an authorized intention into an observable artifact or external effect.

Repository zones:

```text
06_production/
07_verification/
08_effects_feedback/
```

Output:

```text
asset / verification result / release / publication / external effect
```

The neuroscience analogy is action-oriented, not anatomical. Research on large-scale brain systems emphasizes interactions between sensing, prediction, action planning and feedback rather than a single isolated action module. citeturn349193search13turn349193search15

### S5 — Learning

Purpose: compare consequences with prior expectations and decide whether the system should update its knowledge, strategy or model.

Repository zone:

```text
09_learning/
```

Output:

```text
learning candidate / accepted learning / proposed model update / new research question
```

Prediction and error signals are central to several computational accounts of perception and learning, but these theories remain theoretical frameworks rather than a one-to-one mapping from brain function to software design. citeturn349193search12turn349193search6

### S6 — Continuity / identity

Purpose: preserve the system's history so that current state can be understood as the result of prior states rather than as an unexplained snapshot.

Repository zones:

```text
10_records/
model/
docs/
archive/
```

Output:

```text
current model + recoverable history + explicit superseded material
```

## 3. The actual system loop

The top-level loop is therefore:

```text
WORLD
  ↓
SENSE
  ↓
ATTEND
  ↓
MODEL
  ↓
WORK
  ↓
DECIDE
  ↓
ACT
  ↓
OBSERVE CONSEQUENCE
  ↓
LEARN
  ↺
MODEL
```

Editorial production is one particular action path inside this loop:

```text
WORLD
  ↓
SOURCE / SIGNAL
  ↓
EVIDENCE
  ↓
CLAIM
  ↓
KNOWLEDGE
  ↓
EDITORIAL INTENT
  ↓
CONTENT SPEC
  ↓
ASSET
  ↓
VERIFICATION
  ↓
ACCEPTANCE
  ↓
PUBLICATION
  ↓
OBSERVATION
  ↺
```

The editorial path must not be mistaken for the whole system.

## 4. Internal versus external truth

The system never controls the external world. It controls only:

```text
its representation of the world
its decisions
its produced artifacts
its authorized effects
its records of consequences
```

Therefore:

```text
MODEL ≠ WORLD
OBSERVATION ≠ INTERPRETATION
INTERPRETATION ≠ TRUTH
PUBLICATION ≠ OUTCOME
LEARNING ≠ FACT
```

## 5. The highest-level dependency structure

```text
ENVIRONMENT
    ↓
SIGNALS / SOURCES
    ↓
ATTENTION / TRIAGE
    ↓
MEMORY + CURRENT MODEL
    ↓
WORKING CONTEXT
    ↓
REASONING
    ↓
DECISION / AUTHORITY
    ↓
ACTION / PRODUCTION
    ↓
VERIFICATION
    ↓
EXTERNAL EFFECT
    ↓
OBSERVATION
    ↓
LEARNING
    ↓
MODEL UPDATE / NEW QUESTION
    ↺
```

Every lower-level repository transition should be explainable as part of one of these functions.

## 6. Why this level matters

At this level, folders are implementation surfaces of functions, not the architecture itself.

Therefore:

```text
new function
    ↓
ask which system-level capability is missing
    ↓
identify information boundary
    ↓
identify object lifecycle
    ↓
identify transition authority
    ↓
only then decide whether a new folder/state is required
```

This prevents folder-driven architecture.

## 7. Design conclusion

The current hypothesis is that `content_factory` is not fundamentally a content folder structure.

It is a bounded system for:

```text
SENSING
MODEL-BUILDING
WORKING-CONTEXT MANAGEMENT
DECISION
ACTION
VERIFICATION
FEEDBACK
LEARNING
CONTINUITY
```

The editorial workflow is one recurrent trajectory through those functions.
