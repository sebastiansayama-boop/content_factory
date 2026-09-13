# 30 — Diagnostic Reconciliation

Purpose: reconcile the diagnostic findings with mechanisms that have an executable or documented basis, then remove contradictions and stale contracts without expanding the architecture beyond the demonstrated case.

## Mechanism basis

The repository's control model is consistent with several established mechanisms:

- Append-only event history and provenance: preserve what happened, by whom, and from which inputs rather than treating the latest file as the whole truth. This is the operational application of provenance concepts such as W3C PROV.
- Explicit decision records: architecture and operational choices are recorded with rationale and consequences, consistent with Architecture Decision Record practice.
- Human authority gates: acceptance and release are explicit decisions rather than implicit consequences of production or verification. This matches governance and human-oversight principles in the NIST AI Risk Management Framework.
- After-action learning: observation is interpreted before a learning candidate is promoted. This follows the established AAR pattern of learning from both successful and failed outcomes.
- Contract-first integration: provider adapters expose the external boundary; capability bindings map provider results into the factory's canonical execution contract. Provider-specific behavior is therefore not duplicated in the orchestration kernel.
- Revision-bound verification: verification and acceptance identify the exact output revision, preventing a later revision from inheriting an earlier approval.
- Fail-closed publication: release authority and an explicit publisher are required before an external effect can occur.

These mechanisms justify the existing bounded architecture. They do not justify distributed queues, workers, retries, external-effect idempotency, or full crash/resume until a concrete case requires them.

## Defects resolved

### 1. CI environment mismatch

Finding: the workflow invoked `pytest` without installing the source-layout package, while local configuration relied on `pythonpath = ["src"]`.

Resolution: CI now installs the project with `python -m pip install -e .` before running tests.

Mechanism: reproduce the package installation boundary used by an actual installed Python project instead of relying on a test-runner path convenience.

### 2. Stale OpenAI adapter execution contract

Finding: `tests/test_integrations.py` called `OpenAIResponsesAdapter.execute()` and asserted an obsolete `openai.responses.text_generation` mapping. The current adapter owns provider transport; `openai_capability.py` owns the canonical `ExecutionResult` mapping.

Resolution: removed the stale adapter-execution test. The mapping proof remains in `tests/test_openai_capability.py`, against the current capability boundary.

Mechanism: single responsibility at the integration boundary. Transport and canonical capability semantics are tested separately.

### 3. Human-readable and machine-readable candidate lifecycle drift

Finding: the transition matrix treated `CANDIDATE → RESEARCH_REQUIREMENT` as a candidate state transition, while the machine model defines `ADMITTED` as the terminal candidate state and `RESEARCH_REQUIREMENT` as the start of a separate research lifecycle.

Resolution: the transition matrix now uses `CANDIDATE → ADMITTED` and explicitly models creation/activation of a research object as a cross-object relation.

Mechanism: one-object-one-lifecycle with explicit relations between objects.

### 4. Incomplete machine-readable direction map

Finding: `model/project-direction-map.yaml` declared required fields but did not populate them for every direction.

Resolution: every direction now contains the declared navigation fields, including goal, proof status, unresolved state, dependencies, blockers, next legitimate step and return point.

Mechanism: durable operating memory requires the navigation projection to be reconstructable without relying on conversational context.

### 5. Ambiguous external outcome overclaim

Finding: conceptual documentation described ambiguous external outcomes as `UNKNOWN`/recovery, while the runtime currently maps provider/publisher exceptions to `FAILED` and has no `UNKNOWN` state.

Resolution: the transition documentation now states the actual runtime behavior and explicitly marks `UNKNOWN` as unimplemented.

Mechanism: evidence hierarchy and fail-closed claims. A mechanism is not considered proven because it is described; implementation and tests must exist.

## Deliberately unresolved, not defects

The following remain bounded limitations rather than silently repaired architecture gaps:

- Runtime restart recovery restores control state and event history, but does not rehydrate execution, verification, acceptance or publication result objects.
- External-effect idempotency is not implemented.
- Queue/worker/lease/retry machinery is not implemented.
- Real OpenAI execution is not proven until the credential is used in an execution environment and the bounded proof command produces evidence.
- Real external publication and observation are not started.

Adding mechanisms for these items without a concrete failure or proof requirement would contradict the project's mechanism-selection rule.

## Closure rule

A future diagnostic finding is closed only when one of the following is true:

1. the implementation and targeted tests prove the mechanism;
2. the documentation is corrected so it no longer claims an unimplemented mechanism;
3. the item is explicitly recorded as a bounded unresolved limitation with a return point.

No diagnostic result should disappear merely because it is inconvenient to implement.
