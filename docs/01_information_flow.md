# 01 — Information Flow

## 1. Единица проектирования

Основная единица этой системы — не должность и не публикация.

Это переход:

```text
INPUT STATE → OPERATION → OUTPUT STATE
```

Каждый переход должен отвечать на четыре вопроса:

1. Что известно на входе?
2. Что происходит с этой информацией?
3. Что становится известно после операции?
4. Кто или что имеет право изменить следующий state?

## 2. Четыре связанных потока

### Signal flow

```text
WORLD → SIGNAL → QUESTION → CANDIDATE
```

Назначение: определить, что потенциально заслуживает внимания.

### Knowledge flow

```text
SOURCE → EVIDENCE → CLAIM → CONTEXT/RELATIONS → KNOWLEDGE
```

Назначение: сформировать проверяемое представление о том, что известно.

### Value flow

```text
KNOWLEDGE → EDITORIAL DECISION → CONTENT SPEC → ASSET → PUBLICATION
```

Назначение: превратить выбранное знание в конкретный результат для аудитории.

### Learning flow

```text
PUBLICATION → OBSERVATION → LEARNING → KNOWLEDGE / DISCOVERY / DECISION
```

Назначение: вернуть последствия действия системы в следующий цикл.

## 3. Knowledge layer

Knowledge layer является общим слоем, а не одноразовым этапом pipeline.

```text
                    KNOWLEDGE
          ┌────────────┼────────────┐
          ↓            ↓            ↓
       Research     Feedback     Updates
          │            │            │
          └────────────┼────────────┘
                       ↓
                 Editorial work
```

Один claim может использоваться несколькими editorial decisions и несколькими assets.

## 4. Production как projection

Asset является представлением выбранного знания для конкретной аудитории, цели и канала.

```text
CLAIM C17
   ↓
EDITORIAL DECISION
   ↓
CONTENT SPEC
   ↓
CAROUSEL
   ↓
SLIDE 4
```

При этом traceability должна сохраняться:

```text
SLIDE 4 → CLAIM C17 → EVIDENCE E17 → SOURCE S03
```

## 5. Pull principle

Наличие знания не создаёт автоматически production demand.

```text
EDITORIAL NEED
      ↓
REQUEST RELEVANT KNOWLEDGE
      ↓
PRODUCTION
```

Knowledge может существовать без публикации.

## 6. Handoff principle

Передаётся не «документ от человека человеку», а определённое состояние информации.

Переход должен иметь:

```text
state
owner
input contract
output contract
decision authority
traceability
```

## 7. Return paths

Поток не является линейным.

```text
VERIFICATION
   ├── ACCEPT → PUBLICATION
   ├── REVISE → PRODUCTION
   └── KNOWLEDGE GAP → RESEARCH

OBSERVATION
   ├── NEW SIGNAL → DISCOVERY
   ├── NEW EVIDENCE → KNOWLEDGE
   └── EDITORIAL LEARNING → DECISION
```

## 8. Базовый инвариант

Производная форма не должна незаметно становиться новым источником фактов.

Если production добавил factual claim, которого нет в approved knowledge, это должно быть обнаружимо как изменение или нарушение границы.
