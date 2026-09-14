# Factory Kernel v0

## Scope

Content Factory owns durable work-item lifecycle and execution semantics. External execution systems such as n8n remain capability workers and execution substrates.

## First-class identity

Each Work Item has a durable `operation_id`. Each execution attempt has its own `execution_id` and `attempt_id`.

The intended identity chain is:

```text
work_item_id
  ↓
operation_id
  ↓
execution attempt
  ↓
execution_id
  ↓
output_revision_id
```

n8n execution uses the factory-owned `operation_id`; it must not invent a replacement operation identity.

## Durable projections

RuntimeStore persists:

- work-item control state;
- append-only event journal;
- execution attempt status;
- successful ExecutionResult;
- VerificationResult;
- AcceptanceDecision;
- PublicationResult;
- stable publication reservation/idempotency identity.

ArtifactStore remains a separate filesystem evidence projection.

## Recovery

A restart reconstructs execution and decision projections before the runtime continues.

If the process restarts while an execution attempt is `RUNNING`, that attempt becomes `UNKNOWN` rather than being silently re-executed.

A non-idempotent capability cannot automatically re-run after an `UNKNOWN` attempt. An operator must explicitly resolve the unknown state.

An idempotent, retryable capability may use the configured execution-attempt budget.

## Lifecycle states

```text
RECEIVED
  ↓
ADMITTED
  ↓
PRODUCED
  ↓
VERIFIED
  ↓
ACCEPTED
  ↓
RELEASE_READY
  ↓
RELEASED
  ↓
DELIVERED
  ↓
OBSERVED
```

Terminal control states also include:

```text
FAILED
UNKNOWN
CANCELLED
```

`UNKNOWN` means the runtime cannot prove whether the in-flight execution produced an external effect. It is intentionally not treated as success or failure.

`CANCELLED` is an explicit control decision for states before external release. It does not claim that an already-released external effect was undone.

## External publication boundary

Before publication, the kernel reserves a stable `publication_id`.

Publishers receive that identifier and must preserve it. The HTTP publisher also sends it as `Idempotency-Key` so a downstream service can deduplicate retries.

The kernel therefore distinguishes:

```text
execution succeeded
≠
publication delivered
≠
publication observed
```

## Deliberate non-goals

The v0 kernel does not claim to implement:

- distributed worker scheduling;
- hard cancellation of arbitrary Python callables;
- generic execution timeouts;
- a distributed task queue;
- global retry of non-idempotent effects.

Those are responsibilities of the execution substrate or a future worker scheduler. The kernel instead defines the durable identity, recovery, authorization, and effect boundaries around them.
