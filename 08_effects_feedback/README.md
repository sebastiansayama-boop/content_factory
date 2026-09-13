# 08 — Effects and Feedback

External effects and the observations that follow them.

## Purpose

Record actions crossing the repository boundary and their immediate boundary outcomes. Do not treat an external effect as a later consequence, audience response, or business outcome.

## Minimum effect record

```text
effect_id
work_item_id
asset_revision_id
decision_or_authority_ref
effect_type
target_ref
provider_or_channel_ref
requested_at
executed_at
external_reference
status
result_summary
provenance
```

Typical effect types are `RELEASE`, `PUBLICATION`, `DELIVERY`, `UPDATE`, `UNPUBLISH` and `RETIREMENT`.

## Boundary

```text
authorized decision
→ external action
→ effect record
→ later observation
→ learning
```

A publication record establishes publication only to the extent supported by evidence. It does not establish audience response or business outcome.

## Status

External operations must distinguish at least `REQUESTED`, `SUCCEEDED`, `FAILED`, `PARTIAL` and `UNKNOWN`. `UNKNOWN` remains unknown until evidence establishes the final state.

## Observation boundary

Only a genuinely externally observable effect may produce an observation. A dry run, simulated publisher or local test is not evidence of a real-world effect.

## Invariants

- Authorization is linked to the effect.
- The exact asset revision is identified.
- Internal execution is distinct from external consequence.
- Publication is distinct from outcome.
- Simulated effects are explicitly marked as simulated.
- Later observations remain separate records.

## Completion criterion

An effect is sufficiently recorded when its authorized target, exact revision, external boundary, status and external reference, when available, are reconstructable.

The detailed operating contract is retained in `OPERATING_CONTRACT.md` as the companion specification.