# 01 — Observation

Observed signals kept separate from interpretation.

## Purpose

`01_observation` records what was observed about the world, a source, a system, an audience, a production process or an external effect. It answers **what happened or was detected**, not why it happened.

## Allowed input

- direct measurements
- observed events or changes
- source notifications
- audience or market signals
- operational observations
- factual corrections received from a source
- externally observable effects

An observation may originate from an inbox item, verification result, external system, human report or instrument.

## Minimum observation record

```text
observation_id
observed_at
observer_or_source
subject_ref
observation_type
observed_fact
source_ref_or_evidence_ref
confidence_or_uncertainty
related_work_item_ref
provenance
```

The record should preserve the observation as close as practical to the observed signal. If interpretation is necessary, store it separately in `04_reasoning` or `09_learning`.

## Boundary

Observation is not:

```text
observation ≠ explanation
observation ≠ claim truth
observation ≠ decision
observation ≠ learning
```

A verification failure is an observation about a revision; it does not by itself determine the editorial decision.

## Allowed exits

```text
OBSERVATION
  ├─→ reasoning / interpretation
  ├─→ memory candidate when evidence supports durable reuse
  ├─→ learning analysis
  └─→ records as part of a reconstructable case
```

Promotion to memory or learning requires an explicit semantic step; the folder transition itself grants no authority.

## Invariants

- Record what was observed, including uncertainty.
- Preserve source and time where material.
- Keep interpretation outside the observation record.
- Do not rewrite an observation to make a later conclusion appear to have been observed originally.
- External effect and subsequent observation remain separate records.

## Completion criterion

An observation is usable when another reader can identify what was observed, when, by whom or by what source, and what evidence supports the observation.

This README defines the zone contract, not a claim that every observation is verified truth.