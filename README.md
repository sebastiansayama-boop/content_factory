# Content Factory

Исследовательская среда для проектирования `Content Ecosystem` и `Content Factory`.

Репозиторий не является реализацией контентного продукта. Его задача — сделать наблюдаемой и проверяемой модель системы, которая связывает стратегический контекст, аудиторию/рынок, производство контента, выпуск, внешние эффекты и обучение.

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

## 4. Capability and Engineering boundary

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

## 5. Factory Control

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

## 6. Shared Semantic Substrate

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

## 7. Work Item

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

## 8. Research / state / authority foundation

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

## 9. Status

`candidate / integrated working model`

Текущая модель должна быть проверена на реальных production cases до выбора конкретной implementation architecture.
