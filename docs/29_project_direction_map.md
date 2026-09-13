# 29 — Project Direction Map

Status: `CURRENT / NAVIGATION ARTIFACT`

This map preserves the project's active, parked, completed and unresolved directions so that context can be transferred without losing the path back to unfinished work.

## Main roadmap

```text
1. Durable Runtime
      ↓
2. Real Execution
      ↓
3. Real External Effect
      ↓
4. Reliability & Control
      ↓
5. Factory Control Plane
      ↓
6. Operations & Governance
      ↓
7. Learning Loop
```

The roadmap is directional, not proof. Completion status is supported by executable evidence and repository records, not by this map alone.

## 01 — Durable Runtime

- Goal: durable control state, atomic state/event transitions and restart reconstruction.
- Status: `COMPLETED`.
- Current checkpoint: Phase 1 implementation is present in `src/content_factory/runtime_store.py` and covered by runtime tests.
- Proven: SQLite control state, append-only event journal, atomic transition+event transaction, restart recovery and CI verification.
- Unproven: production-scale distributed reliability; multi-worker coordination; external-effect idempotency.
- Research needed: only when a new reliability boundary is proposed.
- Dependencies: runtime contracts and tests.
- Blocked by: none for bounded Phase 1 scope.
- Next legitimate step: return only if later phases expose a durable-runtime gap.
- Return point: Phase 1 runtime tests and `docs/23_content_factory_operating_model.md`.

## 02 — Real Execution

- Goal: prove that a factory capability can cross a real provider boundary and produce a revision-bound execution result that can be verified.
- Status: `ACTIVE`.
- Current checkpoint: provider boundary exists for OpenAI Responses API; real credential, connectivity, real execution and revision-bound verification remain to be observed in an execution environment.
- Proven: provider adapter contract, capability binding, secret environment boundary, unit mapping tests and opt-in external proof command.
- Unproven: real provider call in the current execution environment; real response capture; complete Phase 2 external proof.
- Research needed: provider/tool boundary questions only where unresolved.
- Dependencies: compute environment, secret mechanism, `OPENAI_API_KEY`, network access, provider availability.
- Blocked by: physical execution-environment setup after the local system reset, if not already restored.
- Next legitimate step: restore the execution environment, inject the credential without exposing it to chat or repository, run the bounded proof command, capture only the resulting proof/error, then verify the repository evidence.
- Return point: `scripts/prove_openai_execution.py`, `src/content_factory/openai_adapter.py`, `src/content_factory/openai_capability.py`.

## 03 — Real External Effect

- Goal: prove one authorized publication/delivery to a real external destination and distinguish delivery from observable outcome.
- Status: `PARKED / NOT STARTED`.
- Current checkpoint: runtime has an injected publisher boundary; synthetic publication is explicitly not external proof.
- Proven: publication/effect/observation semantic separation.
- Unproven: real destination, authorization chain, idempotency and externally observable effect.
- Research needed: destination-specific integration and effect semantics.
- Dependencies: Phase 2 real execution; explicit release authority; real external destination.
- Blocked by: Phase 2 closure and choice of first real destination.
- Next legitimate step: select one bounded external destination and define its authority/effect proof boundary.
- Return point: `docs/26_first_external_proof.md` and `08_effects_feedback/`.

## 04 — Reliability & Control

- Goal: introduce reliability mechanisms only where a demonstrated case requires them.
- Status: `PARKED / NOT STARTED`.
- Current checkpoint: no queue/worker/lease/recovery expansion has been justified by a current case.
- Proven: bounded single-node durable runtime.
- Unproven: worker concurrency, retries, idempotency, crash recovery across external effects.
- Research needed: concrete mechanism comparison before adding new primitives.
- Dependencies: real execution/effect cases.
- Blocked by: insufficient concrete failure cases.
- Next legitimate step: derive the first reliability requirement from a real execution/effect failure or an explicitly bounded test case.
- Return point: `model/content-factory-map.yaml` known limits.

## 05 — Factory Control Plane

- Goal: control priority, routing, WIP, queues, capacity, scheduling, ownership, orchestration and bottlenecks.
- Status: `PARKED / NOT STARTED`.
- Current checkpoint: conceptual control-plane boundary exists; no dedicated control-plane implementation is claimed.
- Proven: separation of factory control from content truth.
- Unproven: operational control mechanisms and measurable service behavior.
- Research needed: real production-control mechanisms before implementation.
- Dependencies: sufficient production flow to expose control problems.
- Blocked by: current bounded runtime scope.
- Next legitimate step: observe a concrete flow-control problem and research proven mechanisms for it.
- Return point: `README.md` Factory Control section and `model/content-factory-map.yaml`.

## 06 — Operations & Governance

- Goal: make repository, external integrations, authority, observability and operational procedures reliable enough for sustained use.
- Status: `PARKED / NOT STARTED`.
- Current checkpoint: repository governance is explicit in `RULES.md` and `docs/25_chat_repository_operating_protocol.md`.
- Proven: governance protocol and explicit authority boundaries in the model.
- Unproven: operational maturity under sustained real-world use.
- Research needed: concrete operational boundary questions.
- Dependencies: real integrations and observed operating load.
- Blocked by: lack of sustained external operation.
- Next legitimate step: convert a demonstrated operational failure or recurring burden into a bounded mechanism proposal.
- Return point: `RULES.md`, `docs/25_chat_repository_operating_protocol.md`.

## 07 — Learning Loop

- Goal: connect external effects and feedback to interpretation, learning, knowledge and explicit future decisions.
- Status: `ACTIVE RESEARCH / EXTERNAL PROOF PENDING`.
- Current checkpoint: Program 1 external research is complete and has produced a bounded model evolution. The machine-readable model now distinguishes knowledge validity, applicability, retrieval, use, decision impact, execution impact, external outcome and subsequent knowledge evaluation.
- Proven externally: observation/evidence/interpretation separation; need for validity and generalizability limits; retrieval distinct from application; contradiction requires evidence evaluation; stale knowledge and deliberate challenge/unlearning are real concerns; memory retrieval is a security boundary.
- Proven in project: learning candidate creation, explicit promotion, reusable memory creation, bounded memory consumption and decision change in the Q19–Q21 path.
- Unproven: memory changing execution; real external outcome from memory-informed execution; outcome evaluating memory; real contradiction-driven revision; successful cross-context transfer; product/business improvement.
- Research record: `10_records/2026-09-13-learning-loop-program-1-research-synthesis.md`.
- Decision: `05_decision/2026-09-13-program-1-learning-loop-model-evolution.md`.
- Dependencies: Phase 2 real execution and Phase 3 real external effect.
- Blocked by: absence of a completed real external effect proof.
- Next legitimate step: complete the first bounded real external case and capture expected state, actual state, outcome, attribution confidence and memory effect; then test whether the result can trigger a justified knowledge revision.
- Return point: `09_learning/`, `08_effects_feedback/`, and `10_records/2026-09-13-learning-loop-program-1-research-synthesis.md`.

## Open questions

1. What is the smallest real external destination that can close the first end-to-end proof without introducing unnecessary infrastructure?
2. Which external integration boundary should be tested first after real OpenAI execution: publisher, storage, or workflow orchestration such as n8n?
3. Which reliability mechanism is actually justified by the first real failure mode?
4. Which creative and editorial patterns become reusable knowledge after controlled experiments rather than one-off successes?
5. What evidence should be required before a learning candidate is promoted into reusable memory or a model change?
6. What evidence is sufficient to claim that a memory-informed decision changed execution and external outcome?
7. How should a contradictory outcome change memory without collapsing contradiction, staleness, scope change and supersession into one state?
8. What evidence is required before knowledge can transfer across providers, workflows or projects?
9. Which learning controls can be automated without granting automatic authority?
10. What measurable bottleneck would justify a new retrieval or memory infrastructure mechanism?

## Return points

| Direction | Return point | Meaning |
|---|---|---|
| Real Execution | `scripts/prove_openai_execution.py` | Resume Phase 2 proof from provider boundary. |
| Real External Effect | `docs/26_first_external_proof.md` | Define the first real publication/effect proof. |
| Reliability & Control | `model/content-factory-map.yaml` known limits | Start from an observed limitation, not an assumed architecture. |
| Factory Control Plane | `README.md` Factory Control | Resume when flow-control problems are evidenced. |
| Operations & Governance | `RULES.md` + `docs/25_chat_repository_operating_protocol.md` | Resume from operating-boundary questions. |
| Learning Loop | `09_learning/` + `08_effects_feedback/` | Resume from the first real external outcome and its feedback into knowledge. |

## Map invariant

The map must be updated after a material direction changes status, checkpoint, proven state, unresolved state, dependency or return point.

A parked direction remains visible. A completed direction remains reconstructable. A superseded direction is not silently deleted.
