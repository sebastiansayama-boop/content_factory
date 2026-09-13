# Repository Map

The repository is a functional cognitive environment, not a literal brain simulation.

```text
00_inbox
   ↓ classify
01_observation
   ↓ attend / select
02_memory ←──────────────┐
   ↕                     │
04_reasoning             │
   ↕                     │
03_working_context       │
   ↓                     │
05_decision              │
   ↓                     │
06_production            │
   ↓                     │
07_verification ─────────┘
   ↓
05_decision
   ↓
08_effects_feedback
   ↓
01_observation
   ↓
09_learning
   ├──→ 02_memory
   └──→ 04_reasoning

10_records observes and preserves the evolution of every zone.
model/ describes the current system.
docs/ explains and researches the system.
templates/ standardizes capture.
archive/ preserves superseded material without current authority.
```

## Control rules encoded by the map

1. Inbox is not truth.
2. Observation is not interpretation.
3. Working context is not durable memory.
4. Reasoning does not directly change the model.
5. Decisions authorize transitions; processes do not inherit authority implicitly.
6. Production creates revisions; verification evaluates them.
7. Acceptance and external effects are separate.
8. Effects return observations, not automatic knowledge updates.
9. Learning can propose changes to memory or reasoning, but promotion is explicit.
10. Records preserve history across the whole system.
