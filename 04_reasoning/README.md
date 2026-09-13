# 04 — Reasoning

Explicit synthesis, comparison, contradiction analysis and hypotheses.

## Purpose

`04_reasoning` records the analytical work performed between evidence and a decision or learning proposal. It makes interpretation inspectable instead of hiding it inside a final answer.

## Minimum reasoning record

```text
reasoning_id
question_or_problem
input_refs
evidence_refs
method_or_comparison_basis
analysis
alternatives_considered
contradictions
uncertainties
conclusion
confidence
created_at
author_or_executor
```

The record should make it possible to distinguish source material from the interpretation derived from it.

## Allowed reasoning types

- synthesis of multiple observations
- comparison of alternatives
- contradiction analysis
- causal hypothesis
- interpretation of feedback
- risk analysis
- research reconciliation
- decision preparation

## Decision boundary

Reasoning may recommend a decision, but it does not itself create authority.

```text
EVIDENCE
  ↓
REASONING
  ↓
DECISION
```

A reasoning conclusion must not be rewritten later as if it were an original observation.

## Model boundary

Reasoning may identify a model problem, but a change to `model/` requires a separate traceable decision and the repository protocol. Reasoning alone does not mutate the working model.

## Allowed exits

```text
reasoning → decision
reasoning → learning candidate
reasoning → research record
reasoning → explicit unresolved question
```

## Invariants

- Evidence and interpretation remain distinguishable.
- Alternatives and meaningful contradictions are not silently omitted.
- Unknowns remain explicit.
- A confidence statement does not create authority.
- External research findings are reconciled against the current repository rather than copied as truth.

## Completion criterion

A reasoning record is complete when the question, evidence, analytical method, alternatives or contradictions, conclusion and remaining uncertainty are reconstructable.