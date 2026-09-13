# 09 — Learning

Interpret observations and determine whether they justify future changes.

## Purpose

`09_learning` is the interpretation layer for experience. It asks what an observation means for future behavior and whether the evidence is strong enough to justify a change.

## Minimum learning record

```text
learning_id
observation_refs
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

## Core rule

```text
observation
    ↓
interpretation
    ↓
learning candidate
    ↓
explicit decision
    ↓
knowledge / process / model update
```

A metric is not automatically learning. A learning candidate is not automatically knowledge. A learning outcome is not automatically strategy.

## Required separation

The record should distinguish:

- what was observed;
- what interpretation was proposed;
- what alternatives were considered;
- what remains unknown;
- what change is proposed;
- what authority is required to make that change.

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

## Completion criterion

A learning record is complete when the triggering observations, interpretation, competing explanations, uncertainty and proposed consequence are reconstructable.