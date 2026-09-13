# Content Factory — Space Map

This is the primary navigation map for repository work.

Do not start from files. Locate the situation in the space first.

```text
                           EXTERNAL WORLD
                                │
             ┌──────────────────┴──────────────────┐
             │                                     │
          INCOMING                             CONSEQUENCES
             │                                     ▲
             ▼                                     │
        00_inbox                                   │
             │                                     │
             ▼                                     │
      01_observation                                │
             │                                     │
       ┌─────┴─────┐                               │
       ▼           ▼                               │
  02_memory   03_working_context                   │
       ↕           ↕                               │
       └─────┬─────┘                               │
             ▼                                     │
       04_reasoning                                │
             │                                     │
             ▼                                     │
       05_decision                                 │
             │                                     │
             ▼                                     │
       06_production                               │
             │                                     │
             ▼                                     │
       07_verification ───────────────→ 05_decision
                                             │
                                             ▼
                                      08_effects_feedback
                                             │
                                             ▼
                                      01_observation
                                             │
                                             ▼
                                      09_learning
                                         ↙      ↘
                                    02_memory  04_reasoning

10_records = history of the whole space
model/     = current model of the space
docs/      = explanations/research about the space
templates/ = capture interfaces
archive/   = inactive historical space
```

## Decision locator

```text
What is happening?             → 01_observation
What do we know?               → 02_memory
What am I currently working on?→ 03_working_context
How should it be interpreted?  → 04_reasoning
What should we do?             → 05_decision
How do we make it?             → 06_production
Does the result conform?       → 07_verification
Did we affect the world?       → 08_effects_feedback
What did we learn?             → 09_learning
Why/when did this happen?      → 10_records
What does the system currently believe? → model/
Why does the model say this?   → docs/ + records
```

## Five coordinates of any important item

```text
OBJECT
STATE / REVISION
EVIDENCE
DEPENDENCIES
AUTHORITY
```

Then determine the next legitimate transition.

## Core loop

```text
WORLD
→ OBSERVE
→ REPRESENT
→ REASON
→ DECIDE
→ ACT
→ VERIFY
→ EFFECT
→ OBSERVE
→ LEARN
→ REPRESENT
```

## Hard shortcuts to avoid

```text
observation ≠ interpretation
interpretation ≠ decision
decision ≠ effect
production ≠ truth
verification ≠ acceptance
acceptance ≠ publication
history ≠ current model
learning ≠ knowledge truth
```

For the full navigation protocol, see `docs/19_operator_navigation.md`.
