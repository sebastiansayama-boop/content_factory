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
└── EXPERIENCE / CHANNELS
```

`Content Factory` — одна функциональная система внутри `Content Ecosystem`, а не весь ecosystem/business layer.

## 2. Integrated operating model

Основной документ: `docs/23_content_factory_operating_model.md`.

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

## 4. Factory Control

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

## 5. Shared Semantic Substrate

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

## 6. Work Item

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

Work item, asset, release, publication и request — разные сущности.

## 7. Ecosystem boundary

Content Factory получает:

```text
strategic demand
+
audience / market context
+
evidence-backed knowledge
```

и производит:

```text
verified / authorized content releases
```

Далее experience/channel layer производит внешние response/outcome signals, которые могут вернуться выше уровня фабрики.

## 8. Navigation

Перед изменением репозитория использовать:

```text
SYSTEM LEVEL
→ OBJECT
→ STATE / REVISION
→ EVIDENCE
→ DEPENDENCIES
→ AUTHORITY
→ NEXT LEGITIMATE TRANSITION
```

Главная карта: `SPACE_MAP.md`.

Полный протокол: `docs/19_operator_navigation.md`.

System space: `docs/20_system_space.md`.

## 9. Ontology

Ontology отвечает за семантическую вселенную системы:

```text
что существует
как сущности различаются
какие отношения между ними имеют смысл
```

Она не является workflow, state machine или схемой папок.

Папка `ontology/` содержит requirements, competency questions, identity/dependence analysis, relation analysis, candidate model and constraints.

## 10. State / dependency / authority

State model: `model/state-machine.yaml`.

Dependency and provenance: `docs/09_dependency_and_provenance.md`.

Effect and authority boundaries: `docs/10_effect_and_authority_boundaries.md`.

Object lifecycles: `docs/11_object_lifecycles.md`.

## 11. System maps

- `docs/15_system_level_model.md` — nested Ecosystem → Factory boundary.
- `docs/16_system_map.md` — integrated ecosystem/factory map.
- `docs/17_system_rules.md` — system-level binding rules.
- `docs/18_space_map.md` — semantic repository space.
- `docs/19_operator_navigation.md` — operating navigation protocol.
- `docs/20_system_space.md` — nested state/action space.
- `docs/21_content_factory_level_model.md` — evolved factory model.
- `docs/22_content_ecosystem_model.md` — ecosystem model above the factory.
- `docs/23_content_factory_operating_model.md` — integrated operating model.

## 12. Existing research layers

- `docs/01_information_flow.md` — information flow.
- `docs/02_primitives.md` — primitives.
- `docs/03_processes.md` — processes.
- `docs/04_decision_points.md` — decision points.
- `docs/05_roles.md` — roles.
- `docs/06_unified_state_dependency_map.md` — synthesis from nine existing repositories.
- `docs/07_state_model.md` — state semantics.
- `docs/08_transition_matrix.md` — transitions and authority.
- `docs/09_dependency_and_provenance.md` — provenance/dependency/impact.
- `docs/10_effect_and_authority_boundaries.md` — effect boundaries.
- `docs/11_object_lifecycles.md` — object-specific lifecycles.

## 13. Repository projection

```text
00_inbox/                    input / intake
01_observation/              observed signals and effects
02_memory/                   reusable knowledge
03_working_context/          active work item context
04_reasoning/                interpretation
05_decision/                 authority-bearing choices
06_production/               production work
07_verification/             quality assessment
08_effects_feedback/         external effects
09_learning/                 learning candidates
10_records/                  durable history
ontology/                    semantic domain model
model/                       current model and machine-readable maps
docs/                        research and explanation
templates/                   capture contracts
archive/                     inactive history
```

## 14. Core distinctions

```text
Content Ecosystem ≠ Content Factory
Factory Control ≠ Value-flow stage
Semantic substrate ≠ Workflow
Knowledge ≠ Publication
Asset ≠ Source of truth
Work Item ≠ Asset
History ≠ Current state
Review ≠ Acceptance
Acceptance ≠ Publication
Publication ≠ Outcome
Learning ≠ Truth
Folder ≠ Authority
```

## 15. Status

`candidate / integrated working model`

The current architecture is research-derived and must be challenged with real Content Factory cases before implementation hardening. Structural changes require evidence, external research, experiments, case failures or explicit decisions.
