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
mechanisms/
creative/
relations/
```

These are semantic projections of different information types, not independent authorities. They may remain virtual or be represented by individual records; this list does not require new top-level repository folders.

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

The exact fields depend on the memory type. A source, evidence item, claim, mechanism and knowledge synthesis must not be forced into one indistinguishable record shape.

## Mechanism knowledge

A mechanism record is appropriate when the project has studied a working mechanism from a real system and may adapt it later.

Preserve:

```text
problem_it_solves
source
mechanism
how_it_works
evidence_of_use
applicability_to_factory
limitations
adaptation_decision
confidence
```

External use is evidence for a design option, not proof of local correctness.

## Creative knowledge

Creative experience may be retained as reusable memory when it affects repeatable work. It must preserve context and uncertainty rather than being promoted to objective fact.

Useful fields include:

```text
creative_question
context
reference_or_input
experiment_or_treatment
observed_effect
successful_pattern_or_failure
reusable_candidate
uncertainty
examples
evidence_refs
confidence
```

This can cover visual direction, composition, editorial framing, storytelling structure, prompt patterns, rejected approaches and successful production patterns.

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
input to mechanism-selection decisions
```

Use does not transfer authority. A memory item can be referenced by a work item without being correct for every future context.

## Invariants

- Temporary task context does not belong here.
- Provenance is mandatory for material reusable claims.
- Unknowns remain explicit.
- Memory is not equivalent to current strategy or authority.
- Contradictory evidence must remain discoverable.
- Creative success is not automatically a reusable rule.
- A mechanism reference is not an implementation mandate.

## Completion criterion

A memory item is reusable when its identity, revision, provenance, evidentiary basis, scope and known limitations can be understood without reconstructing the original conversation.
