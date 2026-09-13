# 32 — Cross-Repository Contract Implementation Mapping v0

Status: `EVIDENCE-BASED CURRENT MAP — CANDIDATE`
As of: 2026-09-13

This document maps the candidate cross-repository contract in `docs/31_cross_repository_interface_contract_v0.md` against the current implementation visible in the participating repositories.

It is an implementation map, not a claim that the complete cross-repository slice is operational.

## 1. Classification

- `IMPLEMENTED` — the required semantic boundary exists in the inspected implementation with direct evidence.
- `PARTIAL` — an important part exists, but the contract is incomplete or only local/bounded.
- `ADAPTER NEEDED` — both sides have useful mechanisms, but there is no verified interface binding between them.
- `MISSING` — no current implementation sufficient for the interface was found.
- `CONTRADICTED` — current implementation explicitly establishes a boundary that conflicts with the candidate contract.

## 2. Current overall result

| Interface | Status | Primary repository evidence | Main gap |
|---|---|---|---|
| I01 Demand → WorkItem | `PARTIAL` | `content_factory/src/content_factory/runtime.py` | No implemented Demand/intake/Factory Control path creates the WorkItem. |
| I02 WorkItem → Atlas | `ADAPTER NEEDED` | `content_factory` WorkItem; Atlas `WorkOrder` | Atlas WorkOrder does not currently carry the Factory WorkItem identity/revision contract; no cross-repo adapter is verified. |
| I03 Atlas → Capability / Executor | `ADAPTER NEEDED` | Atlas WorkOrder/ResultEnvelope; controlled executor ATLAS-NATIVE-V1 | Executor accepts its own authorized task contract, not the candidate CapabilityRequest interface. |
| I04 Capability → OutputRevision | `PARTIAL` | Whisper renderer + manifest/hashes; Factory ExecutionResult | Whisper produces durable artifacts and hashes, but there is no verified common OutputRevision contract bound to Factory/Executor execution identity. |
| I05 OutputRevision → Verification | `IMPLEMENTED` | Factory runtime + tests | Implemented only inside the bounded Factory runtime; not yet cross-repository. |
| I06 Verification → Human Acceptance | `IMPLEMENTED` | Factory runtime + tests | Implemented only inside the bounded Factory runtime; no cross-repo decision adapter yet. |
| I07 Acceptance → Release | `IMPLEMENTED` | Factory runtime state/authority transition | Semantics exist locally; cross-repository release authorization enforcement is not implemented. |
| I08 Release → Publication | `PARTIAL` | Factory injected Publisher + publication tests | Publication is injectable/simulated; real external publisher/effect is not established for the cross-repo slice. |
| I09 Publication → Observation | `PARTIAL` | Factory `DELIVERED → OBSERVED`, observation artifact path | Observation is currently represented by bounded runtime state/artifacts rather than the candidate `ObservationRecord` interface. |
| I10 Observation → Learning | `MISSING` | Learning research exists | No operational Observation → Learning integration was found. |

## 3. I01 — Demand → WorkItem

### Evidence

`content_factory/src/content_factory/runtime.py` defines a first-class immutable `WorkItem` with:

- `work_item_id`;
- `revision_id`;
- objective and requested outcome;
- inputs and knowledge basis;
- required capabilities;
- owner;
- acceptance criteria;
- release requirements;
- constraints, dependencies and success signals.

The runtime also has a `submit()` boundary that creates the initial `RECEIVED` state and durable event when configured with `RuntimeStore`.

### Classification

`PARTIAL`.

The WorkItem primitive and admission/storage boundary exist, but the candidate contract starts with a bounded `Demand` and a Factory-controlled intake/admission operation. The inspected current runtime has no implemented Demand object or Factory Control path that creates WorkItems from demand/priority/context.

### Consequence

The WorkItem is usable as the cross-repository canonical starting object, but I01 requires a Factory intake adapter/control-plane implementation before it can be called end-to-end implemented.

## 4. I02 — WorkItem → Atlas

### Evidence

Atlas has a real immutable `WorkOrder` in `src/atlas_agent/orchestration.py`. Its current fields include `work_order_id`, `task_id`, `run_id`, `execution_id`, revision, project, stage, worker, objective, scope paths, input references, acceptance criteria, allowed tools, budget, idempotency key and creation time.

Atlas documentation also establishes that Atlas owns the goal, plan, permissions, records and final response, and that `WorkOrder` is a trusted contract created by Atlas Core rather than by an LLM.

### Gap

The candidate cross-repository contract requires Atlas to consume an immutable Factory `work_item_id` + `work_item_revision_id` and create a WorkOrder that explicitly preserves that identity and revision.

The current Atlas `WorkOrder` schema does not expose those Factory identifiers as fields. Its `task_id` is an Atlas-local identity and `execution_id` is already part of the Atlas WorkOrder model. There is no verified adapter mapping Factory WorkItem → Atlas WorkOrder in the inspected code.

### Classification

`ADAPTER NEEDED`.

This is not a missing Atlas primitive. It is a missing cross-repository identity/contract binding.

## 5. I03 — Atlas → Capability / Executor

### Evidence

Atlas has a typed WorkOrder and ResultEnvelope-oriented orchestration model. The controlled executor has an active `ATLAS-NATIVE-V1` route based on an authorized task contract, exact repository revision, allowlisted paths, temporary lease, checks, review and human decision.

The executor explicitly states that it does not embed a model/provider and that authorization does not implicitly grant network, credentials, provider access, push, merge, deployment, publication, spending or automatic acceptance authority.

### Gap

The candidate contract names a `CapabilityRequest` containing capability identity/version, input references, output contract, allowed effects, requested authority and acceptance checks. The current executor entry route consumes its own authorized task/authorization representation rather than this CapabilityRequest.

No verified adapter translating Atlas WorkOrder → CapabilityRequest → executor task contract was found.

### Classification

`ADAPTER NEEDED`.

The underlying execution substrate is present; the contract boundary between Atlas capability intent and executor authorization is not yet implemented.

## 6. I04 — Capability → OutputRevision

### Evidence

Whisper Studio has a real local renderer. The active route takes an authored local pack containing image and voice assets, produces synchronized vertical MP4 output, and writes a project containing plan, per-shot assets/clips, timeline, final video, contact sheet and `manifest.json`.

The manifest records generator metadata, model/source metadata, shot count, timeline duration, final video, technical validation and per-file byte counts plus SHA-256 hashes.

Whisper therefore has a real artifact-production/evidence mechanism.

Factory has an `ExecutionResult` containing `execution_id`, `capability_id`, `output_revision_id`, payload and evidence references.

### Gap

The candidate contract requires a common `OutputRevisionProduced` with `output_revision_id`, `execution_id`, artifact references, manifest reference, hashes, producer version and input revision references.

The inspected Whisper renderer does not consume the cross-repository `execution_id` or emit the candidate `output_revision_id` as a shared interface object. The Factory `ExecutionResult` currently binds those identifiers locally inside its own runtime.

### Classification

`PARTIAL`.

Both sides contain most of the underlying mechanisms, but the semantic output contract is not yet bridged.

## 7. I05 — OutputRevision → Verification

### Evidence

The Factory runtime requires verification to bind to the exact `ExecutionResult.output_revision_id`. A mismatched revision raises an error and the runtime enters `FAILED`.

`tests/test_runtime.py` contains a dedicated `test_verification_is_revision_bound` test. The runtime also materializes verification evidence and distinguishes verification from acceptance.

### Classification

`IMPLEMENTED` — bounded local implementation.

### Limitation

This does not prove cross-repository verification. I05 is implemented as a Factory runtime semantic boundary, but the Whisper-produced output is not yet entering that boundary through the candidate interface.

## 8. I06 — Verification → Human Acceptance

### Evidence

The Factory runtime has a typed `AcceptanceDecision` containing output revision, acceptance decision, authority and reason. Acceptance is a distinct state transition from `VERIFIED` to `ACCEPTED`.

The runtime rejects acceptance without authority, and `tests/test_runtime.py` contains `test_acceptance_requires_authority`.

### Classification

`IMPLEMENTED` — bounded local implementation.

### Limitation

The human decision boundary is not yet connected to an external cross-repository output. The contract therefore exists semantically but not as an end-to-end interface.

## 9. I07 — Acceptance → Release

### Evidence

The Factory runtime requires explicit `release_authority`. It transitions through `RELEASE_READY` and `RELEASED` only after acceptance.

This preserves the intended distinction:

`execution ≠ verification ≠ acceptance ≠ release`.

### Classification

`IMPLEMENTED` — bounded local implementation.

### Limitation

The candidate `ReleaseAuthorization` object is not yet a cross-repository message consumed by a real publisher adapter. The current release boundary is therefore semantic/local rather than integrated.

## 10. I08 — Release → Publication

### Evidence

The Factory runtime has an injected `Publisher` protocol and a `PublicationResult` containing publication identity, exact output revision, target, external observability and evidence references.

The tests deliberately include both a fake externally observable publisher and a simulated non-observable publisher. The README explicitly states that a synthetic/demo publication is not evidence of a real external effect.

Whisper Studio explicitly excludes automatic publishing and analytics from the active route.

### Classification

`PARTIAL`.

The semantic boundary and test seam exist. A real cross-repository publisher/external-effect path does not.

## 11. I09 — Publication → Observation

### Evidence

The Factory runtime can transition from `DELIVERED` to `OBSERVED` when the publication result is marked `externally_observable`. The artifact materialization tests verify an observation artifact for an externally observable fake publisher and no observation artifact for a simulated publication.

### Gap

The candidate contract defines an explicit `ObservationRecord` with `observation_id`, `publication_id`, observation time, source, metrics, external reference, confidence and evidence references.

The current bounded runtime represents observation primarily through state transition and materialized artifacts. No first-class `ObservationRecord` implementation matching the cross-repository contract was found in the inspected current code.

### Classification

`PARTIAL`.

This is stronger than missing: the system already distinguishes externally observable delivery from simulation, but the semantic observation interface is not yet explicit.

## 12. I10 — Observation → Learning

### Evidence

Content Factory documentation and records contain an explicit learning-loop model and research-to-learning experiments. The current README states that the learning loop is active research and identifies several unproven properties, including memory changing execution, real external outcome from memory-informed execution and product/business improvement.

### Gap

No operational runtime interface was found that consumes an `ObservationRecord` and creates a `LearningCandidate` or decision that feeds back into planning/knowledge.

### Classification

`MISSING` as an executable interface.

Research and operating-memory documentation do not constitute an implemented runtime integration.

## 13. Cross-repository identity gap

The most important implementation gap is not the absence of individual primitives. It is the missing binding layer between local identities.

Current local identities include:

```text
Factory:
  work_item_id
  revision_id
  execution_id
  output_revision_id
  publication_id

Atlas:
  work_order_id
  task_id
  run_id
  execution_id

Executor:
  authorized task identity / task contract / attempt and lease state

Whisper:
  project / shot / render / manifest / artifact hashes
```

The candidate contract requires these to be related explicitly without collapsing their semantic ownership.

In particular, Atlas currently has an `execution_id` inside `WorkOrder`, while the candidate cross-repository contract places `execution_id` downstream of `capability_request_id`. This is a material interface design issue and must be resolved before implementation rather than silently aliased.

## 14. Current vertical slice reality

The repositories currently demonstrate several separate bounded slices:

```text
Content Factory:
WorkItem
  → admit
  → execute capability
  → exact-revision verification
  → human-authorized acceptance
  → release authority
  → injected publisher
  → observed/simulated effect
```

```text
Atlas:
request
  → typed WorkOrder
  → controlled worker/tool orchestration
  → ResultEnvelope
  → human decision
```

```text
Controlled Executor:
authorized task
  → isolated worktree
  → lease
  → allowlisted patch
  → checks
  → review
  → human decision
```

```text
Whisper Studio:
authored local pack
  → shot assets
  → synchronized render
  → manifest
  → hashes
  → local MP4
```

These are compatible in intent but are not yet one executable cross-repository chain.

## 15. What should NOT be implemented yet

The mapping does not justify any of the following changes yet:

- global event bus;
- shared database;
- replacement of local identifiers with one global ID;
- making Atlas a publisher;
- making Whisper Studio an autonomous agent;
- automatic learning-to-strategy promotion;
- replacing the controlled executor with direct provider calls;
- treating GitHub state as runtime state;
- treating successful rendering as semantic acceptance;
- treating publication submission as external outcome.

## 16. Recommended implementation order derived from the map

The smallest path to one real vertical slice is:

1. Resolve the `execution_id` ownership/placement conflict between Atlas WorkOrder and the cross-repository contract.
2. Add a Factory → Atlas adapter carrying immutable WorkItem identity/revision into a WorkOrder.
3. Add an Atlas → Executor capability/authorization adapter without granting additional authority.
4. Add a Whisper output adapter that converts its manifest/artifact evidence into the candidate OutputRevision contract.
5. Reuse the already implemented Factory verification and acceptance boundaries against that real OutputRevision.
6. Add explicit ReleaseAuthorization projection into the publisher boundary.
7. Keep publication simulated until a real external destination and reconciliation protocol are explicitly authorized.
8. Make ObservationRecord explicit before claiming I09 complete.
9. Implement I10 only after I09 produces durable observations.

This order deliberately minimizes new architecture: adapters first, existing bounded semantics reused where possible, real external effects last.

## 17. Evidence basis

Primary implementation evidence inspected on 2026-09-13:

- `content_factory/README.md`
- `content_factory/src/content_factory/runtime.py`
- `content_factory/tests/test_runtime.py`
- `content_factory/docs/31_cross_repository_interface_contract_v0.md`
- `-atlas-agent/README.md`
- `-atlas-agent/src/atlas_agent/orchestration.py`
- `controlled-agent-executor/README.md`
- `controlled-agent-executor/docs/orchestration-principles.md`
- `whisper-studio/README.md`
- `whisper-studio/one_command.py`

The map is based on current repository implementation, not historical records unless explicitly identified above.

## 18. Status

`CANDIDATE — IMPLEMENTATION MAPPING COMPLETE`

The next legitimate architectural decision is the identity/adapter boundary at I02/I03/I04, especially the ownership of `execution_id`. No runtime implementation should begin before that decision is explicit.
