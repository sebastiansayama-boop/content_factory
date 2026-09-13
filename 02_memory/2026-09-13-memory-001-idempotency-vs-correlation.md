# Reusable Memory — Idempotency vs Correlation

Date: 2026-09-13
Memory ID: MEM-2026-09-13-001
Memory type: knowledge
Status: ACCEPTED_REUSABLE
Revision ID: MEM-2026-09-13-001-r1

## Scope

External-capability evaluation, recovery analysis and external-effect design.

## Reusable proposition

Correlation identity and provider operation identity must not be treated as evidence of duplicate-safe retry. Automatic recoverability depends on the operation's duplication semantics and on the provider's actual idempotency/deduplication or equivalent conditional-state contract.

The proposition does **not** require an idempotency key for every external mutation. Natural idempotency or proven conditional-state semantics may provide sufficient safety for some operation classes.

## Why retained

This proposition was promoted from Learning 001 through explicit decision `DEC-2026-09-13-001`.

The source research distinguishes:

- factory correlation ID — links a factory interaction across records and observations;
- provider operation ID — identifies a provider-side execution when exposed;
- provider idempotency key — provider contract for duplicate-safe repeated requests.

The research rejects treating either correlation ID or operation ID as a substitute for idempotency semantics.

## Provenance

Source learning:

- `09_learning/2026-09-13-learning-q19-idempotency-correlation-boundary.md`
- revision `8811878383a2e6a6847e2f4143a226fb1697e4e6`

Promotion decision:

- `05_decision/2026-09-13-learning-001-promotion.md`
- decision `DEC-2026-09-13-001`

Underlying research:

- `10_records/2026-09-13-external-system-q15-idempotency-correlation-requirements-research.md`
- `10_records/2026-09-13-external-system-q12-github-mutation-identity-matrix.md`
- `10_records/2026-09-13-external-system-q13-factory-identity-provenance-research.md`

## Operational use

Before classifying an external capability as automatically recoverable, separately evaluate:

```text
operation semantics
provider idempotency / deduplication
provider operation identity
factory correlation identity
reconciliation evidence
```

An endpoint being callable, or an execution being identifiable, is not by itself evidence that an unresolved retry is safe.

## Known unknowns

- No concrete first Content Factory external effect has yet validated this proposition locally.
- Provider-specific guarantees remain unknown until the concrete capability is inspected.
- This memory does not define a universal retry implementation or authority policy.
- Correlation observability after execution remains provider-dependent.

## Limitations

This is reusable knowledge about an evaluation boundary, not a provider-specific implementation prescription and not proof of Content Factory external-effect behavior.

## Invalidation / supersession

None at creation. If materially contradicted, stale, rejected or superseded, preserve this revision and create an explicit subsequent status/revision rather than rewriting history.

## Confidence

HIGH for the semantic distinction established by the source research; MEDIUM for application to any future provider until that provider's concrete contract is verified.

## Q21 test condition

A later bounded work item must reference this exact memory revision and record whether it changes its decision/specification/verification posture. Citation without decision impact does not count as successful memory consumption.
