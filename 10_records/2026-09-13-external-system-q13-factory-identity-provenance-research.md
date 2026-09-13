# External-System Research — Q13 Minimum Factory-Side Identity / Provenance Record

Date: 2026-09-13
Research branch: External World → External Systems → Reconciliation → Factory-side identity/provenance
Status: COMPLETE
Decision: EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE
Confidence: HIGH for provenance requirements; MEDIUM for exact implementation fields because the provider operation class determines which fields are available

## 1. Question

What is the minimum factory-side identity/provenance record that preserves reconciliation capability when an external provider exposes only target/resource/revision identity and no distinct operation ID?

The question follows Q12: GitHub does not expose one universal mutation-operation identity. Therefore the factory cannot make provider-generated `operation_id` a universal prerequisite for external interaction.

The objective is to identify the minimum information the factory itself must retain before crossing the external boundary so that later observation can still be related to the original intent and recovery claim.

## 2. Decomposition

### Q13.1 — Identity preservation

Which identities must survive the initial interaction?

### Q13.1.1 — Intent identity

How can the exact factory intent be identified independently of provider response semantics?

### Q13.1.1.1 — Target and revision identity

Which target, expected state and input revision must be retained to compare later observations against the intended mutation?

### Q13.1.1.1.1 — Authority identity

Which authority context must be retained so a later recovery action does not silently reuse an expired or broader authority?

### Q13.1.1.1.1.1 — Interaction identity

What factory-generated correlation identity is needed when the provider exposes no operation identifier?

### Q13.1.1.1.1.1.1 — Provenance sufficiency

What additional temporal, provider-result and uncertainty information is necessary to reconstruct the claim and decide what remains unresolved?

## 3. Source map

Primary sources:

1. W3C PROV-DM / PROV-O / PROV-XML for entities, activities, agents, responsibility, generation, usage, derivation and time.
2. AWS Builders Library, “Making retries safe with idempotent APIs,” for caller-provided request identifiers, duplicate detection, semantic equivalence, parameter mismatch and auditability.
3. GitHub mutation research from Q12 for concrete cases where resulting resource/state identity exists without a distinct operation ID.
4. Current Content Factory governing rules and protocol for explicit identity, revision, provenance, authority, unknowns and material-case reconstruction.

W3C PROV establishes provenance around identifiable entities, activities and agents, including responsibility and time. It explicitly treats activities as occurrences that use or generate entities and permits responsibility to be assigned to agents. citeturn0search1turn0search2turn0search5turn0search6

AWS's idempotency guidance establishes why a caller-provided unique request identifier is valuable when a service needs to distinguish repeated requests from distinct intent, and notes that the identifier can also support auditing and resource correlation. citeturn0search0

The repository itself requires object identity/revision, separate provenance/dependency/impact, contextual authority, explicit unknowns, and enough information to reconstruct sensing through learning. fileciteturn266file0

## 4. Candidate minimum record

The research supports the following as a minimum factory-side external-interaction record. This is a candidate record shape, not a new production schema.

```text
EXTERNAL INTERACTION PROVENANCE

factory_interaction_id       required
intent_id                    required
capability / operation_class required
provider                     required
provider_endpoint            required when material to semantics
external_target_identity     required
requested_input_revision     required when the target/input is mutable
expected_prior_state         required when recovery depends on precondition
factory_authority_context    required
authority_validity_window   required when authority is time/scoped
correlation_id               required for externally ambiguous interactions
provider_request_id          optional / provider-dependent
provider_operation_id        optional / provider-dependent
request_time                 required
response_time                optional until response exists
request_payload_fingerprint  required when exact request equivalence matters
result_resource_identity     optional until observed
result_revision_identity     optional until observed
observation_refs             zero-or-more
uncertainty_status           required
causal_attribution_status    required
recovery_claim               optional until an unresolved outcome exists
provenance_links             zero-or-more
```

The key design result is that the factory-generated identity is not a substitute for provider operation identity. It is the stable identity of the factory's own interaction/claim and remains useful even when the provider exposes only state identity.

## 5. Why each minimum element exists

### 5.1 `factory_interaction_id`

This identifies the factory-side interaction as an activity/record independently of provider semantics. It lets later observations and evidence be attached to the same intended interaction even if the provider supplies no operation ID.

### 5.2 `intent_id`

The interaction must remain tied to the exact intent that authorized it. Otherwise a later observation can prove that a state exists but cannot establish which intended change it was supposed to satisfy.

### 5.3 `capability / operation_class`

Recovery safety is operation-specific. Branch update, file mutation, PR creation and workflow dispatch have materially different identity and duplication semantics. Therefore the record must preserve the semantic operation class rather than merely a provider name.

### 5.4 `external_target_identity`

The record must identify what external object or state domain was targeted. A later GET can only reconcile a claim against an identified target.

### 5.5 `requested_input_revision` and `expected_prior_state`

Mutable targets require a reference point. Without the expected prior state, observing the resulting state may be insufficient to distinguish the intended transition from a concurrent or pre-existing state.

This aligns with GitHub's Contents update semantics, where the current blob SHA functions as a mutation precondition rather than an operation ID, and with Git reference conflict semantics established in Q12.

### 5.6 `factory_authority_context`

Authority must be preserved as context, not inferred later from the existence of an interaction record. A recovery action can require different or renewed authority from the original request.

### 5.7 `correlation_id`

A factory-generated correlation identifier is the fallback identity when the provider exposes no durable operation identifier. It cannot prove provider-side execution by itself, but it preserves the factory's causal claim boundary and gives provider logs or later evidence something to correlate against where supported.

### 5.8 Provider identities

`provider_request_id` and `provider_operation_id` must remain optional because Q12 demonstrated that providers do not expose them uniformly. They strengthen attribution when available; their absence is itself meaningful evidence about reconciliation limits.

### 5.9 Request fingerprint

When duplicate intent must be distinguished from changed intent, the factory needs a stable representation of the material request parameters. AWS explicitly describes retaining the parameters associated with an idempotency key and rejecting a reuse with different parameters rather than guessing that the calls are duplicates. citeturn0search0

The fingerprint is not itself proof of provider receipt. It is evidence about what the factory intended to send.

### 5.10 Result and observation identities

These are deliberately nullable until evidence exists. The record must be able to represent:

`interaction exists → provider result unknown → later observation finds state`

without rewriting the original interaction as though its result had been known synchronously.

### 5.11 Uncertainty and attribution status

The record must preserve unresolved epistemic boundaries rather than collapsing them into FAILED or COMPLETED. Q10–Q12 established that state evidence and causal attribution are distinct.

## 6. Provenance model reconciliation

W3C PROV supports this structure conceptually without requiring the factory to adopt PROV as its runtime ontology:

```text
factory interaction      ≈ Activity / provenance record
factory intent / input   ≈ Entity used by the activity
external result          ≈ Entity generated/observed
factory / external actor ≈ Agent
correlation / provider ID ≈ identifiers linking evidence
observation              ≈ later evidence about an entity/state
```

This is an analogy between semantic roles, not a claim that these objects are formally equivalent. PROV's central contribution here is the separation of entities, activities and agents plus explicit provenance relations and temporal information. citeturn0search2turn0search5

## 7. Minimum versus optional information

The minimum is not “everything available from the API.” It is the smallest set that preserves the ability to answer four later questions:

1. What exactly did the factory intend?
2. What exact external target/state was supposed to change?
3. Under what authority and preconditions was the action attempted?
4. What evidence can later establish, disprove or leave unresolved the claim that the intended effect occurred?

Provider-specific enrichments such as request IDs, operation IDs, response payloads, server timestamps, URLs and audit IDs are additional evidence when available.

## 8. Contradictions / rejected simplifications

### N1 — `provider_operation_id is mandatory`

Rejected.

Q12 demonstrated mutation classes without a distinct provider operation ID. Making it mandatory would exclude legitimate external interactions before their semantics are understood.

### N2 — `resource identity is sufficient`

Rejected.

A resource identity identifies the target/result but does not preserve the original intent, authority or expected prior state.

### N3 — `request payload is sufficient provenance`

Rejected.

The payload does not by itself identify the factory intent, authority, target revision, temporal context or later observation.

### N4 — `correlation_id proves execution`

Rejected.

A factory-generated ID identifies the factory-side claim. It does not prove that an external system received or executed the request.

### N5 — `provider response is the provenance record`

Rejected.

A response describes what the provider returned; it does not necessarily preserve why the request was authorized, which revision was intended, or what later observation established.

## 9. Inference boundary

### Established by external evidence

- Provenance benefits from identifiable entities, activities, agents and temporal information. citeturn0search1turn0search2
- Caller-generated request identifiers can make repeated intent explicit and auditable where the API supports them. citeturn0search0
- Provider identity is not universally available across mutation classes.

### Derived for Content Factory

- The factory needs its own stable interaction/claim identity independent of provider operation identity.
- Target identity, expected state/revision, authority context and intended input are necessary to preserve reconciliation capability.
- Provider-generated identifiers should enrich rather than define the factory's provenance record.

### Unknown

- Exact persistence granularity needed at production scale.
- Whether one interaction record should cover a logical multi-step external action or each provider interaction separately. Q3 currently favors preserving constituent interactions independently.
- Whether the candidate fields should become a machine-readable contract; no implementation evidence currently justifies that promotion.

## 10. Decision

`EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE`

The minimum factory-side boundary is a stable interaction/claim identity plus enough immutable intent, target, expected-state, authority, correlation and temporal information to allow later evidence to be evaluated against the original claim.

No new ontology class or runtime schema is introduced. The candidate record remains research until a concrete external effect case requires implementation.

## 11. Derived questions

- Q13.1: Which fields must be immutable after admission, and which may accumulate as evidence?
- Q13.2: What is the minimum record needed for a multi-interaction logical action without collapsing individual operation identities?
- Q14: Which observed states and preconditions are sufficient to authorize a specific recovery action?

## 12. Repository impact

- Research record added.
- No production implementation change.
- No ontology change.
- No new top-level folder.
- Existing external-system research model is extended, not replaced.

## 13. Verification

The record is intended to be reconciled with Q10–Q12 and the current repository rules. The conclusions preserve the existing boundaries between identity, state, observation, attribution, authority and recovery. The repository operating protocol requires exactly this distinction and prohibits promoting research directly into implementation. fileciteturn267file0
