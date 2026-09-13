# Ontology 05 — Candidate Model

This is a **candidate conceptual ontology**, not yet a formal OWL ontology. It is deliberately conservative: only distinctions required by competency questions and current system invariants are promoted.

## 1. Upper semantic categories

```text
DOMAIN ENTITY
├── INFORMATION ENTITY
│   ├── Source
│   ├── Evidence
│   ├── Claim
│   ├── Knowledge
│   ├── ContentSpecification
│   └── Model
│
├── ARTIFACT
│   └── Asset
│
├── AGENT
│   ├── Human
│   ├── System
│   └── ModelAgent
│
├── CONTEXT / ROLE
│   ├── Role
│   └── DecisionContext
│
├── EVENT / ACTIVITY
│   ├── ObservationEvent
│   ├── ResearchActivity
│   ├── DecisionEvent
│   ├── VerificationActivity
│   ├── AcceptanceEvent
│   ├── PublicationEvent
│   └── LearningActivity
│
├── RESULT / INTERPRETATION
│   ├── ObservationResult
│   ├── ResearchResult
│   ├── DecisionOutcome
│   ├── VerificationResult
│   └── LearningCandidate
│
└── RECORD / DESCRIPTION
    ├── DecisionRecord
    ├── AcceptanceRecord
    ├── PublicationRecord
    └── CaseRecord
```

This upper structure is a semantic proposal only. It does not claim that these categories are universal ontology primitives.

## 2. Persistent entities and revisions

```text
Knowledge
  └── has_revision → KnowledgeRevision

ContentSpecification
  └── has_revision → ContentSpecificationRevision

Asset
  └── has_revision → AssetRevision
```

A revision is a versioned representation bound to a persistent identity. Lifecycle state remains outside ontology identity.

## 3. Core information graph

```text
Source
  ↓ gives rise to
Evidence
  ├── supports ─────→ Claim
  └── contradicts ──→ Claim

Claim
  └── included_in ──→ KnowledgeRevision

KnowledgeRevision
  ├── informs ─────→ DecisionEvent / DecisionOutcome
  └── depends_on ──→ Evidence / Claim

DecisionOutcome
  └── constrains ──→ ContentSpecificationRevision

ContentSpecificationRevision
  └── constrains ──→ AssetRevision

AssetRevision
  └── verified_by ──→ VerificationActivity

VerificationActivity
  └── produces ────→ VerificationResult

VerificationResult
  └── supports ────→ AcceptanceEvent

AcceptanceEvent
  └── authorizes ──→ Release / PublicationEvent
```

## 4. Feedback loop

```text
PublicationEvent
   ↓
ObservationEvent
   ↓ produces
ObservationResult
   ↓ interpreted_as
LearningCandidate
   ↓ may_inform
Claim / KnowledgeRevision / DecisionContext
```

The final arrow is deliberately `may_inform`, not `becomes`. Promotion requires an explicit epistemic/decision transition outside ontology semantics.

## 5. Authority structure

```text
Agent
  └── plays_role → Role
                     └── within → DecisionContext
                                   └── authorizes → DecisionEvent / Effect
```

Authority is therefore contextual rather than an intrinsic capability of every agent.

## 6. External effect boundary

```text
Release
  └── authorizes / causes → PublicationEvent
                              ├── targets → Channel
                              └── produces → PublicationArtifact
```

A publication record records the event; it is not the same object as the event itself.

## 7. What is explicitly not in the ontology as a primary class

```text
folder
workflow stage
transition
repository zone
lifecycle state
current status
```

These belong to system representation and operational modeling.

## 8. Candidate relation inventory

```text
has_revision
part_of
assembled_into

supports
contradicts
invalidates
verified_against

derived_from
produced_from

depends_on
impacts
supersedes

plays_role
within_context
authorizes
requires_authority

constrains
informs
publishes
published_as
observes
```

## 9. Deferred concepts

The following are intentionally unresolved:

- whether `Release` is primarily a bundle entity, a release event, or both;
- whether `PublicationArtifact` is required in all channels;
- whether `Evidence` should specialize into observations, documents, measurements and other forms;
- whether `Knowledge` should be modeled as an information object, a body of propositions, or a managed conceptual identity over revisions;
- whether `State` needs any direct ontology representation beyond the operational state model;
- which upper ontology, if any, should be reused formally.

No implementation should silently resolve these questions.
