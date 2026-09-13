# 11 — Object Lifecycles

The state model is object-specific. There is no single global lifecycle in which `Publication`, `Observation`, `Learning`, and `Knowledge` are merely successive statuses of one object.

## 1. Why object-specific lifecycles

The same editorial workflow contains several different kinds of stateful objects:

```text
Candidate
Research
Knowledge Revision
Editorial Decision
Content Specification Revision
Asset Revision
Verification Result
Release
Publication
Observation
Learning
Evidence
```

They interact through explicit relations.

They do not share one universal status field.

## 2. Candidate lifecycle

```text
SIGNAL
  ↓
QUESTION
  ↓
CANDIDATE
  ├── ADMITTED
  ├── HELD
  └── REJECTED
```

## 3. Research lifecycle

```text
RESEARCH_REQUIREMENT
  ↓
RESEARCH_ACTIVE
  ├── SUFFICIENT
  ├── INCONCLUSIVE
  └── AFFECTED
          ↓
     RESEARCH_ACTIVE
```

Research is closed only after the relevant result has been handed to the next decision boundary or explicitly marked inconclusive.

## 4. Knowledge revision lifecycle

```text
DRAFT
  ↓
SUFFICIENT
  ├── AFFECTED → revalidation
  └── SUPERSEDED by a new revision
```

Knowledge revisions are snapshots in history. A newer revision does not rewrite the old revision.

## 5. Editorial decision lifecycle

```text
PENDING
 ├── PROCEED
 ├── HOLD
 ├── REJECT
 └── UPDATE_EXISTING
```

A new decision may supersede an earlier decision; the earlier decision remains historical.

## 6. Content specification lifecycle

```text
DRAFT
  ↓
READY
  ↓ upstream change
AFFECTED
  ↓
DRAFT
```

A specification is valid only relative to the upstream knowledge/decision revisions it declares.

## 7. Asset revision lifecycle

```text
DRAFT
  ↓
READY_FOR_VERIFICATION
  ├── REVISION_REQUIRED → DRAFT
  ├── ACCEPTED
  └── REJECTED
```

`ACCEPTED` is a state of the exact asset revision, not a permanent property of the asset identity.

## 8. Verification result lifecycle

```text
PENDING
 ├── PASSED
 └── FAILED

PASSED / FAILED
      ↓ newer relevant revision
   SUPERSEDED
```

A verification result is evidence about a specific revision. It does not automatically transfer to a later revision.

## 9. Release lifecycle

```text
DRAFT
  ↓
READY
 ├── HELD → READY
 └── PUBLISHED
       ├── RETIRED
       └── SUPERSEDED
```

A Release groups exact accepted revisions into one externally meaningful unit.

## 10. Observation lifecycle

Observation starts only after an externally meaningful event or other observable condition exists.

```text
RECORDED
  ↓
INTERPRETED
  ↓
CLOSED
```

Observation is its own object. It does not change the publication's lifecycle state.

## 11. Learning lifecycle

```text
CANDIDATE
 ├── ACCEPTED
 ├── REJECTED
 └── SUPERSEDED
```

Learning is an interpretation that may be accepted for reuse; it is not automatically a factual claim.

## 12. Evidence lifecycle

```text
OBSERVED
  ↓
RELEVANT
 ├── AFFECTED
 │     ↓
 │   INVALID
 └── SUPERSEDED
```

An evidence item may become affected without immediately becoming invalid.

## 13. Cross-object transitions

The editorial workflow is now represented as relations between independent lifecycles:

```text
Candidate
   ↓ produces
Research Requirement
   ↓ informs
Knowledge Revision
   ↓ informs
Editorial Decision
   ↓ produces
Content Specification Revision
   ↓ produces
Asset Revision
   ↓ verified_by
Verification Result
   ↓ accepted_by
Acceptance Decision
   ↓ assembled_into
Release
   ↓ produces
Publication
   ↓ produces
Observation
   ↓ interpreted_as
Learning / New Evidence
```

The critical architectural point is:

```text
OBJECT STATE
≠
WORKFLOW STAGE
```

A workflow stage describes where a case is operating. An object state describes the lifecycle of a particular object revision.

## 14. Case state versus object state

A case may therefore have this high-level view:

```text
CASE-001

Candidate: ADMITTED
Research: SUFFICIENT
Knowledge K8 r5: SUFFICIENT
Editorial Decision D9: PROCEED
Content Spec CS4 r2: READY
Asset A12 r3: ACCEPTED
Verification V7: PASSED
Release R2: READY
Publication P7: PUBLISHED
Observation O3: RECORDED
Learning L1: CANDIDATE
```

No single object owns the entire lifecycle.

The case view is a projection over object states and relations.

## 15. Minimum implementation consequence

Any future implementation should avoid a single `status` field that tries to represent the entire editorial pipeline.

It needs at least:

```text
object identity
object revision
object type
object lifecycle state
relations to other object revisions
```

A case-level status can be derived later from those facts.
