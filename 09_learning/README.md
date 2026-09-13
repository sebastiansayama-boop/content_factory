# 09 — Learning

Interpret observations and determine whether they justify future changes.

## Purpose

`09_learning` is the interpretation layer for experience. It asks what an observation means for future behavior and whether the evidence is strong enough to justify a change.

## Minimum learning record

```text
learning_id
observation_refs
experiment_refs
question_or_trigger
interpretation
evidence_refs
alternative_explanations
uncertainties
learning_status
proposed_change
impact_scope
created_at
actor_or_executor
```

## Learning statuses

```text
CANDIDATE
SUPPORTED
REJECTED
INCONCLUSIVE
PROMOTED
SUPERSEDED
```

The status describes the learning proposition, not the truth of every observation from which it was derived.

## Core learning transition

```text
question / hypothesis
    ↓
experiment / observation
    ↓
result
    ↓
evidence
    ↓
interpretation
    ↓
lesson / learning candidate
    ↓
explicit decision
    ↓
knowledge / process / model update
```

A metric is not automatically learning. A learning candidate is not automatically knowledge. A learning outcome is not automatically strategy.

Both failed and successful outcomes are eligible for learning. Unexpected success should be examined before being treated as a reusable pattern.

## Required separation

The record should distinguish:

- what was observed;
- whether the observation came from an experiment or production case;
- what interpretation was proposed;
- what alternatives were considered;
- what remains unknown;
- what change is proposed;
- what authority is required to make that change.

## Creative learning

Creative experiments use the same evidence discipline while preserving creative-specific context.

Where relevant, record:

```text
creative_question
context
reference_or_input
experiment_or_treatment
observed_effect
successful_pattern_or_failure
reusable_candidate
uncertainty
examples
evidence_refs
confidence
```

A successful creative result remains a context-bound learning candidate until repeated evidence or an explicit decision supports promotion.

## Allowed exits

```text
learning → decision
learning → new experiment
learning → knowledge update candidate
learning → model update candidate
learning → no-change conclusion
```

A learning record may recommend a model change but cannot silently modify `model/`.

## Invariants

- Observation precedes interpretation.
- Evidence and interpretation remain distinguishable.
- Uncertainty is retained.
- Rejected learning remains discoverable when material.
- Strategy changes require an explicit boundary decision outside this zone.
- Creative success is not automatically knowledge.
- Learning does not silently mutate architecture or ontology.

## Completion criterion

A learning record is complete when the triggering observations or experiments, result, interpretation, competing explanations, uncertainty and proposed consequence are reconstructable.
