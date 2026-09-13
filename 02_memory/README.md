# 02 — Memory

Durable, reusable information.

## Purpose

`02_memory` contains information intentionally retained for reuse across work items. It is not a scratchpad and it is not a chronological event log.

## Suggested sub-zones

```text
sources/
evidence/
claims/
knowledge/
relations/
```

These are projections of different information types, not independent authorities.

## Minimum memory record

A reusable item should preserve, at minimum:

```text
memory_id
memory_type
subject_or_scope
content
status
source_refs
evidence_refs
provenance_refs
revision_id
created_at
updated_at
known_unknowns
supersedes_or_superseded_by
```

The exact fields depend on the memory type. A source, evidence item, claim and knowledge synthesis must not be forced into one indistinguishable record shape.

## Promotion rule

Information may enter memory only through an explicit promotion step supported by evidence or an explicit decision. In particular:

```text
observation → memory candidate → accepted reusable item
```

is valid only when the middle and final steps are recorded. The existence of an observation does not make it knowledge.

## Revision and invalidation

Memory is mutable in meaning but must remain reconstructable in history. When a reusable item changes:

- preserve its identity;
- create or identify a new revision;
- preserve provenance;
- state what evidence supports the revision;
- record contradictions, uncertainty or invalidation;
- link superseded material rather than silently deleting it.

## Allowed exits

Memory may be used as:

```text
knowledge basis for working context
input to reasoning
input to editorial decisions
input to production specifications
input to verification criteria
```

Use does not transfer authority. A memory item can be referenced by a work item without being correct for every future context.

## Invariants

- Temporary task context does not belong here.
- Provenance is mandatory for material reusable claims.
- Unknowns remain explicit.
- Memory is not equivalent to current strategy or authority.
- Contradictory evidence must remain discoverable.

## Completion criterion

A memory item is reusable when its identity, revision, provenance, evidentiary basis, scope and known limitations can be understood without reconstructing the original conversation.