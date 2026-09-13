# External-System Research — Q10: Minimum Generic Reconciliation Contract

Date: 2026-09-13
Research branch: External World → External Systems → Uncertainty → Reconciliation
Status: COMPLETE FOR CURRENT SCOPE
Decision: EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE
Confidence: HIGH for the semantic boundary; MEDIUM for a future reusable contract

## 1. Question

What is the minimum generic reconciliation contract that lets Content Factory resolve an ambiguous external outcome without fabricating success or repeating an unsafe mutation?

The target is not a universal connector interface. The target is the minimum information required to answer a recovery question after the normal request/result path becomes incomplete.

Core distinction:

`RECONCILIATION ≠ RETRY`

Reconciliation asks what can now be established about a prior interaction. Retry is a later action whose safety depends on that evidence and on operation semantics.

## 2. Decomposition

### Q10.1 — Reconciliation claim

What exact uncertainty is reconciliation expected to resolve?

### Q10.1.1 — Identity evidence

Can the prior interaction, request, operation, target object or intended revision be identified without relying only on local timestamps or transport metadata?

### Q10.1.1.1 — State/effect evidence

Can reconciliation establish acceptance, completion, external state/effect, or only the existence of a request/operation?

### Q10.1.1.1.1 — Authority of evidence

Is the returned evidence authoritative for the claim, or is it an independent observation that still requires interpretation?

### Q10.1.1.1.1.1 — Observation semantics

What target, revision/version, temporal scope and consistency level does the observation actually cover?

### Q10.1.1.1.1.1.1 — Attribution

Can the observed state/effect be causally attributed to the prior interaction, rather than merely coexisting with it?

### Q10.1.1.1.1.1.1.1 — Recovery decision

Does the evidence justify retry, waiting, recording completion, further observation, reauthorization, compensation, or human decision?

This decomposition reaches beyond five levels because attribution and recovery remain materially different claims.

## 3. Source map

### A. Provenance semantics

1. W3C PROV-O.

PROV separates entities, activities and agents and provides qualified relations for usage, generation, derivation, association and delegation. This supports preserving the identity of the activity and the entities involved rather than treating one observed object as self-proving evidence of the preceding activity. citeturn1search0

### B. External state/version semantics

2. Kubernetes API Concepts.

Kubernetes exposes `resourceVersion` as server-side version information and supports follow-up observation from a known version. This demonstrates that object identity and state/version identity are different evidence dimensions. citeturn0search0

### C. Idempotent operation identity

3. Stripe API idempotency documentation.
4. AWS EC2 / Cloud Control API idempotency documentation.

These systems use client-generated identifiers to distinguish retries of the same intended operation from new operations. Stripe additionally stores the result associated with an idempotency key, while AWS documents client tokens as a mechanism for disambiguating retried requests. citeturn2search0turn2search13turn2search12

### D. GitHub concrete external system

5. GitHub Git Database / commit / reference APIs.

GitHub separates Git objects such as commits from references such as branch heads. Its documented write sequence creates objects/commit and then updates the branch reference. This provides a concrete example where existence of a commit is not equivalent to publication of that commit through a branch reference. citeturn0search2turn0search5turn0search7

## 4. Evidence

### E1 — Reconciliation must name the claim being resolved

A reconciliation query is insufficiently specified if it merely says `check status`.

The evidence above exposes several distinct claims:

```text
Did a request exist?
Was the request accepted?
Does an operation exist?
Did the operation reach a terminal result?
Does the target object/state now exist?
What revision/state is observed?
Can that state be attributed to the operation?
Does the state satisfy the intended outcome?
```

These claims are not interchangeable. PROV's separation of activities, entities and agents is direct evidence for retaining the activity/entity relationship rather than collapsing it into one result. citeturn1search0

### E2 — Operation identity and object identity solve different problems

Stripe and AWS demonstrate operation/request identity through idempotency keys or client tokens. Kubernetes demonstrates server-side object revision identity. GitHub demonstrates object identity through commit SHA and separately reference identity through a branch ref. citeturn2search0turn2search13turn0search0turn0search7

Therefore a generic reconciliation mechanism cannot assume that one `external_id` is sufficient.

Candidate dimensions are:

`operation/request identity`
`target/object identity`
`state/revision identity`
`causal/intent identity`

These are semantic dimensions, not yet ontology classes.

### E3 — Existence of an operation does not prove its effect

An externally represented operation can be pending or completed independently of the target state becoming visible to the observer. Conversely, a target state can be observed without proving which operation caused it.

GitHub gives a concrete structural example: a commit object can exist in the Git object database while a branch reference points elsewhere. The documented mutation path therefore has multiple externally meaningful points. citeturn0search2turn0search5turn0search7

This reinforces the Q3 result that a logical action may contain multiple interactions and that composition does not imply atomicity.

### E4 — Reconciliation evidence has an authority/consistency dimension

Kubernetes version semantics demonstrate that an observation may have a defined relationship to a server-side revision, including exact or minimum-version requirements. A plain current `GET` is therefore not automatically equivalent to an observation sufficient for every recovery claim. citeturn0search0

The generic question is not merely `did we read the object?`, but:

`what state did we observe, at what revision/time, under what consistency guarantee, from which authority/source?`

### E5 — Idempotency can provide an alternate reconciliation path

Stripe stores the result associated with an idempotency key for the relevant retention window; AWS client tokens allow a service to distinguish repeated attempts of the same operation. These mechanisms can collapse request ambiguity without requiring a separate state lookup, but only within the provider's documented semantics and scope. citeturn2search0turn2search13

This is important because reconciliation does not universally mean `GET target`.

It can mean:

`ASK OPERATION STATUS`
`REPLAY SAME IDEMPOTENT REQUEST`
`LOOK UP TARGET STATE`
`COMPARE TARGET REVISION`
`OBSERVE AN INDEPENDENT SOURCE`

The safe choice depends on the unresolved boundary and provider semantics.

## 5. Cross-source comparison

| Evidence dimension | GitHub | Kubernetes | Stripe | AWS client-token APIs | Generic implication |
|---|---|---|---|---|---|
| Request/operation identity | Commit/ref operations provide object/ref identities; transport request identity is separate | API request plus object/resource identity | Idempotency key + request ID | Client token | Preserve operation/request identity when provider exposes it |
| Object identity | Commit SHA, ref name | Object name/UID | Resource/object ID | Resource ID | Preserve target/object identity separately |
| Revision/state identity | Commit SHA and ref target | `resourceVersion` | Object state/versioning varies by API | Resource/operation state varies | Preserve revision/version when meaningful |
| Operation result | API response / resulting Git object or ref | API response/status/watch events | Stored idempotent response where applicable | Service-specific response/state | Do not infer one universal result form |
| External state/effect | Ref points to commit; commit exists | Object state at resource version | Resource state | Resource/operation state | Effect needs its own proof target |
| Causal attribution | Expected commit/ref relationship can be checked | Version/object history can constrain attribution | Idempotency key binds retry to request | Client token binds retries | Attribution is stronger than simple coexistence |
| Observation consistency | API state at observation time | Explicit version semantics | Endpoint-specific consistency | Service-specific | Record consistency/temporal scope when material |
| Recovery relevance | Reconcile object + ref before repeating mutation | Re-observe at required version | Reuse same key only under documented scope | Reuse same token only under documented scope | Recovery action follows evidence, not generic error status |

The comparison supports a common semantic envelope but rejects a common provider-specific mechanism.

## 6. Candidate minimum reconciliation contract

The research supports the following as a candidate semantic contract, not yet a production schema:

```text
RECONCILIATION_REQUEST
    unresolved_claim
    parent_interaction_or_action_identity
    operation_identity? 
    intent_or_idempotency_identity?
    target_identity?
    expected_state_or_revision?
    authority_context
    observation_scope
    required_consistency?
    risk/recovery_context

RECONCILIATION_RESULT
    claim
    result_status
    evidence_source
    observed_at
    operation_identity?
    target_identity?
    observed_state_or_effect?
    observed_revision/version?
    causal_relation?
    authority/authoritativeness
    consistency/temporal_scope?
    provenance
    uncertainty
```

The contract is deliberately claim-oriented. It does not require every provider to expose every field.

The minimum invariant is:

`A reconciliation result must state what claim the evidence supports and what remains unresolved.`

That is stronger and safer than returning a generic `status=success`.

## 7. Evidence sufficiency levels

A useful candidate ladder emerges from the comparison. These are evidence levels, not ontology classes:

```text
R0 — NO_CORRELATION
     No reliable link to the prior interaction.

R1 — INTERACTION_IDENTIFIED
     Request/operation existence can be established.

R2 — OPERATION_STATE_IDENTIFIED
     Acceptance/pending/completion state can be established.

R3 — EFFECT_OR_STATE_IDENTIFIED
     Resulting external object/state/effect can be identified.

R4 — EFFECT_ATTRIBUTED
     The observed effect/state can be causally related to the prior interaction.

R5 — RECOVERY_CLAIM_VERIFIED
     Evidence satisfies the specific claim needed for the next recovery decision.
```

The important result is that `R3` does not automatically imply `R4`, and `R4` does not automatically imply `R5`.

Example: observing the desired commit on a repository proves a state, but if another actor could have produced the same state, causal attribution may remain unresolved. Conversely, an operation record can prove execution without proving the desired external state.

## 8. Authoritative evidence vs independent observation

These should remain distinct.

### Authoritative evidence

Evidence emitted by the system that owns the relevant operation/state and whose semantics explicitly establish the claim.

Examples:

- provider operation record marked completed;
- provider response tied to an idempotency key;
- authoritative resource version/state returned by the state owner;
- GitHub branch reference pointing to the expected commit.

### Independent observation

Evidence obtained from a source that can observe the state but is not itself the authority that executed or owns the operation.

Independent observation is valuable when the primary response is lost or when causal verification requires a second source. But it does not automatically prove causality.

Therefore:

`observation ≠ attribution`
`provider response ≠ desired consequence`
`object existence ≠ operation causality`

## 9. Reconciliation itself is an interaction

Q7–Q9 established that recovery actions require their own authority and safety semantics. Q10 extends this to reconciliation.

A reconciliation read/request can fail, return stale data, require authorization, or have provider-specific consistency semantics. It must therefore be represented as a new interaction linked to the unresolved parent interaction, not as a magical rewrite of the original result.

Conceptually:

```text
ORIGINAL INTERACTION
        │
        ├── outcome = UNKNOWN
        │
        ▼
RECONCILIATION INTERACTION
        │
        ├── evidence
        ├── observation scope
        ├── authority
        └── result claim
        │
        ▼
UPDATED KNOWLEDGE
        │
        ▼
RECOVERY DECISION
```

The historical original interaction remains unchanged.

## 10. Contradictions and negative evidence

### N1 — `GET target = reconciliation`

Rejected as a universal rule.

Some providers expose operation-level idempotency or operation-status evidence that is more directly relevant than current target state. Conversely, target observation may be the only available route. Reconciliation is claim-driven, not method-driven. citeturn2search0turn2search13

### N2 — `object exists = operation succeeded`

Rejected.

An object may have pre-existed, been created by another actor, or represent only an intermediate state. GitHub's separate commit object and branch reference model demonstrates this distinction. citeturn0search2turn0search7

### N3 — `operation completed = desired consequence verified`

Rejected.

Completion establishes a technical operation result, not necessarily a downstream business/content consequence. This remains consistent with the Q4/Q6 evidence matrix.

### N4 — `one external ID = enough identity`

Rejected.

The sources expose different identities for request/operation, object and revision/state. A generic contract must permit multiple identities without requiring all of them for every provider. citeturn2search0turn0search0turn0search7

### N5 — `reconciliation is free/read-only`

Rejected as a universal assumption.

Reconciliation is a new external interaction and therefore inherits the provider's authority, rate, consistency, availability and side-effect semantics. The factory must not silently assume that every observation path is consequence-free.

## 11. Inference boundary

### Directly supported by external evidence

- Provenance needs separate activity/entity/agent relationships rather than one undifferentiated result. citeturn1search0
- Operation/request identity and resource/object identity can be separate. citeturn2search0turn2search13
- State revision/version can be materially relevant to observation and recovery. citeturn0search0
- GitHub exposes separate Git objects and references, making intermediate external states observable. citeturn0search2turn0search7
- Provider-specific idempotency mechanisms can disambiguate retries, but only within documented scope/retention semantics. citeturn2search0turn2search13

### Inferred for Content Factory

- Reconciliation should be claim-oriented rather than endpoint-oriented.
- A reconciliation result must explicitly identify the claim it supports and the residual uncertainty.
- Operation identity, target identity and state/revision identity should be independently representable when available.
- Authoritative evidence and independent observation should remain distinguishable.
- Reconciliation should be recorded as a new interaction linked to the unresolved original interaction.
- A reusable semantic envelope is justified conceptually, but provider-specific mechanisms should remain outside the generic contract.

### Not yet proven

- Exact field names or persistent schema for a reconciliation contract.
- Whether the contract should be a generic capability interface, a record type, or policy over existing interaction records.
- Whether R0–R5 is the right universal evidence scale.
- Whether all six external roles can use the same reconciliation result structure without role-specific extensions.
- Whether reconciliation can always be performed without additional external effect or elevated authority.

## 12. Role implications

| Role | Typical reconciliation target | Minimum decisive evidence candidate |
|---|---|---|
| Source / information | Source representation and freshness | Source identity + representation/revision + observation time/provenance |
| Execution | Operation lifecycle | Operation identity + authoritative terminal state/result |
| Publication | External visibility/state | Artifact revision + target + publication/effect identity + resulting external state |
| Transaction | Authoritative durable state | Transaction identity + authoritative commit/result + resulting state/revision |
| Control / governance | Effective authority/policy state | Subject + policy/permission identity + effective scope/time + authoritative state |
| Observation | Observation validity itself | Source + target + scope/time + observed revision/state + provenance |

This does not create six reconciliation primitives. It specializes the claim and evidence target according to the semantic role already established by Q2.

## 13. Decision

`EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE`

The research supports a generic semantic reconciliation contract, but not yet a production interface or ontology class.

The minimum generic invariant is:

```text
RECONCILIATION
= evidence collected to resolve a named unresolved claim
  about a prior interaction,
  while preserving identity, authority, observation scope,
  provenance and residual uncertainty.
```

The contract should be claim-oriented and extensible. It should not assume that reconciliation means GET, that one external ID is sufficient, or that observed state proves causality.

This is sufficient to advance the research model but insufficient to justify implementation of a new runtime primitive.

## 14. Repository impact

- Durable research record added.
- No production implementation changes.
- No ontology changes.
- No new top-level folder.
- Existing `UNKNOWN_EXTERNAL_OUTCOME` boundary is strengthened.
- Q7–Q9 recovery semantics are extended with an evidence-producing reconciliation interaction.
- Q3 composition principle is preserved: reconciliation is a constituent interaction with its own authority and recovery semantics.
- Q4/Q6 evidence model is preserved: every reconciliation result is evaluated against a specific claim.

## 15. Research consistency

The result is consistent with:

- `RULES.md`: unknowns remain explicit; evidence must support the exact claim; new primitives require demonstrated need.
- `docs/32_external_system_research_tree.md`: reconciliation follows uncertainty and precedes recovery.
- Q3 composition research: constituent interactions retain independent identity, authority and recovery semantics.
- Q4/Q6 evidence research: sufficient evidence is transition/claim-specific.
- Q7–Q9 recovery research: recovery depends on uncertainty location, operation semantics, idempotency, authority, observability and risk.
- `docs/10_effect_and_authority_boundaries.md`: ambiguous external outcomes remain unresolved until sufficient evidence is obtained.

## 16. Derived questions

1. Which external roles expose enough operation identity and revision information to reach R4/R5 rather than only R1–R3?
2. Can a reconciliation interaction be proven non-mutating for the first concrete systems we integrate?
3. How should the factory encode the evidence that permitted a subsequent retry or recovery action?
4. Can GitHub provide a controlled end-to-end case where request outcome is intentionally made ambiguous and then reconciled without duplicating the effect?
5. What is the smallest real external experiment that distinguishes `operation identified`, `effect identified`, and `effect attributed`?
6. How does reconciliation interact with an already accepted content revision and its immutable provenance?
7. Which parts of the candidate envelope belong to semantic records, and which belong to provider adapters/policies?

## 17. Post-write verification

Required verification:

1. Fetch the exact record from `main`.
2. Confirm the resulting commit and blob identity.
3. Confirm the record contains the decomposition, source map, cross-source matrix, candidate contract, evidence ladder, authority distinction, contradictions, inference boundary and decision.
4. Confirm no production/model artifact was changed by this research cycle.
5. Confirm consistency with Q7–Q9, Q4/Q6, Q3 and the external-effect boundary.

## 18. Current terminal status

`COMPLETED`

No implementation is justified by Q10 alone.

The next research step is not to build a generic reconciliation primitive. It is to test the candidate contract against a concrete external system with a controlled ambiguous-outcome scenario. GitHub is a suitable candidate because its object/reference model exposes multiple externally observable points, but no external mutation should be performed until an explicit experiment and authority boundary are established.
