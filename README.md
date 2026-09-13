# Content Factory

Экспериментальная среда для исследования editorial knowledge system и production system.

Репозиторий не является реализацией контентного продукта. Его задача — сделать наблюдаемой модель того, как информация возникает, изменяется, принимается, превращается в производный материал и возвращается в следующий цикл.

## Исходный принцип

Сначала проектируется **information flow**, затем процессы и decision points, затем ownership и роли. После synthesis state/dependency model становится отдельным слоем. Техническая реализация появляется только тогда, когда модель достаточно определена и выдерживает реальные cases.

## Базовый цикл

```text
WORLD
  ↓
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

## State model

Значимое состояние определяется не одним этапом, а комбинацией:

```text
OBJECT
+ REVISION
+ LIFECYCLE STATE
+ BOUND INPUTS
+ EVIDENCE
+ OWNER / AUTHORITY
```

Поэтому `VERIFIED`, `ACCEPTED` и `PUBLISHED` — разные состояния, а material change создаёт новую revision.

## Важные разделения

Knowledge — не публикация.

Asset — не source of truth.

History — не current state.

Review — не acceptance.

Acceptance — не publication.

Observation — не learning.

Learning — не автоматически knowledge truth.

Production result не должен становиться новым фактом только потому, что он хорошо написан или визуализирован.

## Рабочая модель

```text
IDENTITY
  ↓
EXACT VERSION / STATE
  ↓
BOUND INPUTS
  ↓
OPERATION
  ↓
OBSERVED RESULT
  ↓
REVIEW
  ↓
DECISION
  ↓
EXPLICIT EFFECT
```

Editorial semantics находятся внутри этого control loop:

```text
SOURCE → EVIDENCE → CLAIM → KNOWLEDGE → EDITORIAL INTENT → ASSET → PUBLICATION
```

## Документы

- `docs/01_information_flow.md` — как информация должна перемещаться и преобразовываться.
- `docs/02_primitives.md` — минимальные сущности и их границы.
- `docs/03_processes.md` — процессы, входы, операции, выходы и ownership.
- `docs/04_decision_points.md` — точки, в которых поток может продолжаться, остановиться или вернуться назад.
- `docs/05_roles.md` — роли как следствие информационного потока.
- `docs/06_unified_state_dependency_map.md` — synthesis с девятью существующими репозиториями и классификация универсальных/специализированных паттернов.
- `docs/07_state_model.md` — operational state families, invariants и state cards.
- `docs/08_transition_matrix.md` — допустимые state transitions и authority boundaries.
- `docs/09_dependency_and_provenance.md` — provenance, dependency и invalidation/impact semantics.
- `docs/10_effect_and_authority_boundaries.md` — разделение production, review, acceptance и external effect.
- `model/state-machine.yaml` — машинно-читаемая рабочая версия state machine.
- `templates/case.md` — шаблон реального editorial case.
- `templates/decision.md` — шаблон durable decision record.

## Как использовать модель

Новый вопрос сначала проверяется как research question или case. Нельзя добавлять новое состояние только потому, что оно удобно для описания одного примера. Новое состояние становится частью модели после того, как оно необходимо для нескольких transitions или закрывает наблюдаемый разрыв.

Реальный case должен позволять восстановить:

```text
input
→ object identity
→ exact revisions
→ dependencies
→ operations
→ observed results
→ reviews
→ decisions
→ authorized effects
→ publication / observation
→ learning
```

## Статус

Это **working model**. State machine и dependency semantics являются текущей гипотезой, предназначенной для проверки на реальных editorial cases. Никакая из этих моделей пока не является окончательной БД или runtime architecture.
