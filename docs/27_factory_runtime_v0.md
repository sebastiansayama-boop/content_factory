# 27 — Factory Runtime v0

Status: `PHASE 1 COMPLETE / DURABLE CONTROL STATE`

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
- append-only event journal for the active runtime instance.
- `RuntimeStore` — durable SQLite control state and event journal.
- atomic persistence of each state transition together with its event.
- restart reconstruction of persisted states and events.
- `ArtifactStore` — durable workspace projections of runtime evidence.
- injected `Publisher` boundary; no publisher means no external effect.
- `HttpJsonAdapter` and `IntegrationConfig` — provider-neutral HTTP integration boundary with environment-based secret lookup.

## Durable runtime boundary

`RuntimeStore` is intentionally separate from `ArtifactStore`.

```text
RuntimeStore
  → recovery/control state
  → current work-item state
  → append-only runtime events

ArtifactStore
  → repository evidence projection
  → working context / production / verification /
    decision / effects / observation / records
```

The runtime uses SQLite WAL with `synchronous=FULL` for this bounded single-node phase. The SQLite documentation establishes transactional atomicity and durability guarantees for committed transactions, while WAL is explicitly a same-host mechanism and does not solve distributed coordination.

The phase proof is intentionally limited to application/runtime restart recovery. It does not claim external-effect recovery or idempotency.

## Explicit non-features

The bounded phase intentionally does not provide:

- external-operation idempotency or reconciliation;
- queue workers, leases or scheduling;
- multi-capability orchestration;
- provider routing or fallback policy;
- production credential provisioning;
- a built-in CMS/social/channel publisher;
- external observation ingestion;
- a general authorization/policy service;
- a claim that a publication equals an audience or business outcome.

These are later operational phases and must not be implied by durable local state.

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
10. State transition and its event are committed together when `RuntimeStore` is configured.
11. A failed operation cannot silently return to a successful state.
12. Simulated publication cannot create an external observation record.

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

The repository test workflow runs `pytest` on pushes to `main` and pull requests. The Phase 1 suite covers:

- complete traversal to `OBSERVED`;
- refusal to publish without a publisher;
- verification revision mismatch;
- acceptance without authority;
- durable artifact materialization;
- refusal to create an observation for simulated publication;
- runtime state and event-journal recovery after restart;
- atomic persistence of state transition plus event.

CI run `34741686623` for the durable-runtime implementation completed the `pytest -q` step successfully. The workflow was still finalizing its post-job cleanup when inspected; the test step itself is the relevant verification result.

## First external proof

A fake or simulated publisher proves only the internal boundary. The first external proof requires a real destination, real authorization, an independently inspectable external reference/effect, and a reconstructable provenance and authority chain.

## Phase boundary

Phase 1 is complete when durable runtime control state, atomic state/event persistence, restart reconstruction, tests and the model/documentation layers are mutually consistent.

The next phase is Phase 2 — Real Execution:

```text
compute environment
→ secret mechanism
→ one real provider adapter
→ provider credentials
→ connectivity test
→ real capability execution
→ verification
```

No external provider, credential or real-world execution is marked complete by documentation alone.