# 03 — Working Context

Temporary context for one bounded task or case.

## Purpose

`03_working_context` is the active context required to execute one bounded work item. It combines selected inputs, evidence, constraints and objectives without pretending that the selection is durable truth.

## Minimum work-item context

```text
work_item_id
revision_id
objective
requested_outcome
input_refs
knowledge_basis_refs
active_question_or_specification
constraints
dependencies
required_capabilities
owner
priority
acceptance_criteria
release_requirements
success_signals
current_stage
```

The context should reference durable objects instead of copying them where practical.

## Lifecycle

A working context is created when an input has been admitted as actionable work. It may be updated while the work item remains active.

Typical progression:

```text
INTAKE
→ CONTEXTUALIZED
→ READY
→ IN_PROGRESS
→ BLOCKED / WAITING
→ COMPLETED / REJECTED / CANCELLED
```

These are work-item control states, not claims about content truth.

## Relationship to other zones

```text
inbox → working context
memory → working context
observation → working context
working context → reasoning / decision / production / verification
```

A work item may reference evidence from several zones. The context must state which evidence is actually being used.

## Invariants

- Context is bounded to one work item or case.
- It is not durable truth merely because it is active.
- Selected evidence must remain traceable to its source and revision.
- Changes to objective, scope, acceptance criteria or release requirements must be explicit.
- Completion of a work item does not automatically promote its outputs to memory, acceptance or publication.

## Completion criterion

A working context is complete when the work item has a stable identity, explicit requested outcome, bounded scope, required inputs, dependencies, acceptance criteria and current control state.

This zone is the operational bridge between intake and concrete work; it is not a replacement for decision, production or history records.