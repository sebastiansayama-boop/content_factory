# Ontology 04 — Relation Analysis

A relation is defined by its semantic meaning, not by where two records happen to be stored.

## Relation families

### Origin and derivation

`derived_from`

The target is semantically derived from the source.

Example:

```text
Claim C17 derived_from Evidence E17
LearningCandidate L4 derived_from ObservationResult O9
```

`produced_from`

The target was produced by a bounded production activity using the source as an input.

Example:

```text
AssetRevision A12-r3 produced_from ContentSpecificationRevision CS4-r2
```

These are not interchangeable: derivation is semantic; production is an activity/output relationship.

### Epistemic relations

`supports`

The source provides support for the target proposition.

```text
Evidence → Claim
```

`contradicts`

The source conflicts with the target proposition or its evidential basis.

```text
Evidence → Claim
```

`invalidates`

A change or finding removes the validity of a previously relied-upon object or proposition.

This is stronger than contradiction and should be used only when invalidation is actually established or explicitly decided.

`verified_against`

A verification result assesses an exact target against an exact normative/evidential basis.

The relation must preserve revision identity.

### Dependency relations

`depends_on`

The continued validity or executability of the target requires the source, according to the declared dependency kind.

Dependency must be typed conceptually as:

```text
semantic
operational
existential
provenance
```

A generic edge must not erase these distinctions where the distinction changes impact behavior.

### Version and evolution relations

`has_revision`

Persistent entity to its version/revision.

`supersedes`

A newer entity/revision is preferred as the current successor of an older one, without asserting that the older one never existed or was false.

`impacts`

A change in the source may require review or reconsideration of the target.

`supersedes` and `impacts` are not equivalent: impact does not imply replacement.

### Structural relations

`part_of`

The source is a component of the target under a defined whole/part interpretation.

`assembled_into`

A production/release activity combines components into a larger operational bundle.

`part_of` is structural and persistent; `assembled_into` describes a construction relationship and may be revision-specific.

### Normative / authority relations

`plays_role`

An agent occupies a role in a bounded context.

`authorizes`

An agent/role/authority assignment permits a specific transition or effect.

`requires_authority`

A transition or effect cannot legitimately occur without the specified authority.

Authority is contextual and scoped; it must not be inferred from object ownership or folder location.

### External effect relations

`publishes`

An internal release/effect transition causes an external publication event.

`published_as`

An external publication event identifies the exact internal accepted/released state it represented.

`observes`

An observation event records information about an external or internal state/event.

## Relation non-equivalences

The following pairs must remain distinct:

```text
supports        ≠ depends_on
produced_from   ≠ derived_from
contradicts     ≠ invalidates
supersedes      ≠ invalidates
impacts         ≠ supersedes
part_of         ≠ depends_on
verification    ≠ acceptance
publishes       ≠ publication_record
observation    ≠ interpretation
```

## Relation validation questions

For every relation ask:

1. What is the precise meaning?
2. What are valid source and target types?
3. Can the relation be directional?
4. Is it time-dependent?
5. Is revision identity required?
6. Is it epistemic, structural, temporal, normative or operational?
7. Does it propagate impact?
8. Can the relation be retracted, invalidated, or superseded?
9. Is the relation itself evidence-bearing and therefore recordable?
