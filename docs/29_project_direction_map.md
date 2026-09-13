# 29 — Project Direction Map

Status: `CURRENT / NAVIGATION ARTIFACT`

The roadmap is directional, not proof. Completion status is supported by executable evidence and repository records, not by this map alone.

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

## 01 — Durable Runtime

- Goal: durable control state, atomic state/event transitions and restart reconstruction.
- Status: `COMPLETED`.
- Current checkpoint: Phase 1 implementation is present in `src/content_factory/runtime_store.py` and covered by runtime tests.
- Proven: SQLite control state, append-only event journal, atomic transition+event transaction, restart recovery and CI verification.
- Unproven: production-scale distributed reliability; multi-worker coordination; external-effect idempotency.
- Next legitimate step: return only if later phases expose a durable-runtime gap.
- Return point: Phase 1 runtime tests and `docs/23_content_factory_operating_model.md`.

## 02 — Real Execution

- Goal: prove that a factory capability can cross a real provider boundary and produce a revision-bound execution result that can be verified.
- Status: `ACTIVE`.
- Current checkpoint: provider boundary exists for OpenAI Responses API; real credential, connectivity, real execution and revision-bound verification remain to be observed in an execution environment.
- Proven: provider adapter contract, capability binding, secret environment boundary, unit mapping tests and opt-in external proof command.
- Unproven: real provider call in the current execution environment; real response capture; complete Phase 2 external proof.
- Research needed: unresolved provider/tool boundary questions only.
- Dependencies: compute environment, secret mechanism, `OPENAI_API_KEY`, network access, provider availability.
- Next legitimate step: run the bounded OpenAI proof with the credential kept out of chat and repository, then record only proof output/error.
- Return point: `scripts/prove_openai_execution.py`, `src/content_factory/openai_adapter.py`, `src/content_factory/openai_capability.py`.

## 03 — Real External Effect

- Goal: prove one authorized publication/delivery to a real external destination and distinguish delivery from observable outcome.
- Status: `PARKED / NOT STARTED`.
- Current checkpoint: runtime has an injected publisher boundary; synthetic publication is explicitly not external proof.
- Proven: publication/effect/observation semantic separation.
- Unproven: real destination, authorization chain, idempotency and externally observable effect.
- Research needed: destination-specific integration and effect semantics.
- Dependencies: Phase 2 real execution; explicit release authority; real external destination.
- Next legitimate step: select one bounded external destination and define its authority/effect proof boundary.
- Return point: `docs/26_first_external_proof.md` and `08_effects_feedback/`.

## 04 — Reliability & Control

- Goal: introduce reliability mechanisms only where a demonstrated case requires them.
- Status: `PARKED / NOT STARTED`.
- Proven: bounded single-node durable runtime.
- Unproven: worker concurrency, retries, idempotency, crash recovery across external effects.
- Next legitimate step: derive the first reliability requirement from a real failure or explicitly bounded failure test.
- Return point: `model/content-factory-map.yaml` known limits.

## 05 — Factory Control Plane

- Goal: control priority, routing, WIP, queues, capacity, scheduling, ownership, orchestration and bottlenecks.
- Status: `PARKED / NOT STARTED`.
- Current checkpoint: conceptual control-plane boundary exists; no dedicated control-plane implementation is claimed.
- Proven: separation of factory control from content truth.
- Unproven: operational control mechanisms and measurable service behavior.
- Next legitimate step: observe a concrete flow-control problem and research proven mechanisms for it.
- Return point: `README.md` Factory Control section and `model/content-factory-map.yaml`.

## 06 — Operations & Governance

- Goal: make repository, external integrations, authority, observability and operational procedures reliable enough for sustained use.
- Status: `PARKED / NOT STARTED`.
- Current checkpoint: repository governance is explicit in `RULES.md` and `docs/25_chat_repository_operating_protocol.md`.
- Proven: governance protocol and explicit authority boundaries in the model.
- Unproven: operational maturity under sustained real-world use.
- Next legitimate step: convert a demonstrated operational failure or recurring burden into a bounded mechanism proposal.
- Return point: `RULES.md`, `docs/25_chat_repository_operating_protocol.md`.

## 07 — Learning Loop

- Goal: connect external effects and feedback to interpretation, learning, knowledge and explicit future decisions.
- Status: `ACTIVE RESEARCH / EXTERNAL PROOF PENDING`.
- Current checkpoint: Program 1 external research is complete; Q19–Q21 demonstrated a bounded learning path from research to promoted memory, memory consumption and decision change. Real external outcome feedback remains unproven.
- Externally supported: provenance and explicit derivation; measurement/validity limits; retrieval distinct from application; contradiction requires evaluation; stale knowledge and deliberate challenge/unlearning are legitimate concerns; memory can be a security boundary.
- Project-demonstrated: learning candidate creation, explicit promotion, reusable memory creation, bounded memory consumption and decision change in Q19–Q21.
- Unproven: memory changing execution; real external outcome from memory-informed execution; outcome evaluating memory; real contradiction-driven revision; successful cross-context transfer; product/business improvement.
- Research record: `10_records/2026-09-13-learning-loop-program-1-research-synthesis.md`.
- Audit record: `10_records/2026-09-13-repository-external-evidence-audit.md`.
- Decision: `05_decision/2026-09-13-program-1-learning-loop-model-evolution.md`.
- Next legitimate step: complete the first bounded real external case and capture expected state, actual state, outcome, attribution confidence and memory effect.
- Return point: `09_learning/`, `08_effects_feedback/`, and the learning-loop research record.

## Open questions

1. Which bounded real external destination should close the first end-to-end proof?
2. Which integration boundary should be tested first after real OpenAI execution: publisher, storage, or workflow orchestration such as n8n?
3. Which reliability mechanism is justified by the first real failure mode?
4. Which creative/editorial patterns become reusable knowledge after controlled experiments rather than one-off successes?
5. What evidence is sufficient before a learning candidate is promoted or a model is changed?
6. What evidence is sufficient to claim that a memory-informed decision changed execution and external outcome?
7. How should contradictory outcomes change memory without collapsing contradiction, staleness, scope change and supersession?
8. What evidence is required before knowledge transfers across providers, workflows or projects?
9. Which learning controls can be automated without granting automatic authority?
10. What measurable bottleneck would justify new retrieval or memory infrastructure?

## Return points

| Direction | Return point |
|---|---|
| Real Execution | `scripts/prove_openai_execution.py` |
| Real External Effect | `docs/26_first_external_proof.md` |
| Reliability & Control | `model/content-factory-map.yaml` known limits |
| Factory Control Plane | `README.md` Factory Control |
| Operations & Governance | `RULES.md` + `docs/25_chat_repository_operating_protocol.md` |
| Learning Loop | `09_learning/` + `08_effects_feedback/` |

## Map invariant

The map must be updated after a material direction changes status, checkpoint, proven state, unresolved state, dependency or return point. A parked direction remains visible; a completed direction remains reconstructable; a superseded direction is not silently deleted.
