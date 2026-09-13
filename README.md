# Content Factory

Экспериментальная среда для исследования editorial knowledge system и production system.

Репозиторий не является реализацией контентного продукта. Его задача — сделать наблюдаемой модель того, как информация возникает, изменяется, принимается, превращается в производный материал и возвращается в следующий цикл.

## Уровни модели

Репозиторий теперь рассматривается на нескольких уровнях:

```text
SYSTEM SPACE
  ↓
ONTOLOGY
  ↓
FUNCTIONAL NETWORK
  ↓
OBJECT / STATE / DEPENDENCY / AUTHORITY
  ↓
FOLDERS / RECORDS / CASES
```

### Ontology

Ontology отвечает на вопрос:

```text
Что существует в предметной области,
как эти вещи различаются,
какие отношения между ними имеют смысл?
```

Она не является state machine, workflow или схемой папок.

Текущий ontology layer:

- `ontology/00_requirements.md` — scope, requirements и границы.
- `ontology/01_competency_questions.md` — вопросы, которыми проверяется достаточность ontology.
- `ontology/02_term_inventory.md` — inventory терминов и candidate classifications.
- `ontology/03_identity_and_dependence.md` — identity и виды зависимости.
- `ontology/04_relation_analysis.md` — семантика отношений.
- `ontology/05_candidate_model.md` — текущая candidate conceptual ontology.
- `ontology/06_constraints.md` — ограничения и formalization gate.
- `ontology/ontology-map.yaml` — machine-readable candidate map.

Статус ontology: `candidate`. Это сознательно не оформлено как OWL/RDF implementation; сначала модель должна пройти реальные editorial cases и competency-question tests.

### System space

```text
WORLD
  ↓
PERCEPTION
  ↓
REPRESENTATION
  ↓
MODEL
  ↓
POSSIBILITIES
  ↓
DECISION
  ↓
ACTION
  ↓
CONSEQUENCE
  ↓
OBSERVATION
  ↓
MODEL UPDATE
```

### Functional repository level

```text
00_inbox → 01_observation
                 ↓
          02_memory ←→ 04_reasoning
                 ↑          ↓
          03_working_context
                 ↓
             05_decision
                 ↓
            06_production
                 ↓
           07_verification
                 ↓
             05_decision
                 ↓
        08_effects_feedback
                 ↓
           01_observation
                 ↓
             09_learning
              ↙       ↘
         02_memory   04_reasoning

10_records observes the whole system.
model/ = current model.
docs/ = explanation and synthesis.
templates/ = capture contracts.
archive/ = superseded material.
```

Neuroscience is used here only as a functional analogy. Human cognition is supported by interacting distributed networks, not isolated modules.

## Space Map

The operational navigation map is `SPACE_MAP.md`.

Before deciding what to edit, locate the situation by:

```text
SPACE
→ OBJECT
→ STATE / REVISION
→ EVIDENCE
→ DEPENDENCIES
→ AUTHORITY
→ NEXT LEGITIMATE TRANSITION
```

The full navigation procedure is in `docs/19_operator_navigation.md`.

## System space model

`docs/20_system_space.md` defines the repository as a bounded state space with both a state space and an action space. It separates observed reality, represented reality, intended future, committed history and unknown space.

## Editorial trajectory

```text
SIGNAL
  ↓
CANDIDATE
  ↓
RESEARCH
  ↓
KNOWLEDGE
  ↓
EDITORIAL DECISION
  ↓
CONTENT SPECIFICATION
  ↓
PRODUCTION
  ↓
VERIFICATION
  ↓
ACCEPTANCE
  ↓
RELEASE / PUBLICATION
  ↓
OBSERVATION
  ↓
LEARNING / NEW EVIDENCE
  ↺
```

Это не одна глобальная state machine. Каждый значимый object имеет отдельный lifecycle; case-level pipeline является projection над этими lifecycles.

## State model

Значимое состояние определяется комбинацией:

```text
OBJECT
+ REVISION
+ LIFECYCLE STATE
+ BOUND INPUTS
+ EVIDENCE
+ OWNER / AUTHORITY
```

Ontology не определяет lifecycle states; она определяет семантические виды сущностей и отношений, на которые state model накладывается.

## Важные разделения

Knowledge — не публикация.

Asset — не source of truth.

History — не current state.

Review — не acceptance.

Acceptance — не publication.

Observation — не learning.

Learning — не автоматически knowledge truth.

Production result не должен становиться новым фактом только потому, что он хорошо написан или визуализирован.

## Основные карты и правила

- `SPACE_MAP.md` — основная карта пространства для навигации и принятия решений.
- `docs/19_operator_navigation.md` — операционный протокол навигации.
- `docs/20_system_space.md` — state space, action space, constraints, opportunities и system boundary.
- `docs/15_system_level_model.md` — система как bounded cognitive-production loop.
- `docs/16_system_map.md` — highest-level functional map и три пересекающиеся плоскости: information, control, time.
- `docs/17_system_rules.md` — правила системы, расположенные выше отдельных folder rules.
- `RULES.md` — краткая binding-версия правил.
- `docs/12_brain_functional_analogy.md` — ограниченная функциональная аналогия с мозгом.
- `docs/13_repository_structure_and_map.md` — назначение repository zones.
- `docs/14_repository_rules.md` — подробные операционные правила.
- `model/repository-map.md` — компактная карта repository functions.
- `model/state-machine.yaml` — object-specific state machines.

## Остальные модели

- `docs/01_information_flow.md` — information flow.
- `docs/02_primitives.md` — primitives.
- `docs/03_processes.md` — processes.
- `docs/04_decision_points.md` — decisions.
- `docs/05_roles.md` — roles.
- `docs/06_unified_state_dependency_map.md` — synthesis с девятью существующими репозиториями.
- `docs/07_state_model.md` — state semantics.
- `docs/08_transition_matrix.md` — transitions и authority.
- `docs/09_dependency_and_provenance.md` — provenance/dependency/impact.
- `docs/10_effect_and_authority_boundaries.md` — effect boundaries.
- `docs/11_object_lifecycles.md` — отдельные lifecycles.
- `templates/case.md` — case contract.
- `templates/decision.md` — decision contract.

## Как использовать модель

Новый вопрос сначала рассматривается как research question или case.

Новая папка, primitive, state или ontology class не добавляются только потому, что они красиво описывают один пример.

Каждый material case должен позволять восстановить:

```text
world input
→ observation
→ internal model
→ working context
→ reasoning
→ decision
→ action
→ verification
→ external effect
→ consequence
→ learning
→ model update
```

## Статус

Это **working model**. System-level model, ontology candidate model, functional repository map, object-specific state machines, dependency semantics и operational space map являются текущими гипотезами, предназначенными для проверки на реальных editorial cases. Это ещё не окончательная БД или runtime architecture.
