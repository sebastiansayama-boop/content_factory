# 16 — System Map

This is the highest-level working map for `content_factory`.

## 1. System map

```text
                              EXTERNAL WORLD
                                     │
                    ┌────────────────┴────────────────┐
                    ↓                                 ↑
              SIGNALS / SOURCES                 EFFECTS / RESPONSE
                    │                                 │
                    ↓                                 │
               [ SENSING ]                            │
                    │                                 │
                    ↓                                 │
          00_inbox → 01_observation                   │
                    │                                 │
                    ↓                                 │
               [ ATTENTION ]                          │
                    │                                 │
                    ↓                                 │
           candidate / research need                  │
                    │                                 │
                    ├──────────────┐                  │
                    ↓              ↓                  │
              [ MEMORY ]      [ REASONING ]           │
                    │              │                  │
                    │              ↓                  │
                    │       [ WORKING CONTEXT ]       │
                    │              │                  │
                    └──────────────┤                  │
                                   ↓                  │
                              [ DECISION ]            │
                                   │                  │
                                   ↓                  │
                              [ ACTION ]              │
                                   │                  │
                             production              │
                                   ↓                  │
                              [ VERIFY ]              │
                                   │                  │
                                   ↓                  │
                              [ EFFECT ] ─────────────┘
                                   │
                                   ↓
                              OBSERVATION
                                   │
                                   ↓
                              [ LEARNING ]
                                ↙       ↘
                         MEMORY UPDATE  NEW QUESTION
```

## 2. Repository projection

```text
SYSTEM FUNCTION        REPOSITORY ZONES

SENSING                00_inbox/
                       01_observation/

MEMORY                 02_memory/

WORK                   03_working_context/

REASONING              04_reasoning/

DECISION               05_decision/

ACTION                 06_production/

VERIFICATION           07_verification/

EFFECT / FEEDBACK      08_effects_feedback/

LEARNING               09_learning/

CONTINUITY             10_records/

CURRENT MODEL          model/
EXPLANATION            docs/
CAPTURE CONTRACTS      templates/
INACTIVE HISTORY       archive/
```

## 3. Three planes

The repository can also be understood as three intersecting planes.

### Plane A — Information

```text
observation
→ evidence
→ claim
→ knowledge
→ specification
→ asset
→ publication
→ observation
```

### Plane B — Control

```text
identity
→ state
→ authority
→ review
→ decision
→ effect
```

### Plane C — Time

```text
past/history
→ current state
→ expected/future state
→ consequence
→ learning
```

A valid design must survive all three planes simultaneously.

## 4. Core feedback loops

The system has multiple loops, not one loop.

### Perception loop

```text
WORLD → SIGNAL → OBSERVATION → MODEL
```

### Production loop

```text
MODEL → DECISION → ACTION → VERIFICATION → EFFECT
```

### Learning loop

```text
EFFECT → OBSERVATION → INTERPRETATION → LEARNING → MODEL
```

### Governance loop

```text
STATE → REVIEW → DECISION → AUTHORIZED TRANSITION → STATE
```

### Memory loop

```text
CURRENT STATE → RECORD → REVISION → CURRENT STATE
```

## 5. The repository as a cognitive environment

No folder owns the whole system.

A function is complete only when its downstream and feedback relationships are preserved.

For example:

```text
production without verification
    = action without error feedback

memory without current-state projection
    = history without usable present state

reasoning without decision boundary
    = interpretation without controlled action

learning without evidence
    = adaptation without grounding

observation without provenance
    = signal without recoverable meaning
```

## 6. System-level invariant

The repository should always permit a reader to answer:

```text
What entered the system?
What did we believe or know at the time?
What changed internally?
Who or what authorized the change?
What exact effect occurred?
What happened afterward?
What was learned?
What changed in the model as a result?
```

If the repository cannot answer one of these questions for a material case, the structure is incomplete.

## 7. Boundary rule

The system boundary is not `content_factory/` versus the Internet.

The meaningful boundary is:

```text
uncontrolled external world
        ↓
observed information
        ↓
controlled internal representation
        ↓
authorized action
        ↓
observable external effect
```

This is the central architectural boundary for future cases.
