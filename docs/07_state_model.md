# 07 — State Model

This document turns the synthesis into an operational conceptual state model.

It is still implementation-independent: states and transitions are defined so that real editorial cases can be executed against them before a database or runtime exists.

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
ASSET A12 revision 3 / VERIFIED
```

is materially different from:

```text
ASSET A12 revision 4 / DRAFT
```

## 2. State families

The system has six state families.

### 2.1 Intake states

```text
SIGNAL
QUESTION
CANDIDATE
```

### 2.2 Knowledge states

```text
RESEARCH_REQUIREMENT
RESEARCH_ACTIVE
KNOWLEDGE_DRAFT
KNOWLEDGE_SUFFICIENT
KNOWLEDGE_INCONCLUSIVE
KNOWLEDGE_AFFECTED
```

### 2.3 Editorial states

```text
EDITORIAL_PENDING
EDITORIAL_PROCEED
EDITORIAL_HOLD
EDITORIAL_REJECT
EDITORIAL_UPDATE
```

### 2.4 Production states

```text
SPEC_DRAFT
SPEC_READY
ASSET_DRAFT
ASSET_READY_FOR_VERIFICATION
ASSET_REVISION_REQUIRED
```

### 2.5 Verification and effect states

```text
VERIFICATION_PENDING
VERIFIED
VERIFICATION_FAILED
ACCEPTED
REJECTED
RELEASE_CANDIDATE
PUBLISHED
PUBLICATION_HELD
RETIRED
```

### 2.6 Learning states

```text
OBSERVED
INTERPRETED
LEARNING_CANDIDATE
LEARNING_ACCEPTED
NEW_EVIDENCE
KNOWLEDGE_UPDATE_REQUIRED
```

## 3. Canonical lifecycle

```text
SIGNAL
  ↓
QUESTION
  ↓
CANDIDATE
  ↓
RESEARCH_REQUIREMENT
  ↓
RESEARCH_ACTIVE
  ↓
KNOWLEDGE_DRAFT
  ↓
KNOWLEDGE_SUFFICIENT
  ↓
EDITORIAL_PENDING
  ↓
EDITORIAL_PROCEED
  ↓
SPEC_READY
  ↓
ASSET_DRAFT
  ↓
ASSET_READY_FOR_VERIFICATION
  ↓
VERIFICATION_PENDING
  ↓
VERIFIED
  ↓
ACCEPTED
  ↓
RELEASE_CANDIDATE
  ↓
PUBLISHED
  ↓
OBSERVED
  ↓
INTERPRETED
  ↓
LEARNING_CANDIDATE
  ↙              ↘
KNOWLEDGE_UPDATE  NEW_EVIDENCE
```

This is a reference lifecycle, not a requirement that every case traverse every state.

## 4. State ownership

Ownership is attached to the state boundary.

| State family | Primary owner | Authority boundary |
|---|---|---|
| Signal / Question | Discovery | create candidate |
| Candidate | Discovery | admit to research |
| Research Requirement | Research | define research stop condition |
| Knowledge | Research | assert knowledge sufficiency |
| Editorial | Editorial | decide whether to produce |
| Specification | Content Design | define production contract |
| Asset | Production | deliver specified form |
| Verification | Verification | report conformity |
| Acceptance | Editorial / designated approver | accept exact revision |
| Release Candidate | Publication owner | authorize external publication |
| Publication | Publication | record external effect |
| Observation | Observation owner | preserve observed signal |
| Learning | Learning / Editorial | interpret observation and propose update |

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

An interpretation of observations remains a hypothesis or learning candidate until separately accepted for use in knowledge or editorial decision-making.

## 6. Terminal and reversible states

The system distinguishes states that normally move forward from states that create a new revision.

```text
ACCEPTED
  ↓
new revision required for material changes

PUBLISHED
  ↓
new publication event or retirement/update

RETIRED
  ↓
terminal for that publication revision
```

A material change should generally create a new revision rather than mutate the accepted or published historical state in place.

## 7. Current state versus history

For every object, two views are required conceptually:

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
