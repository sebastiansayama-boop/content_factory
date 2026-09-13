# Q21 Work Item — Consume MEM-001 in a Bounded Provider Evaluation

Date: 2026-09-13
Work item ID: WI-2026-09-13-001
Revision ID: WI-2026-09-13-001-r1
Status: COMPLETED

## Objective

Test whether promoted memory is actually consumed by later work and changes a decision, rather than merely being cited.

## Bounded task

Evaluate the recovery posture of a concrete GitHub Contents API file create/update interaction using the already completed Q12 research as the provider-specific evidence base.

No GitHub mutation is performed by this work item.

## Knowledge basis

Primary reusable memory:

- `02_memory/2026-09-13-memory-001-idempotency-vs-correlation.md`
- revision `MEM-2026-09-13-001-r1`

Supporting provider evidence:

- `10_records/2026-09-13-external-system-q12-github-mutation-identity-matrix.md`
- `10_records/2026-09-13-external-system-q13-factory-identity-provenance-research.md`

## Question

Does the existence of a resulting file/blob SHA and generated commit SHA justify classifying an ambiguous Contents API mutation as automatically recoverable?

## Pre-memory decision hypothesis

If the later work considered only the provider result identities documented by Q12, it could be tempting to classify the operation as strongly reconcilable and therefore suitable for automatic recovery after comparing the resulting file state.

This is a counterfactual baseline for the Q21 test, not a claim that this decision was actually adopted.

## Memory-informed analysis

MEM-001 requires correlation/operation identity to remain distinct from duplicate-safe retry semantics. Q12 states that Contents mutations expose resulting file/blob and commit identities, require the current file blob SHA for updates, but do not expose a documented generic mutation-operation ID or idempotency key.

Therefore the observed result identities establish useful external state/revision evidence but do not, by themselves, establish duplicate-safe retry semantics.

## Decision-changing effect

Without MEM-001, the provider's result identities could be treated as sufficient evidence for a stronger recovery posture.

With MEM-001, the decision is narrowed:

`DO NOT CLASSIFY AMBIGUOUS CONTENTS MUTATION AS AUTOMATICALLY RECOVERABLE SOLELY FROM FILE/BLOB/COMMIT IDENTITY.`

Before any automatic retry claim, the work must additionally establish the operation's duplication semantics, exact intended target and revision, expected prior blob state, concurrency boundary and acceptable duplicate consequence. If the original mutation may already have succeeded and those conditions are unresolved, reconciliation or human decision is preferred over issuing a fresh mutation.

## Result

`MEMORY_CONSUMED_AND_DECISION_CHANGED`

The memory changed the classification criterion applied to the concrete provider case. It did not merely supply terminology or a citation.

## Scope / limitations

- This is a provider-analysis work item, not an external execution.
- No local GitHub mutation behavior was newly observed.
- The result depends on Q12's documented provider evidence and MEM-001's promoted semantic boundary.
- This does not prove that Content Factory's future implementation is automatically recoverable or that every GitHub mutation behaves identically.

## Success signals

1. Exact promoted memory revision is referenced.
2. A concrete provider operation is evaluated.
3. A pre-memory counterfactual is explicit.
4. The memory changes the selected recovery posture.
5. No external effect is performed.

## Q21 status

`COMPLETED`

This is the first demonstrated downstream consumption of a promoted Content Factory memory item with an explicit decision delta.
