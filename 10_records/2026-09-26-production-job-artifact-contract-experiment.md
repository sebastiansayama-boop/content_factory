# ProductionJob + Artifact Contract Experiment

Date: 2026-09-26
Repository: sebastiansayama-boop/content_factory
Branch: experiment/dependency-aware-regeneration-v1

## Purpose

Test the minimum production contract before changing implementation.

Control case:

`script → image → video → final assembly`

The experiment compares the existing `ExecutionResult` boundary with a normalized:

`ProductionJob → Artifact`

model and checks whether the existing `FactoryRuntime` control boundary must change.

## Evidence inspected

Repository:
- `src/content_factory/runtime.py`
- `src/content_factory/text_capability.py`
- `src/content_factory/n8n_capability.py`
- `src/content_factory/content_provenance.py`
- `docs/27_factory_runtime_v0.md`

External provider documentation:
- Adobe Firefly Creative Production Workflow API
- Luma generation API

## Experiment 1 — Existing ExecutionResult mapping

Current text capability creates:

- execution_id
- capability_id
- output_revision_id
- payload
- evidence_refs

The real OpenAI-compatible adapter binds `output_revision_id` to a provider response ID.

Therefore an existing result can be decomposed as:

```
ProductionJob
  job_id             = execution_id
  capability_id      = capability_id
  provider_job_id    = provider response ID
  status             = completed
  output_artifact_id = derived from output revision

Artifact
  artifact_id        = output revision / artifact identity
  type               = text
  payload/reference  = current payload
```

Result: the mapping is possible, but information is missing.

Missing from the current `ExecutionResult` contract:
- explicit provider identity;
- explicit provider job identity;
- provider/model parameters;
- explicit input artifact references;
- job lifecycle;
- explicit output artifact collection;
- failure/cancellation metadata;
- timing;
- provider-specific job metadata.

## Experiment 2 — Synchronous versus asynchronous execution

Current text capability can behave synchronously from the runtime's point of view.

External production APIs do not guarantee this shape.

Adobe's Workflow API returns a batch/job identifier, exposes status, cancellation, and per-asset execution results. Luma creates a generation ID and requires status retrieval/polling until completion or failure.

Result: `ProductionJob` is not merely a renamed `ExecutionResult`. It represents a provider-side operation with its own lifecycle.

## Experiment 3 — One job can produce multiple artifacts

Adobe's batch execution exposes per-asset results and outputs. Therefore the normalized contract must not assume:

`one job → one artifact`

Minimum relation:

`ProductionJob → 0..N Artifact`

A single artifact is common, but not structurally guaranteed.

## Experiment 4 — One job can consume multiple artifacts

The target video stage can consume an image artifact plus structured production parameters. Assembly can consume multiple video/audio artifacts.

Therefore:

`ProductionJob → N input artifacts`

is required.

This is not representable cleanly by treating the output payload of the preceding `ExecutionResult` as the only input channel.

## Experiment 5 — Dependency-aware regeneration

Current `ProvenanceGraph` already supports:

`claim → editorial unit → asset`

and computes affected assets for changed claims.

Extending the production model gives:

`claim → editorial unit → artifact → production job → downstream artifact`

Example:

```
C1 changed
 ↓
script artifact A1
 ↓
image artifact A2
 ↓
video artifact A3
 ↓
final artifact A4
```

An unrelated audio artifact A5 can remain intact.

Result: dependency-aware regeneration requires artifact-level dependency identity. Asset IDs alone are insufficient once production jobs become first-class.

## Experiment 6 — WorkItem boundary

Current `FactoryRuntime` intentionally supports one selected capability per WorkItem.

The experiment does not require replacing that boundary.

A WorkItem can remain the control-plane unit while a production capability creates/manages one or more ProductionJobs.

Recommended conceptual boundary:

```
WorkItem
  ↓
Capability
  ↓
ProductionJob
  ↓
Provider Adapter
  ↓
Provider Job
  ↓
Artifact(s)
  ↓
ExecutionResult
  ↓
Verification
  ↓
Acceptance
  ↓
Delivery
```

Result: `FactoryRuntime` can remain the control kernel. The production lifecycle belongs below the capability/execution boundary.

## Experiment 7 — ArtifactStore distinction

The current `ArtifactStore` is an evidence projection of runtime state:

- working context
- production evidence
- verification
- decision
- effects/feedback
- observation
- records

It is not currently a general media artifact registry.

Result: do not overload the existing `ArtifactStore` with provider media semantics without a separate contract.

## Experiment 8 — Minimal ProductionJob contract

Fields justified by the experiments:

- `job_id`
- `capability_id`
- `provider`
- `provider_job_id`
- `input_artifact_ids`
- `parameters`
- `status`
- `output_artifact_ids`
- `error` / failure information
- `created_at`
- `started_at`
- `completed_at`
- `evidence_refs`

Not required for the first contract experiment:
- cost
- provider-specific routing policy
- queue implementation
- scheduling
- generalized distributed workers

## Experiment 9 — Minimal Artifact contract

Fields justified by the dependency and provider experiments:

- `artifact_id`
- `artifact_type`
- `revision_id`
- `uri/reference or payload`
- `producer_job_id`
- `created_at`
- `metadata`

The artifact must be addressable by downstream jobs and immutable by identity. A replacement is a new artifact/revision, not mutation of the old artifact identity.

## Experiment 10 — Runtime preservation

Existing runtime invariants remain valid:

- execution does not imply publication;
- verification binds to an exact output revision;
- acceptance binds to an exact output revision;
- explicit authority is required;
- publication binds to the exact accepted output;
- runtime events remain the durable control record.

Result: no evidence currently requires rewriting the FactoryRuntime state machine.

## Final result

The experiments support a narrow architectural change:

```
Capability
   ↓
ProductionJob
   ↓
Artifact(s)
```

should become the production execution model, while:

```
WorkItem
   ↓
FactoryRuntime
   ↓
Verification / Acceptance / Release / Delivery
```

remains the control model.

The current `ExecutionResult` should therefore not be deleted. It should become the runtime-facing completion/evidence envelope around one or more production jobs/artifacts, or be narrowed to that role during implementation.

## Implementation boundary

Do NOT implement provider-specific image/video/audio adapters yet.

The next implementation should be a minimal internal contract test using a fake provider:

```
fake provider
→ ProductionJob
→ two Artifact outputs
→ downstream job consuming both
→ verification
→ regeneration of one upstream input
→ downstream invalidation/rebuild
```

This test is sufficient to prove the new abstraction before connecting real media providers.

## Decision

Proceed to implementation of the minimal provider-neutral `ProductionJob` + `Artifact` contract.

Do not expand into scheduling, cost optimization, provider routing, or a generalized workflow engine until this contract passes the internal dependency/regeneration test.

## External verification

Adobe documents asynchronous batch execution with a returned `batchId`, status tracking, cancellation, per-asset results, outputs, errors, and timing.

Luma documents generation IDs, asynchronous generation state, polling, completion/failure, and generated asset references.

These external APIs independently support the distinction between a production job and its resulting artifact(s).
