# Content Factory

Исследовательская и частично исполняемая среда для проектирования `Content Ecosystem` и `Content Factory`.

Репозиторий завершил bounded v0 и Phase 1 durable runtime. Phase 2 — Real Execution — реализуется через реальный provider boundary; production readiness и реальный внешний эффект не заявляются.

## Current system hierarchy

```text
CONTENT ECOSYSTEM
│
├── STRATEGY / INTENT
├── AUDIENCE / MARKET
├── PRODUCT / BUSINESS
├── CONTENT FACTORY
│   ├── VALUE FLOW
│   │   ├── INPUT
│   │   ├── KNOWLEDGE
│   │   ├── EDITORIAL
│   │   ├── PRODUCTION
│   │   ├── QUALITY
│   │   ├── DISTRIBUTION
│   │   └── LEARNING
│   ├── FACTORY CONTROL
│   └── SHARED SEMANTIC SUBSTRATE
├── CAPABILITY SYSTEM
├── ENGINEERING SYSTEM
└── EXPERIENCE / CHANNELS
```

`Content Factory` — функциональная система внутри `Content Ecosystem`. Capability и Engineering являются execution layers, позволяющими фабрике использовать абстрактные способности без прямой зависимости от конкретных инструментов и провайдеров.

## Integrated operating model

Основные документы:

- `docs/23_content_factory_operating_model.md`
- `docs/24_capability_and_engineering_layer.md`
- `docs/26_first_external_proof.md`
- `docs/27_factory_runtime_v0.md`
- `docs/28_project_operating_memory.md`
- `docs/29_project_direction_map.md`
- `model/content-factory-map.yaml`
- `model/project-direction-map.yaml`

## Executable Runtime v0

Минимальный runtime реализует контролируемый execution path:

```text
WORK ITEM
   ↓
ADMIT
   ↓
EXECUTE CAPABILITY
   ↓
VERIFY EXACT REVISION
   ↓
ACCEPT + AUTHORITY
   ↓
RELEASE AUTHORITY
   ↓
RELEASE
   ↓
PUBLISHER
   ↓
OBSERVABLE EFFECT
```

Реализация: `src/content_factory/runtime.py`.
Тесты: `tests/test_runtime.py`.

Runtime v0 ограничен одним capability и injected publisher. Без publisher внешний эффект невозможен. Execution result не становится accepted content автоматически. Synthetic/demo publication не считается доказательством внешнего эффекта.

## Durable runtime — Phase 1

`RuntimeStore` предоставляет bounded single-node durable control state:

```text
work-item state + append-only event journal
        ↓
atomic state/event transaction
        ↓
process restart
        ↓
state + event history reconstruction
```

Phase 1 проверена runtime-тестами на restart recovery и атомарную фиксацию перехода вместе с событием. Используется SQLite WAL с `synchronous=FULL`.

## Real Execution — Phase 2

Первый provider boundary реализован для OpenAI Responses API:

```text
WORK ITEM
    ↓
OpenAIResponsesAdapter
    ↓
https://api.openai.com/v1/responses
    ↓
provider response id
    ↓
ExecutionResult
    ↓
output revision
```

Реализация: `src/content_factory/openai_adapter.py`.
Секретная граница: `OPENAI_API_KEY`; raw key не входит в repository, provenance или logs. Default model: `gpt-5.6-luna`.

Unit-тесты проверяют provider boundary и mapping ответа в `ExecutionResult`. Есть opt-in external test: `tests/test_external_openai.py`.

Phase 2 не завершена: требуется реальный credential в execution environment, connectivity test, реальный capability execution и revision-bound verification. Unit-тесты эти шаги не заменяют.

## Capability and Engineering boundary

```text
FACTORY WORK ITEM
        ↓
CAPABILITY REQUEST
        ↓
EXECUTOR
        ↓
PROVIDER ADAPTER
        ↓
TOOL / MODEL / SERVICE / PROVIDER
        ↓
RESULT / EXTERNAL EFFECT
        ↓
VERIFICATION / OBSERVATION
```

Ключевое правило:

```text
CAN EXECUTE
≠ CAN AUTHORIZE
≠ CAN PUBLISH
```

## First external proof

Минимальное внешнее доказательство — завершённый bounded `Content Work Item`, который проходит через авторизованную публикацию/доставку к реальному внешнему destination, создаёт реально наблюдаемый внешний эффект, а provenance и authority chain восстанавливаемы.

`publication ≠ outcome`.

Fake/synthetic publisher не является external proof.

## Project operating memory

Основной цикл:

```text
QUESTION
→ RESEARCH / EXPERIMENT / IMPLEMENTATION
→ EVIDENCE
→ INTERPRETATION
→ LESSON
→ KNOWLEDGE CANDIDATE
→ DECISION
→ WORK / OUTCOME
→ PROJECT MAP UPDATE
```

`PROJECT MAP` и `CURRENT CHECKPOINT` различаются. Правила: `docs/28_project_operating_memory.md`. Chat ↔ repository protocol: `docs/25_chat_repository_operating_protocol.md`.

## Learning Loop — current state

Program 1 external research produced a bounded model evolution. Q19–Q21 demonstrated a project-level path from research to learning candidate, explicit promotion, reusable memory consumption and decision change.

Externally supported principles include provenance, explicit derivation, measurement/validity limits, retrieval/application distinction, contradiction evaluation, stale-knowledge concerns and memory-security concerns. These are external support, not proof that Content Factory is effective in production.

Still unproven:

- memory changing execution;
- real external outcome from memory-informed execution;
- outcome evaluating memory;
- contradiction-driven revision in a real external case;
- successful cross-context transfer;
- product/business improvement.

Research: `10_records/2026-09-13-learning-loop-program-1-research-synthesis.md`.
Audit: `10_records/2026-09-13-repository-external-evidence-audit.md`.
Decision: `05_decision/2026-09-13-program-1-learning-loop-model-evolution.md`.

## Status

`PHASE 1 COMPLETE / PHASE 2 IN PROGRESS / PHASE 3 NOT STARTED / LEARNING LOOP ACTIVE RESEARCH / PRODUCTION NOT CLAIMED`

```text
1 durable runtime                COMPLETE
2 real execution                 IN PROGRESS
3 real external effect           NOT STARTED
4 reliability and control        NOT STARTED
5 factory control plane          NOT STARTED
6 operations and governance      NOT STARTED
7 learning loop                  ACTIVE RESEARCH / EXTERNAL PROOF PENDING
```

No subsequent boundary is considered complete merely because it exists in documentation or uses a fake publisher.
