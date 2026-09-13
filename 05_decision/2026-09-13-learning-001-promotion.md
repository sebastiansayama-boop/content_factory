# Decision — Promote Learning 001 to Reusable Memory

Date: 2026-09-13
Decision ID: DEC-2026-09-13-001
Decision type: ACCEPT / UPDATE
Subject: `09_learning/2026-09-13-learning-q19-idempotency-correlation-boundary.md`
Subject revision: `8811878383a2e6a6847e2f4143a226fb1697e4e6`

## Evidence

- Q19 learning candidate: `09_learning/2026-09-13-learning-q19-idempotency-correlation-boundary.md`
- Source research: `10_records/2026-09-13-external-system-q15-idempotency-correlation-requirements-research.md`
- Supporting research: Q12 GitHub mutation identity matrix; Q13 factory-side identity/provenance research.

## Question

Is Learning 001 sufficiently scoped and evidenced to become reusable memory without converting its uncertainties or research-level conclusions into universal facts?

## Options considered

1. REJECT promotion because no Content Factory external effect has yet been executed.
2. PROMOTE as a bounded reusable knowledge proposition, retaining provider-specific and local-behavior unknowns.
3. PROMOTE as a universal implementation rule requiring provider idempotency for all external mutations.

## Selected option

`PROMOTE_AS_BOUNDED_REUSABLE_KNOWLEDGE`

The learning is promoted because its core distinction is explicitly supported by the source research, its scope is bounded to external-capability/recovery analysis, competing simplifications are recorded and rejected, and unresolved provider-specific behavior remains explicit.

Promotion does **not** establish that:

- every external mutation requires an idempotency key;
- any particular provider is automatically recoverable;
- Content Factory has proven an external effect;
- correlation proves provider execution;
- operation identity proves retry safety.

## Authority

This record is an explicit project decision to promote the learning proposition into `02_memory` for reuse in later analysis. It does not authorize external mutation, automatic retry, production implementation, or a model/ontology change.

## Authorized effects

- create one versioned reusable memory item derived from Learning 001;
- mark Learning 001 as `PROMOTED` and link the memory item;
- use the memory item as a knowledge-basis reference in later bounded work.

## Forbidden / unauthorized effects

- no generic idempotency infrastructure;
- no automatic retry policy;
- no provider-specific implementation claim;
- no external effect;
- no ontology or model mutation solely from this promotion.

## Conditions

The promoted memory must preserve source/evidence/provenance, explicit scope, known unknowns, revision identity and the distinction between correlation, operation identity and idempotency.

## Result

Q20: `COMPLETED`

Promotion is explicit and bounded. Q21 may now test whether the resulting memory is actually consumed by a later work item and changes its decision.
