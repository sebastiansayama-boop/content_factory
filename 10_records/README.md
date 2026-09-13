# 10 — Records

Durable append-only history and provenance.

## Purpose

`10_records` is the historical reconstruction layer. It preserves material events, decisions, revisions, experiments and superseded states so that current state can be understood as a projection over history.

## Minimum record envelope

Every material record should expose, at minimum:

```text
record_id
record_type
occurred_at
recorded_at
subject_refs
actor_or_executor
source_refs
caused_by_refs
result_refs
revision_refs
status
provenance
```

The exact payload depends on the record type. Do not flatten distinct events, decisions, observations and artifacts into one semantic object merely for storage convenience.

## What belongs here

- case timelines
- decision records
- revision history
- experiment outcomes
- material execution events
- effect records and their references
- superseded model snapshots
- provenance chains
- explicit discard, rejection, cancellation and failure events

## Append-only rule

Historical records are not rewritten to hide an earlier state. Corrections are represented by a new record or revision linked to the prior state.

```text
old record
   ↓
correction / supersession record
   ↓
current projection
```

## Reconstruction requirement

A material case should be traceable across the relevant boundaries:

```text
sensing / intake
→ modelling / context
→ reasoning
→ decision
→ production
→ verification
→ action / effect
→ observation
→ learning
```

Not every case uses every zone, but skipped boundaries must be explainable rather than silently omitted.

## Relationship to current state

`10_records` is history, not the current working model. Current state may be projected from records, but a projection must not rewrite the historical evidence from which it was derived.

## Invariants

- History remains reconstructable.
- Supersession is explicit.
- Provenance, dependency and impact remain distinguishable.
- Historical authority is not automatically current authority.
- Unknown outcomes remain unknown.
- Records do not manufacture evidence that was never observed.

## Completion criterion

A material case is sufficiently recorded when an independent reader can reconstruct the relevant path, revisions, decisions, effects and uncertainties without relying on hidden chat state.