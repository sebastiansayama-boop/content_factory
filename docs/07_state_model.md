# 07 — State Model

This document turns the synthesis into an operational conceptual state model.

It is implementation-independent: states and transitions are defined so that real editorial cases can be executed against them before a database or runtime exists.

## 1. State is not just a stage

A significant state is represented conceptually as:

```text
OBJECT
+ OBJECT_ID
+ REVISION
+ LIFECYCLE_STATE
+ BOUND_INPUTS
+ EVIDENCE_BINDING
+ OWNER
+ AUTHORITY
```

Therefore:

```text
ASSET A12 revision 3 / ACCEPTED
```

is materially different from:

```text
ASSET A12 revision 4 / DRAFT
```

## 2. Object-specific state

There is no single global status field for the whole editorial system.

The lifecycle of an `Asset`, `Publication`, `Observation`, and `Learning` is different because they are different objects.

The canonical machine-readable model is in `model/state-machine.yaml` and the object-by-object explanation is in `docs/11_object_lifecycles.md`.

## 3. Case-level reference flow

A case may present its work as this derived view:

```text
SIGNAL
  ↓
CANDIDATE
  ↓
RESEARCH
  ↓
KNOWLEDGE REVISION
  ↓
EDITORIAL DECISION
  ↓
CONTENT SPEC REVISION
  ↓
ASSET REVISION
  ↓
VERIFICATION RESULT
  ↓
ACCEPTANCE
  ↓
RELEASE
  ↓
PUBLICATION
  ↓
OBSERVATION
  ↓
LEARNING / NEW EVIDENCE
  ↺
```

This is a **case projection**, not a universal lifecycle of one object.

## 4. State ownership

Ownership is attached to the state boundary.

| Object | Primary owner | Authority boundary |
|---|---|---|
| Candidate | Discovery | admit / hold / reject |
| Research | Research | define sufficiency / inconclusive |
| Knowledge revision | Research | establish and revalidate sufficiency |
| Editorial decision | Editorial | proceed / hold / reject / update |
| Content specification | Content Design | make production contract ready |
| Asset revision | Production | deliver specified form |
| Verification result | Verification | pass / fail against exact revision |
| Acceptance decision | designated approver | accept / reject exact revision |
| Release | Publication | assemble / hold / publish / retire |
| Observation | Observation | preserve observed signal |
| Learning | Learning / Editorial | accept or reject interpretation for reuse |

## 5. State invariants

### S1 — Revision binding

Every verification, acceptance, or publication decision must identify the exact revision concerned.

### S2 — No silent promotion

A result does not become accepted merely because the producing process completed.

### S3 — No silent factual expansion

Production may not create new factual claims without making the change visible and sending it back to the appropriate verification/research boundary.

### S4 — Unknown remains explicit

An unresolved fact remains `UNKNOWN` / unresolved and is never silently filled by inference.

### S5 — History is append-only conceptually

Previous states remain recoverable even when a newer revision becomes current.

### S6 — External effect is explicit

`PUBLISHED` means an external effect actually occurred. It is not equivalent to `ACCEPTED` or `READY`.

### S7 — Learning is not automatically knowledge

An interpretation of observations remains a learning candidate until separately accepted for reuse in knowledge or editorial decisions.

### S8 — One object, one lifecycle

`Observation` must not become a status of `Publication`; `Learning` must not become a status of `Observation`; `Acceptance` must not become a hidden state of `Verification`.

## 6. Revision rule

A material change to an accepted or published object produces a new revision.

```text
ACCEPTED revision 2
        ↓ material change
DRAFT revision 3
```

Revision 2 remains historical and traceable.

## 7. Current state versus history

For every stateful object, two views are required conceptually:

```text
HISTORY
  = ordered prior revisions and transitions

CURRENT
  = latest valid projection of that history
```

A current-state view must never erase historical evidence.

## 8. Minimum state card

A case must be able to represent a state with at least:

```text
object_type
object_id
revision_id
lifecycle_state
created_from
depends_on
verified_against
accepted_against
owner
authority
status_reason
evidence_refs
previous_revision
```

The implementation format is intentionally undecided.
