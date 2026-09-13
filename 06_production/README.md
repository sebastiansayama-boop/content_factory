# 06 — Production

Transformation of approved knowledge plus a bounded specification into a concrete asset revision.

## Purpose

`06_production` records the creation or transformation of a concrete content asset. Production changes representation into an output revision; it must remain bound to the inputs and specification that authorized the work.

## Minimum production record

```text
production_id
work_item_id
operation_id
asset_id
output_revision_id
input_refs
knowledge_basis_refs
specification_ref
capability_id
executor_ref
provider_ref_or_execution_ref
started_at
completed_at
result_ref
production_status
```

Provider and executor identifiers may be recorded for provenance. Secret values must never be stored here.

## Production boundary

Production may transform representation, but it may not silently introduce unsupported factual claims.

```text
approved basis + bounded specification
            ↓
         production
            ↓
       asset revision
```

An execution result is not automatically accepted content.

## Failure semantics

A production attempt should distinguish at least:

```text
SUCCEEDED
FAILED
PARTIAL
CANCELLED
UNKNOWN
```

`UNKNOWN` is used when the system cannot establish whether an external or asynchronous operation completed. It must not be rewritten as success without evidence.

## Revision identity

Every meaningful production output must be tied to an identifiable asset revision. If a later production attempt changes the asset, it creates or identifies a new revision rather than mutating the history of an earlier result.

## Allowed exits

```text
production → verification
production → failure/rework
production → explicit hold
```

Production does not itself authorize publication.

## Invariants

- Input basis and specification are reconstructable.
- Output revision identity is explicit.
- Execution capability is not treated as authority.
- Unsupported factual additions are not silently accepted.
- Failed or unknown execution is preserved as such.

## Completion criterion

A production record is complete when the exact output revision, input basis, specification, execution identity and result status can be reconstructed and handed to verification.