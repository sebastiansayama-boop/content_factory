# 27 — Factory Runtime v0

Status: `IMPLEMENTED / LOCAL EXECUTION CORE`

## Purpose

Factory Runtime v0 is the first executable implementation of the Content Factory's execution boundary. It is intentionally small: one bounded Work Item, one selected capability, one executor, one verification step, one acceptance decision, one explicit release authority, and one injected publisher.

It does not attempt to implement the complete Content Factory.

## Runtime contract

```text
Work Item
  ↓
submit
  ↓
RECEIVED
  ↓ admit
ADMITTED
  ↓ execute capability
PRODUCED
  ↓ verify exact output revision
VERIFIED
  ↓ explicit acceptance + authority
ACCEPTED
  ↓ explicit release authority
RELEASE_READY
  ↓ release
RELEASED
  ↓ injected publisher
DELIVERED
  ↓ externally observable publication
OBSERVED
```

Any failure enters `FAILED` and is retained in the event journal.

## Implemented primitives

- `WorkItem` — canonical bounded work request for v0.
- `Capability` — abstract capability bound to an executor.
- `ExecutionResult` — execution identity and exact output revision.
- `VerificationResult` — revision-bound verification.
- `AcceptanceDecision` — revision-bound acceptance with explicit authority.
- `PublicationResult` — publication identity, target, exact output revision and external observability.
- `FactoryRuntime` — deterministic state transition/orchestration kernel.
- append-only in-memory `Event` journal for provenance reconstruction.
- injected `Publisher` boundary; no publisher means no external effect.

## Explicit non-features

v0 does not yet provide:

- durable database storage;
- queue workers or leases;
- retry/recovery after process crash;
- multiple capabilities per work item;
- capability routing or provider selection;
- production provider adapters;
- real external publication;
- persistent provenance storage;
- observation ingestion from an external channel;
- authorization service or policy engine.

These are deliberately deferred. The first implementation should prove the execution boundary before adding infrastructure around it.

## Safety invariants

1. Execution does not imply publication.
2. Verification must bind to the exact output revision.
3. Acceptance must bind to the exact output revision.
4. Acceptance requires an explicit authority value.
5. Release requires explicit release authority.
6. Publication is impossible without an injected publisher.
7. Publication must bind to the exact output revision.
8. External observation is represented separately from delivery.
9. Every transition is recorded as an event.
10. A failed operation cannot silently return to a successful state.

These invariants implement the repository's existing state model: revision-bound review, no silent promotion, explicit external effects, append-only history and separate object lifecycles. fileciteturn63file0

## Test status

The repository now contains unit tests for:

- complete v0 traversal to `OBSERVED`;
- refusal to publish without a publisher;
- verification revision mismatch;
- acceptance without authority.

The test suite is not yet CI-verified because the repository previously had no executable workflow. The source and tests have been written, but local execution remains a separate verification step.

## Relation to first external proof

A fake publisher can prove that the runtime's external-effect boundary is exercised, but it cannot satisfy the first external proof criterion. The actual proof still requires a real external destination and an independently inspectable external effect. fileciteturn67file0

## Research reconciliation

`SUPPORTS_CURRENT_MODEL`: W3C PROV models provenance around entities, activities and agents and provides constraints/representations for reconstructing provenance. The v0 event journal follows the same basic separation without claiming conformance to PROV. citeturn0search0turn0search3

`EXTENDS_CURRENT_MODEL`: the repository previously defined the execution boundary conceptually; this document and implementation make the minimum runtime transition path concrete without changing the value-flow architecture. fileciteturn66file0

`NOT_PROVEN`: durable recovery, provider independence in production, and a real external effect remain unproven.
