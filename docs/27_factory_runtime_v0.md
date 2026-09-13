# 27 — Factory Runtime v0

Status: `IMPLEMENTED / LOCAL EXECUTION CORE`

## Purpose

Factory Runtime v0 is the first executable implementation of the Content Factory execution boundary. It is intentionally small: one bounded Work Item, one selected capability, one executor, one verification step, one acceptance decision, one explicit release authority, and one injected publisher.

It does not claim to implement the complete production Content Factory.

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

Any failure enters `FAILED` and is retained in the runtime event journal and, when configured, the workspace artifact store.

## Implemented primitives

- `WorkItem` — bounded work request for v0.
- `Capability` — abstract capability bound to an executor.
- `ExecutionResult` — execution identity and exact output revision.
- `VerificationResult` — revision-bound verification.
- `AcceptanceDecision` — revision-bound acceptance with explicit authority.
- `PublicationResult` — publication identity, target, exact output revision and external observability.
- `FactoryRuntime` — deterministic state transition/orchestration kernel.
- append-only in-memory `Event` journal for the active runtime instance.
- `ArtifactStore` — durable workspace projections of runtime evidence.
- injected `Publisher` boundary; no publisher means no external effect.
- `HttpJsonAdapter` and `IntegrationConfig` — provider-neutral HTTP integration boundary with environment-based secret lookup.

## Explicit non-features

The bounded v0 intentionally does not provide:

- durable runtime control state or crash recovery;
- queue workers, leases or scheduling;
- multi-capability orchestration;
- provider routing or fallback policy;
- production credential provisioning;
- a built-in CMS/social/channel publisher;
- external observation ingestion;
- a general authorization/policy service;
- a claim that a publication equals an audience or business outcome.

These are deployment/production-control concerns and must be introduced only with a concrete case that requires them.

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
11. Simulated publication cannot create an external observation record.

## Evidence materialization

When an `ArtifactStore` is configured, the runtime projects evidence into the corresponding repository workspace zones:

```text
03_working_context → work item projection
06_production      → execution result
07_verification    → verification result
05_decision        → acceptance decision
08_effects_feedback→ publication/effect record
01_observation    → only for externally observable publication
10_records        → complete runtime event journal
```

Workspace materialization is not the same operation as committing the artifacts to Git history. Repository synchronization remains an explicit boundary.

## Test status

The repository test workflow runs `pytest` on pushes to `main` and pull requests. The v0 suite covers:

- complete traversal to `OBSERVED`;
- refusal to publish without a publisher;
- verification revision mismatch;
- acceptance without authority;
- durable artifact materialization;
- refusal to create an observation for simulated publication.

A successful CI run verifies the repository implementation and tests. It does not constitute an external-world proof.

## First external proof

A fake or simulated publisher proves only the internal boundary. The first external proof requires a real destination, real authorization, an independently inspectable external reference/effect, and a reconstructable provenance and authority chain.

## Completion boundary

`Factory Runtime v0` is considered repository-complete when the executable boundary, tests, evidence projections, integration boundary, zone contracts and operating-model documentation are mutually consistent.

Production deployment is a separate phase. Its minimum sequence is:

```text
compute environment
→ secret mechanism
→ one real provider adapter
→ real capability execution
→ verification
→ release authority
→ one real publisher
→ external observation
→ durable runtime state
→ recovery/idempotency
→ broader provider/channel coverage
```

No step in that sequence is marked complete by documentation alone.