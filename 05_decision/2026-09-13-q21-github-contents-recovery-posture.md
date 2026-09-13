# Decision — Q21 GitHub Contents Recovery Posture

Date: 2026-09-13
Decision ID: DEC-2026-09-13-002
Decision type: HOLD / UPDATE
Subject: `WI-2026-09-13-001`
Subject revision: `WI-2026-09-13-001-r1`

## Knowledge consumed

- `02_memory/2026-09-13-memory-001-idempotency-vs-correlation.md`
- revision `MEM-2026-09-13-001-r1`

## Provider evidence

- `10_records/2026-09-13-external-system-q12-github-mutation-identity-matrix.md`
- `10_records/2026-09-13-external-system-q13-factory-identity-provenance-research.md`

## Question

Does a GitHub Contents API file/blob SHA plus generated commit SHA justify automatic recovery of an ambiguous mutation?

## Options considered

1. AUTOMATIC_RECOVERY — treat resulting file/blob/commit identities as sufficient.
2. CONDITIONAL_RECOVERY — allow automatic recovery only after operation-specific duplication and state conditions are proven.
3. HUMAN_OR_RECONCILIATION — when the original outcome is ambiguous and the required safety conditions are unresolved, do not issue a fresh mutation automatically.

## Selected option

`CONDITIONAL_RECOVERY_WITH_RECONCILIATION_FIRST`

A resulting file/blob SHA or commit SHA is evidence of resulting external state, not proof of duplicate-safe retry. Automatic recovery requires operation-specific evidence covering duplication semantics, exact target/input revision, expected prior blob state, concurrency boundary and bounded duplicate consequence.

When an original mutation may already have succeeded and these conditions remain unresolved, the factory should reconcile the external state or escalate rather than issue a new mutation merely because a new request can be executed.

## Decision delta caused by memory

Counterfactual baseline without MEM-001:

`result identity → stronger recovery posture`

Actual decision with MEM-001:

`result identity → state evidence → evaluate duplication semantics → conditional recovery / reconciliation`

Therefore MEM-001 materially changed the decision boundary. It prevented provider result identity from being treated as equivalent to idempotency/retry safety.

## Authority

This is a bounded analysis decision only. It authorizes no GitHub mutation, retry, publication, release, or generic infrastructure change.

## Conditions

A future implementation may only claim automatic recovery for this operation class after the concrete GitHub interaction contract and failure mode are independently verified.

## Result

`Q21 = COMPLETED`

Memory consumption is demonstrated because the later work references the exact promoted memory revision and records a different selected posture from the explicit counterfactual baseline.
