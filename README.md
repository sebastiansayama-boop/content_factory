# Content Factory

Исследовательская и теперь частично исполняемая среда для проектирования `Content Ecosystem` и `Content Factory`.

Репозиторий содержит модель системы и первый минимальный executable runtime. Runtime пока не является полной production-фабрикой: он предназначен для доказательства контролируемого execution boundary на одном bounded Work Item.

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

Runtime materializes evidence into a workspace filesystem through `ArtifactStore`. Это ещё не означает запись в Git history. Синхронизация workspace evidence с репозиторием выполняется отдельной, явно запускаемой GitHub Actions workflow: `.github/workflows/materialize-runtime.yml`. Эта операция имеет собственную repository-write authority и проверяет scope изменённых файлов перед commit.

Синтетический demo runtime не создаёт `01_observation`: он моделирует publication, но не доказывает внешний эффект.

## 5. Capability and Engineering boundary

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

## 6. First external proof

Минимальное доказательство работы фабрики — один завершённый `Content Work Item`, который проходит от bounded input до авторизованной публикации/доставки, создаёт реально наблюдаемый внешний эффект, а вся цепочка provenance и authority восстанавливаема.

Публикация сама по себе не считается достаточным доказательством: `publication ≠ outcome`.

Runtime v0 может пройти эту цепочку с fake publisher в тесте, но это не является external proof. Для external proof нужен реальный внешний destination.

## 7. Factory Control

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

## 8. Shared Semantic Substrate

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

## 9. Work Item

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

## 10. Research / state / authority foundation

Репозиторий также содержит отдельные модели:

- state model;
- transition matrix;
- dependency and provenance model;
- effect and authority boundaries;
- object lifecycles;
- ontology candidate;
- system map / space map;
- operator navigation;
- repository rules.

Эти модели не должны смешиваться в одну workflow-схему.

## 11. Status

`candidate architecture + implemented Factory Runtime v0`

Runtime v0 является исполняемым, но production readiness и первый реальный external proof пока не доказаны.
