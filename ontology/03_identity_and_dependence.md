# Ontology 03 — Identity and Dependence

Identity is the test for deciding whether two observed records refer to the same entity, a new entity, or a new revision/state of an existing entity.

## 1. Persistent identity versus revision

The current working model uses the following distinction:

```text
Knowledge
  ├── Revision 1
  ├── Revision 2
  └── Revision 3

Asset
  ├── Revision 1
  └── Revision 2
```

The ontology does not assume that `Revision` is itself the same kind of thing as `Knowledge` or `Asset`. For now it is treated as a versioning construct attached to an identity-bearing entity.

The exact identity criteria must therefore be expressed separately from lifecycle state.

## 2. Identity candidates

### Source

Identity candidate:

```text
source_id
```

Two source records may refer to the same external source while containing different observations or retrieved versions. Source identity must not be confused with a particular observation from that source.

### Evidence

Identity candidate:

```text
evidence_id
```

Evidence should identify a particular evidential item or observation, not merely the source from which it came.

### Claim

Identity candidate:

```text
claim_id
```

A materially changed proposition should normally produce a new claim identity or an explicit revision, rather than silently mutating an accepted proposition.

### Knowledge

Identity candidate:

```text
knowledge_id
```

`KnowledgeRevision` carries the version-specific content and bindings.

### Content specification

Identity candidate:

```text
specification_id
```

A material semantic change creates a new specification revision.

### Asset

Identity candidate:

```text
asset_id
```

A material change in the produced artifact creates a new asset revision.

### Release

Release identity depends on whether the domain treats a release as a persistent publication bundle or as an event. This remains a validation point rather than a final assumption.

## 3. Events do not acquire identity from artifacts

A recurring event should not be collapsed into the object affected by that event.

For example:

```text
Asset A12
  ← affected by ←
VerificationActivity V9
```

is not the same semantic statement as:

```text
VerificationResult V9
= Asset A12
```

Likewise:

```text
PublicationEvent P7
```

is not identical to:

```text
PublicationArtifact PA7
```

## 4. Dependence types

The model distinguishes at least four kinds of dependence.

### Existential dependence

An entity cannot exist in the modeled domain without another entity or context.

Example candidate:

```text
DecisionOutcome
  depends existentially on
DecisionContext / DecisionEvent
```

### Semantic dependence

The entity's correctness or meaning depends on another entity remaining valid.

Example:

```text
ContentSpecificationRevision
  depends semantically on
KnowledgeRevision
```

### Provenance dependence

An object can be traced to an origin without requiring the origin to remain valid for the object to exist.

Example:

```text
AssetRevision
  produced_from
ContentSpecificationRevision
```

The asset can remain a historical artifact even if the specification later becomes superseded.

### Operational dependence

A transition or effect requires another capability or external component.

Example:

```text
PublicationEvent
  operationally depends on
Channel
```

Operational failure must not be interpreted as semantic invalidity.

## 5. Identity rules

1. Material semantic change is not a silent identity-preserving mutation of an accepted revision.
2. Historical objects retain their identity and history even when superseded.
3. A record describing an event is not identical to the event.
4. A source is not identical to evidence derived from it.
5. A claim is not identical to the knowledge revision containing it.
6. A production artifact is not identical to the knowledge it represents.
7. An observation is not identical to the interpretation made from it.
8. A decision record is not identical to the authority or decision event it records.

## 6. Open identity questions

The following require real-case testing before formal ontology commitments:

- whether `Knowledge` is a persistent conceptual identity or a convenience grouping over revisions;
- whether `Release` is an entity, a bundle description, or an event;
- whether `Publication` needs three separate concepts (event, artifact, record);
- whether `Evidence` should always refer to an observation event or may also be a stable informational item;
- whether `Claim` requires explicit revision identity or can be replaced by new claim identities;
- whether `Model` is best treated as a document/artifact, a conceptual object, or both through separate layers.
