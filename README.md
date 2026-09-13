# Content Factory

Исследовательская и частично исполняемая среда для проектирования `Content Ecosystem` и `Content Factory`.

Репозиторий завершил bounded v0 и первую эксплуатационную фазу: модель системы, операционные контракты зон, executable runtime, evidence materialization, durable runtime control state, integration boundary и CI-проверки согласованы между собой. Phase 2 — Real Execution — сейчас реализуется через реальный provider boundary; production readiness и реальный внешний эффект по-прежнему не заявляются.

## 1. Current system hierarchy

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
│
├── CAPABILITY SYSTEM
│
├── ENGINEERING SYSTEM
│   ├── DOMAIN MODEL
│   ├── EXECUTION
│   ├── STORAGE
│   ├── INTEGRATION
│   ├── GOVERNANCE
│   ├── OBSERVABILITY
│   └── INFRASTRUCTURE
│
└── EXPERIENCE / CHANNELS
```

`Content Factory` — одна функциональная система внутри `Content Ecosystem`. Capability и Engineering — execution layers, которые позволяют фабрике использовать абстрактные способности без прямой зависимости от конкретных инструментов и провайдеров.

## 2. Integrated operating model

Основной документ: `docs/23_content_factory_operating_model.md`.

Модель Capability / Engineering layers: `docs/24_capability_and_engineering_layer.md`.

Исполняемый Runtime v0: `docs/27_factory_runtime_v0.md`.

Критерий первого внешнего доказательства работы: `docs/26_first_external_proof.md`.

Верхнеуровневая модель экосистемы: `docs/22_content_ecosystem_model.md`.

Исследовательски выведенная модель фабрики: `docs/21_content_factory_level_model.md`.

Машинно-читаемая карта фабрики: `model/content-factory-map.yaml`.

Проектная operating memory: `docs/28_project_operating_memory.md`.

Карта направлений и return points: `docs/29_project_direction_map.md`.

Машинно-читаемая карта направлений: `model/project-direction-map.yaml`.

## 3. Factory value flow

```text
STRATEGIC DEMAND + EXTERNAL CONTEXT
                ↓
             INPUT
                ↓
           KNOWLEDGE
                ↓
           EDITORIAL
                ↓
           PRODUCTION
                ↓
             QUALITY
                ↓
          DISTRIBUTION
                ↓
          EXTERNAL EFFECT
                ↓
            LEARNING
                ↺
```

Это projection потока ценности, а не единая state machine.

## 4. Executable Runtime v0

Минимальный runtime реализует один контролируемый execution path:

```text
WORK ITEM
   ↓
RECEIVED
   ↓ ADMIT
ADMITTED
   ↓ EXECUTE CAPABILITY
PRODUCED
   ↓ VERIFY EXACT REVISION
VERIFIED
   ↓ ACCEPT + AUTHORITY
ACCEPTED
   ↓ RELEASE AUTHORITY
RELEASE_READY
   ↓ RELEASE
RELEASED
   ↓ PUBLISHER
DELIVERED
   ↓ OBSERVABLE EFFECT
OBSERVED
```

Реализация: `src/content_factory/runtime.py`.

Тесты: `tests/test_runtime.py`.

Runtime v0 намеренно ограничен одним capability и injected publisher. Без publisher внешний эффект невозможен. Execution result не становится accepted content автоматически.

Runtime materializes evidence into a workspace filesystem through `ArtifactStore`. Это не означает запись в Git history. Синхронизация workspace evidence с репозиторием выполняется отдельной workflow: `.github/workflows/materialize-runtime.yml`.

Синтетический demo runtime не создаёт `01_observation`: он моделирует publication, но не доказывает внешний эффект.

## 5. Durable runtime — Phase 1

`RuntimeStore` добавляет отдельный слой durable control state:

```text
RuntimeStore
    ↓
work-item state + append-only event journal
    ↓
atomic state/event transaction
    ↓
process restart
    ↓
state + event history reconstruction
```

Это не замена `ArtifactStore`. `RuntimeStore` нужен для восстановления управляющего состояния; `ArtifactStore` остаётся projection доказательств в workspace.

Phase 1 проверена тестами на restart recovery и атомарную фиксацию перехода вместе с событием. Используется SQLite WAL с `synchronous=FULL` для bounded single-node runtime.

## 6. Real Execution — Phase 2

Первый реальный provider boundary реализован для OpenAI Responses API:

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

Секретная граница: `OPENAI_API_KEY`; raw key не входит в repository, provenance или logs. Для модели по умолчанию используется `gpt-5.6-luna`.

Unit-тесты проверяют provider boundary и mapping ответа в `ExecutionResult`. Есть отдельный opt-in external test: `tests/test_external_openai.py`.

Phase 2 пока не завершена: требуется реальный credential в execution environment, connectivity test, реальный capability execution и revision-bound verification. Эти шаги нельзя считать выполненными по unit-тестам.

## 7. Capability and Engineering boundary

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

Factory формулирует требуемый результат и capability. Engineering отвечает за контролируемое исполнение. Concrete tools/providers являются заменяемыми реализациями.

Ключевое правило:

```text
CAN EXECUTE
≠ CAN AUTHORIZE
≠ CAN PUBLISH
```

## 8. First external proof

Минимальное доказательство работы фабрики — один завершённый `Content Work Item`, который проходит от bounded input до авторизованной публикации/доставки, создаёт реально наблюдаемый внешний эффект, а вся цепочка provenance и authority восстанавливаема.

Публикация сама по себе не считается достаточным доказательством: `publication ≠ outcome`.

Runtime v0 может пройти эту цепочку с fake publisher в тесте, но это не является external proof. Для external proof нужен реальный внешний destination.

## 9. Factory Control

Factory Control — control plane над семью системами потока:

```text
priority
routing
WIP / queues
capacity
scheduling
ownership
service expectations
orchestration
bottleneck management
```

Она управляет движением работы, но не является источником истины контента.

## 10. Shared Semantic Substrate

Общий смысловой слой:

```text
identity
revisions
structured content
knowledge graph
claims / evidence
provenance
dependencies
audience / taxonomy metadata
reusable components
```

Он используется всеми системами и не является отдельной стадией workflow.

## 11. Work Item

Основная единица производственного потока — `Content Work Item` / `Work Package`.

```text
WORK ITEM
├── strategic intent
├── audience context
├── objective
├── requested outcome
├── inputs
├── knowledge basis
├── dependencies
├── capabilities
├── owner
├── priority
├── constraints
├── acceptance criteria
├── release requirements
└── success signals
```

Основные различия:

```text
WORK ITEM ≠ REQUEST
WORK ITEM ≠ ASSET
WORK ITEM ≠ RELEASE
WORK ITEM ≠ PUBLICATION
CAPABILITY ≠ TOOL
EXECUTION RESULT ≠ ACCEPTED CONTENT
```

## 12. Project operating memory

Репозиторий сохраняет не только текущую архитектуру, но и опыт, необходимый для продолжения работы после смены контекста.

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

`PROJECT MAP` и `CURRENT CHECKPOINT` различаются: карта сохраняет направления и return points, checkpoint фиксирует точное место остановки.

Правила этого слоя: `docs/28_project_operating_memory.md`.

Карта направлений: `docs/29_project_direction_map.md`.

Правила взаимодействия chat ↔ repository: `docs/25_chat_repository_operating_protocol.md`.

## 13. Research / state / authority foundation

Репозиторий содержит отдельные модели:

- state model;
- transition matrix;
- dependency and provenance model;
- effect and authority boundaries;
- object lifecycles;
- ontology candidate;
- system map / space map;
- operator navigation;
- repository rules;
- project direction map;
- project operating memory.

Эти модели не смешиваются в одну workflow-схему.

## 14. Status

`PHASE 1 COMPLETE / PHASE 2 IN PROGRESS / PRODUCTION NOT CLAIMED`

Завершены bounded v0 и Phase 1 durable runtime: Work Item → execution → revision-bound verification → explicit acceptance → release authority → injected publication → optional external observation; evidence materialization; SQLite control-state persistence; append-only event journal; restart reconstruction; CI verification.

Phase 2 имеет реализованный provider boundary для OpenAI Responses API и opt-in real-execution test, но её внешний proof ещё не завершён.

Последовательность следующих фаз:

```text
1 durable runtime                COMPLETE
2 real execution                 IN PROGRESS
3 real external effect           NOT STARTED
4 reliability and control        NOT STARTED
5 factory control plane          NOT STARTED
6 operations and governance      NOT STARTED
7 learning loop                  NOT STARTED
```

Ни одна последующая граница не считается выполненной документацией или fake publisher.
