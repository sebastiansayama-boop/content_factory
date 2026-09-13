# 18 — Space Map

This map is the primary navigation instrument for working in `content_factory`.

The repository is treated as a bounded information space. A decision is made by locating the current situation in that space before choosing an operation.

## 1. The highest-level space

```text
                         EXTERNAL WORLD
                              │
                ┌─────────────┴─────────────┐
                │                           │
             INCOMING                   CONSEQUENCES
                │                           ▲
                ▼                           │
        [1] PERCEPTION / INTAKE             │
                │                           │
                ▼                           │
        [2] OBSERVATION                     │
                │                           │
        ┌───────┴────────┐                  │
        ▼                ▼                  │
 [3] MEMORY          [4] WORKING            │
                      CONTEXT               │
        │                │                  │
        └───────┬────────┘                  │
                ▼                           │
          [5] REASONING                     │
                │                           │
                ▼                           │
          [6] DECISION                      │
                │                           │
                ▼                           │
          [7] ACTION / PRODUCTION           │
                │                           │
                ▼                           │
          [8] VERIFICATION                  │
                │                           │
                ▼                           │
          [6] DECISION                      │
                │                           │
                ▼                           │
          [9] EXTERNAL EFFECT ──────────────┘
                │
                ▼
          [10] LEARNING
             │       │
             ├───────┘
             ▼
           MEMORY / MODEL
```

The numbers describe functional regions, not implementation modules.

## 2. The five dimensions of the space

Every significant repository item should be locatable on five dimensions.

### A. Object

What kind of thing is it?

```text
signal
question
candidate
source
evidence
claim
knowledge revision
research requirement
editorial decision
content specification revision
asset revision
verification result
release
publication
observation
learning
model change
decision record
```

### B. State

What is its current lifecycle state?

State is object-specific. Do not infer it from folder names.

### C. Time

Where is it in relation to change?

```text
past / historical
current
proposed / future
superseded
unknown
```

### D. Epistemic status

How strongly do we know it?

```text
observed
supported
interpreted
hypothesized
accepted
unknown
invalidated
```

### E. Authority

What may this item cause?

```text
information only
working context
proposal
decision
authorized internal transition
authorized external effect
```

These dimensions must not be collapsed.

## 3. Primary spaces

### Space S0 — Outside world

Anything not controlled by the repository.

The repository may observe it, but does not own its truth or future behavior.

Examples:

- external sources;
- audience behavior;
- platform responses;
- new events;
- new evidence.

### Space S1 — Intake

`00_inbox/`

Unclassified incoming material.

The only safe assumption is: "this exists and has entered the workspace."

### Space S2 — Observation

`01_observation/`

Things the system has actually observed and recorded.

Observation must not contain conclusions that were not observed.

### Space S3 — Memory

`02_memory/`

Reusable information with provenance.

This is where source/evidence/claim/knowledge relations accumulate.

### Space S4 — Working context

`03_working_context/`

Temporary material selected for one active problem.

It is disposable unless explicitly promoted elsewhere.

### Space S5 — Reasoning

`04_reasoning/`

Interpretation, comparison, contradiction analysis, hypotheses and case synthesis.

Reasoning proposes; it does not silently authorize.

### Space S6 — Decision

`05_decision/`

Authority-bearing choices about what the system should do next.

A decision must identify its target, revision, evidence and scope.

### Space S7 — Production

`06_production/`

Transformation of approved inputs into a concrete representation.

Production changes representations; it does not silently rewrite knowledge.

### Space S8 — Verification

`07_verification/`

Checks whether a concrete result matches its specification, evidence and constraints.

Verification produces an assessment, not automatic acceptance.

### Space S9 — Effects and feedback

`08_effects_feedback/`

External actions and their immediate consequences.

This is the boundary where the system stops merely reasoning and changes the outside world.

### Space S10 — Learning

`09_learning/`

Interpretations of consequences that may change future behavior or knowledge.

Learning is a proposal until explicitly promoted.

### Space S11 — Records

`10_records/`

Durable history of transitions, decisions, evidence bindings, revisions and case timelines.

Records observe the whole system; they are not an alternate current state.

### Space S12 — Current model

`model/`

The current working theory of how the system behaves.

It is not raw evidence and not a history store.

### Space S13 — Explanation and research

`docs/`

Human-readable explanations, synthesis and external comparisons.

### Space S14 — Capture interfaces

`templates/`

Contracts for creating new cases, decisions, experiments and research records consistently.

### Space S15 — Inactive space

`archive/`

Superseded or inactive material with no current authority.

## 4. Spatial navigation rule

When deciding what to do with an item, ask in this order:

```text
1. Where is it now?
2. What object is it?
3. What state is it in?
4. What evidence supports it?
5. What does it depend on?
6. What authority does it have?
7. What transition is being considered?
8. What new state would result?
9. What record must be created?
```

This is the default decision procedure for repository work.

## 5. Transition geometry

The system should be thought of as a graph of controlled transitions rather than a straight pipeline.

```text
INBOX
  ↓ classify
OBSERVATION
  ↓ select / extract
MEMORY ←──────────────┐
  ↕                   │
WORKING CONTEXT       │
  ↕                   │
REASONING             │
  ↓                   │
DECISION ─────────────┤
  ↓                   │
PRODUCTION             │
  ↓                   │
VERIFICATION ─────────┘
  ↓
DECISION
  ↓
EFFECT
  ↓
OBSERVATION
  ↓
LEARNING
  ├────────────→ MEMORY
  └────────────→ REASONING / MODEL CHANGE
```

## 6. Decision navigation

For any requested change, choose the smallest sufficient route.

```text
Question about reality?
→ OBSERVATION / RESEARCH

Question about what is known?
→ MEMORY

Question about how to interpret evidence?
→ REASONING

Question about what should happen?
→ DECISION

Question about how to make something?
→ PRODUCTION

Question about whether a result conforms?
→ VERIFICATION

Question about changing the external world?
→ EFFECT / AUTHORITY

Question about what was learned?
→ LEARNING

Question about what the repository currently believes?
→ MODEL

Question about why we believe it?
→ RECORDS / RESEARCH / DECISIONS
```

## 7. Forbidden shortcuts

The following spatial jumps are invalid by default:

```text
INBOX → MODEL
REASONING → MODEL
PRODUCTION → KNOWLEDGE
VERIFICATION → PUBLICATION
OBSERVATION → LEARNING
LEARNING → KNOWLEDGE
HISTORY → CURRENT AUTHORITY
```

Each requires an explicit transition with appropriate evidence and authority.

## 8. Repository navigation state

At the beginning of meaningful work, the operator should be able to establish this compact map:

```text
CURRENT MODEL:
UNKNOWN / ASSUMED / CHANGED:
ACTIVE CASE:
ACTIVE OBJECTS:
CURRENT REVISIONS:
OPEN DECISIONS:
KNOWN DEPENDENCIES:
KNOWN INVALIDATIONS:
CURRENT UNKNOWNs:
RECENT OBSERVATIONS:
AVAILABLE EFFECTS:
NEXT LEGITIMATE TRANSITIONS:
```

This is the minimum situational awareness required before making a structural change.

## 9. Why this map exists

The map exists to reduce repository-wide re-reading and prevent local optimization.

A local file edit is correct only when its position in the larger space is understood.

The repository should therefore be navigable as:

```text
SPACE → OBJECT → STATE → EVIDENCE → AUTHORITY → TRANSITION
```

rather than:

```text
FILE → EDIT
```
