# 09 — Dependency and Provenance Model

The editorial system is a dependency graph. A sequence is only one view over that graph.

## 1. Core relation types

The model distinguishes six relations.

### `produced_from`

Answers:

```text
What information or work produced this object?
```

Example:

```text
ASSET A12 produced_from SPEC CS4
```

### `depends_on`

Answers:

```text
What must remain valid for this object to remain valid?
```

Example:

```text
SPEC CS4 depends_on KNOWLEDGE K8 revision 5
```

### `verified_against`

Answers:

```text
Which exact basis was used to verify this object?
```

Example:

```text
ASSET A12 revision 3 verified_against
  SPEC CS4 revision 2
  KNOWLEDGE K8 revision 5
```

### `accepted_against`

Answers:

```text
Which exact verified state was accepted?
```

Example:

```text
ACCEPTANCE AC7 accepted_against ASSET A12 revision 3
```

### `published_as`

Answers:

```text
Which exact accepted state produced this external publication?
```

Example:

```text
PUBLICATION P7 published_as ASSET A12 revision 3
```

### `supersedes` / `invalidates` / `impacts`

These describe evolution rather than production.

```text
REVISION 4 supersedes REVISION 3
SOURCE S03 invalidates EVIDENCE E17
CLAIM C17 impacts PUBLICATION P7
```

## 2. Provenance versus dependency

These must not be collapsed.

```text
PROVENANCE:
A12 ← CS4 ← K8 ← C17 ← E17 ← S03
```

means:

> where did A12 come from?

Dependency asks the reverse operational question:

```text
S03
 ↓
E17
 ↓
C17
 ↓
K8
 ↓
CS4
 ↓
A12
 ↓
P7
```

and means:

> what becomes affected if S03 changes?

## 3. Minimum dependency graph

```text
SOURCE
  ↓ evidence
EVIDENCE
  ↓ supports / contradicts
CLAIM
  ↓ included_in
KNOWLEDGE REVISION
  ↓ selected_by
EDITORIAL DECISION
  ↓ specified_by
CONTENT SPEC REVISION
  ↓ produced_as
ASSET REVISION
  ↓ verified_against
VERIFICATION RESULT
  ↓ accepted_as
ACCEPTANCE
  ↓ released_as
RELEASE CANDIDATE
  ↓ published_as
PUBLICATION
```

Observations return to the graph:

```text
PUBLICATION
  ↓
OBSERVATION
  ├── NEW_EVIDENCE → EVIDENCE
  ├── CORRECTION → CLAIM REVIEW
  ├── MEASUREMENT → LEARNING
  └── USER_SIGNAL → DISCOVERY
```

## 4. Invalidating event

An upstream change must not silently rewrite downstream objects.

Example:

```text
SOURCE S03 becomes unreliable
        ↓
EVIDENCE E17 = AFFECTED
        ↓
CLAIM C17 = REVIEW_REQUIRED
        ↓
KNOWLEDGE K8 rev 5 = AFFECTED
        ↓
SPEC CS4 rev 2 = IMPACTED
        ↓
ASSET A12 rev 3 = REVIEW_REQUIRED
        ↓
PUBLICATION P7 = REVIEW_REQUIRED
```

The normal response is a review decision, not automatic deletion or automatic rewriting.

## 5. Dependency statuses

Every material dependency should be conceptually classifiable as:

```text
VALID
AFFECTED
INVALID
UNKNOWN
WAIVED
SUPERSEDED
```

`UNKNOWN` means the system has insufficient information to determine validity.

`WAIVED` is an explicit decision that a dependency is intentionally not required for this case. It must never be inferred from absence.

## 6. Semantic versus operational dependency

### Semantic dependency

The downstream meaning would become incorrect if the upstream information changes.

Example:

```text
ARTICLE depends_on CLAIM
```

### Operational dependency

The downstream action requires a tool, channel, provider, storage location, or execution capability.

Example:

```text
PUBLICATION depends_on CHANNEL ADAPTER
```

Semantic invalidation can change factual validity.

Operational failure can block delivery without changing factual validity.

These are different failure modes and must not share one generic `dependency_failed` state.

## 7. Version binding

Dependencies point to exact revisions when the dependent result was created or verified.

```text
SPEC CS4 revision 2
  depends_on KNOWLEDGE K8 revision 5
```

If K8 moves to revision 6, CS4 revision 2 remains historically tied to revision 5.

The system then creates an impact decision rather than retroactively changing the dependency.

## 8. Dependency closure

A release candidate should be considered structurally complete only when every required upstream dependency is resolvable:

```text
release
  ↓
asset revision
  ↓
spec revision
  ↓
knowledge revision
  ↓
claims
  ↓
evidence
  ↓
sources
```

An unresolved required dependency blocks release unless an explicit authority records a waiver.

## 9. Impact propagation

The conceptual impact algorithm is:

```text
changed upstream object
  ↓
find direct dependents
  ↓
classify impact
  ↓
propagate only through semantic dependencies
  ↓
create review candidates
  ↓
require explicit decisions
```

This is intentionally not automatic republication.

## 10. Provenance package minimum

Any externally visible publication should eventually be able to reconstruct:

```text
publication_id
published_revision
accepted_revision
verification_result
content_spec_revision
editorial_decision
knowledge_revision
claim_ids
evidence_ids
source_ids
publication_time
publication_channel
```

The implementation may use another representation, but the information must remain reconstructable.
