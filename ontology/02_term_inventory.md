# Ontology 02 — Term Inventory

This inventory records current vocabulary as candidates. A term is not promoted to an ontology class merely because it appears in the repository.

## Candidate domain terms

| Term | Candidate semantic category | Current assessment |
|---|---|---|
| World | domain boundary | contextual, not a normal class |
| Source | information-bearing entity | candidate class |
| Evidence | information-bearing entity | candidate class; may require event/result distinction |
| Claim | propositional/information entity | candidate class |
| Knowledge | structured information/conceptual object | candidate class |
| KnowledgeRevision | revision/version of information | candidate class or version object |
| Signal | incoming observed/input item | candidate class |
| Question | information object / inquiry | candidate class |
| Candidate | work/discovery proposal | candidate class |
| ResearchRequirement | specification of required investigation | candidate class |
| ResearchActivity | activity/process | candidate class |
| ResearchResult | result of research | candidate class |
| EditorialDecision | decision result/act family | must be decomposed |
| DecisionEvent | event | candidate class |
| DecisionOutcome | outcome/value | candidate class |
| DecisionRecord | record/document | candidate class |
| ContentSpecification | prescriptive information artifact | candidate class |
| Asset | produced artifact | candidate class |
| AssetRevision | version of artifact | candidate class or version object |
| VerificationActivity | assessment activity | candidate class |
| VerificationResult | assessment result | candidate class |
| AcceptanceEvent | authority-bearing event | candidate class |
| AcceptanceRecord | durable record of acceptance | candidate class |
| Release | bundle/organizational publication unit | candidate class; semantics require case validation |
| PublicationEvent | external event/effect | candidate class |
| PublicationArtifact | externally visible information artifact | candidate class |
| PublicationRecord | record of external publication | candidate class |
| ObservationEvent | observation event | candidate class |
| ObservationResult | observed result | candidate class |
| LearningActivity | process | candidate class |
| LearningCandidate | proposed interpretation/change | candidate class |
| Agent | actor | candidate class |
| Human | agent subtype | candidate subclass after upper ontology decision |
| Model | system representation | candidate information artifact |
| Role | contextual social/organizational role | candidate class |
| AuthorityAssignment | normative/contextual relation or reified assignment | candidate class |
| DecisionContext | context bounding authority | candidate class |
| Channel | external/integration entity | candidate class |
| Audience | external stakeholder/group | candidate class |
| ExternalEffect | effect in outside world | candidate class |
| Revision | versioning construct | cross-cutting modeling construct; should not automatically become domain superclass |
| Event | temporal occurrence | upper category |
| State | condition/situation | upper category; not automatically a lifecycle class |
| Record | durable representation of something | cross-cutting information artifact |

## Terms currently treated as mechanisms rather than domain entities

These should not become ontology classes solely because the repository uses them:

```text
folder
workflow
process
transition
space
state-machine
repository zone
```

They describe how the system represents or changes domain entities.

## Terms requiring decomposition

### Decision

Do not use one overloaded `Decision` class until the model distinguishes:

```text
DecisionEvent
DecisionOutcome
DecisionRecord
DecisionAuthority / AuthorityAssignment
DecisionContext
```

### Observation

Distinguish at least:

```text
ObservationEvent
ObservationResult
ObservationInterpretation / LearningCandidate
ObservationRecord
```

### Verification

Distinguish:

```text
VerificationActivity
VerificationResult
VerificationCriterion
VerificationRecord
```

### Publication

Validate whether a case needs:

```text
PublicationEvent
PublicationArtifact
PublicationRecord
```

rather than one overloaded `Publication` entity.

### Learning

Distinguish the activity/process from the produced interpretation:

```text
LearningActivity
LearningCandidate
```

The learning candidate must not silently become a knowledge revision.

## Classification test

For every candidate term ask:

1. Is it a persistent entity, an event, an activity, a role, a state/situation, a quality, a description, an artifact, or a record?
2. What is its identity criterion?
3. Does it exist independently or depend on another entity/context?
4. Can it change while remaining the same entity?
5. Can it occur multiple times for the same entity?
6. Can it be represented by a record without being identical to that record?
7. Does it need a lifecycle, or does it participate in someone else's lifecycle?
8. Which competency questions require the distinction?
