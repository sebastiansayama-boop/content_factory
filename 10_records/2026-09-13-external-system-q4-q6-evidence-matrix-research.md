# External-System Research — Q4/Q6: Minimum Sufficient Evidence Matrix

Date: 2026-09-13
Research branch: External World → External Systems → System Classes → External Action → Effect / Observation / Verification
Status: COMPLETE FOR CURRENT SCOPE
Decision: EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE
Confidence: HIGH for the transition distinctions; MEDIUM for the exact generic evidence contract

## 1. Question

What evidence is sufficient to distinguish the following claims for each major external-system role?

`intent → authorized operation → request sent → accepted → execution completed → external state/effect changed → observed → verified → desired consequence`

The purpose is not to define one universal success record. The purpose is to determine which evidence is sufficient for each semantic claim and how the requirement changes by external-system role.

## 2. Decomposition

### Q4/Q6.1 — Evidence boundary

What exactly is being claimed at each transition?

### Q4/Q6.1.1 — Claim identity

Can the evidence be attached to a specific action, interaction, target, input/revision, and time interval?

### Q4/Q6.1.1.1 — Evidence type

What distinguishes request evidence, acceptance evidence, execution evidence, effect evidence, observation evidence, and consequence evidence?

### Q4/Q6.1.1.1.1 — Role specificity

Does the minimum sufficient evidence change for source, execution, publication, transaction, control, and observation systems?

### Q4/Q6.1.1.1.1.1 — Ambiguity and independence

When is a response from the acting system sufficient, and when is an independent observation or reconciliation required?

### Q4/Q6.1.1.1.1.1.1 — Sufficiency test

For each transition, can a reasonable alternative explanation remain that would make the claimed state/effect false? If yes, the evidence is insufficient for that claim.

This seventh level is required because the distinction between technical completion and external consequence is the central unresolved evidence boundary.

## 3. Source map

### A. Provenance

1. W3C PROV-O / PROV Data Model.
2. W3C Trace Context.

These establish that provenance needs identifiable entities, activities, agents/responsibility, and causal relationships; correlation identity alone is not the whole provenance record. citeturn1search3turn1search2

### B. Protocol-level request semantics

3. RFC 9110 HTTP Semantics.

HTTP status describes the result of the request at the protocol boundary, but it does not universally establish a later business consequence or independent state observation. citeturn0search2

### C. Operational evidence conventions

4. OpenTelemetry HTTP semantic conventions.
5. OpenTelemetry general trace semantic conventions.

These distinguish logical operations from physical request attempts and record operation-specific attributes such as target, request method, response status, error information, and resend count. They therefore support preserving operation identity and attempt evidence without treating telemetry as proof of business effect. citeturn0search0turn0search4turn0search5

### D. Machine-readable failure evidence

6. RFC 9457 Problem Details.

This demonstrates that a protocol response may contain a machine-readable problem type, status, occurrence identity, and additional details. Error evidence can therefore establish why a request was rejected without implying that no external mutation occurred in every possible asynchronous system. citeturn1search0

## 4. Evidence taxonomy

The research supports six distinct evidence claims:

| Evidence claim | What it proves | What it does NOT prove |
|---|---|---|
| Request evidence | Factory attempted/sent a specific request | Acceptance, completion, effect |
| Acceptance evidence | External system accepted the request for processing | Completion, state change, consequence |
| Execution evidence | External system reports processing/completion of the operation | Desired state or business consequence unless semantics guarantee it |
| Effect evidence | External state/object was changed or made externally visible | Desired downstream consequence |
| Observation evidence | A state/effect was observed at a specified time by a source | Causality, unless linked to the action and no plausible competing explanation remains |
| Consequence evidence | Desired domain outcome occurred | That the factory's technical action was the sole cause |

The critical rule is:

`evidence is sufficient only for the claim whose semantics it actually establishes`.

## 5. Comparative matrix — six external-system roles

Legend:
- **M** = minimum evidence normally required for the transition.
- **C** = conditional; required when the operation has that semantic property.
- **I** = independent evidence normally required to make the stronger claim.
- **N/A** = transition is not intrinsic to the role.

| Role | Intent → target | Target → authority | Authority → request | Request → acceptance | Acceptance → execution | Execution → external effect | Effect → observation | Observation → verification | Verification → consequence |
|---|---|---|---|---|---|---|---|---|---|
| Source / information | Query/retrieval purpose + source identity/scope | Access identity + permitted scope + validity | Exact query/retrieval request + timestamp | Source response or retrieval acknowledgement | Retrieved representation + source response semantics | C: source state/revision if claiming acquisition of a particular version | Source identity + observed representation + retrieval time | Compare representation against expected source/provenance rules; C: corroboration/freshness | N/A unless the source itself is the target of a downstream consequence |
| Execution | Operation intent + execution target | Acting identity + scoped authority + validity | Exact input/revision + operation/request identity | Provider acceptance/response or explicit asynchronous job/operation identity | Completion/result tied to operation identity, or explicit `UNKNOWN` | C/I when execution mutates external state: resulting object/state identity or authoritative effect evidence | I when effect is material or independently observable | Compare observed state/effect with requested operation, target, revision and expected semantics | C: domain/business evidence beyond technical completion |
| Publication | Artifact identity/revision + publication target | Publisher identity + publication scope + authority | Exact accepted artifact revision + target + publication operation identity | Target acceptance/publication acknowledgement | Publication result + external object/URL/identifier where provided | External visibility/object existence at target; exact revision if exposed | I: retrieve/view/query the published object/state | Verify target, revision, visibility, content integrity and temporal state | C: audience/reach/consumption/consequence evidence |
| Transaction / durable business state | Transaction intent + exact target/state transition | Strong authority + subject + scope + preconditions + validity | Exact transaction request + idempotency/transaction identity | Authoritative transaction acceptance/ID | Authoritative commit/result + transaction identity | Authoritative resulting state/ledger/object identity | I: authoritative read/reconciliation of resulting state | Verify preconditions, commit state, amount/subject/object identity and no conflicting state | C/I: business outcome evidence if distinct from state mutation |
| Control / governance | Intended policy/permission/configuration change | Authority over subject/policy + scope + duration | Exact policy change + target + decision identity | Control system acknowledgement/decision | Effective policy/configuration state | Resulting control state, not merely API response | I: observe effective policy where another system may cache/propagate it | Verify effective scope, subject, duration, conditions and policy semantics | C: downstream operational consequence if the control change is intended to cause one |
| Observation | Observation purpose + target state/effect + scope/time | Authority to inspect/observe, where applicable | Exact observation/query request + source identity | Observation source accepts query/request | Returned observation record/result | N/A: observation does not itself prove mutation | Observation record with source, time, target, state/object/revision | Cross-check temporal scope, source independence, identity/revision and expected relation to action | C/I: consequence evidence only if the observation directly measures the desired consequence |

## 6. What the matrix establishes

### 6.1 A common evidence core exists, but a common mandatory record does not

Across the six roles, the following dimensions recur often enough to form a candidate common evidence vocabulary:

1. claim identity;
2. interaction/action identity;
3. source/actor identity;
4. target identity;
5. input or observed revision where relevant;
6. authority context where relevant;
7. timestamp/temporal scope;
8. response/result/evidence payload;
9. external object/state identity where relevant;
10. uncertainty status;
11. provenance link to the parent action.

However, the matrix rejects making every field mandatory for every role. A source retrieval and a financial transaction do not require the same proof boundary.

### 6.2 Request evidence is the weakest transition

Evidence that the factory sent a request proves only the factory-side attempt. OpenTelemetry's HTTP conventions explicitly model individual client attempts and response status separately, while HTTP semantics define status at the request/response boundary. citeturn0search0turn0search2

Therefore:

`request evidence ≠ acceptance evidence ≠ execution evidence`.

### 6.3 Acceptance evidence is not effect evidence

A protocol can report that a request was received, understood, or accepted while the operation continues asynchronously or later fails. HTTP 2xx semantics describe successful receipt/understanding/acceptance of the request, not a universal guarantee of a later business consequence. citeturn0search2

Therefore asynchronous systems require an operation identity or equivalent durable reference when completion is not synchronous.

### 6.4 Execution evidence is not automatically state/effect evidence

Execution evidence establishes what the external execution system reports about processing. It becomes sufficient for an effect claim only when the operation's semantics explicitly guarantee the claimed state transition and the result identifies the affected object/state strongly enough to rule out ambiguity.

For material external mutations, the stronger default is to require effect evidence or later observation.

### 6.5 Observation is a distinct evidentiary role

An observation can establish current external state, but it does not automatically establish that a preceding factory action caused that state. Provenance requires causal relationships between activities/entities rather than correlation alone. W3C PROV explicitly distinguishes usage, generation, derivation, association, attribution and delegation. citeturn1search3

Thus a strong post-action claim needs both:

`action/effect evidence` + `observation evidence`

when the operation is consequential, asynchronous, independently mutable, or otherwise ambiguous.

### 6.6 Independent observation is conditional, not universal

It would be excessive to require an independent observer for every operation. For a pure read, the retrieved representation can itself be the observation. For a synchronous operation whose protocol contract explicitly returns the authoritative resulting state, that result may satisfy both execution and effect evidence.

Independence becomes materially important when:

- the acting system can acknowledge without completing;
- the operation is asynchronous;
- the response can be lost;
- the state can be changed by other actors;
- the operation is consequential or irreversible;
- the provider's acknowledgement does not expose resulting state;
- recovery depends on knowing whether the effect already happened.

## 7. Sufficiency rule for each transition

### T1 — Intent → target

Sufficient evidence:
- explicit intended operation;
- target identity/scope;
- exact object/resource identity where relevant.

Failure boundary:
- an unqualified provider name is not sufficient target evidence.

### T2 — Target → authority

Sufficient evidence:
- acting identity;
- authority/capability or policy decision;
- scope;
- validity conditions/time;
- target/action compatibility.

Failure boundary:
- possession of a credential or connector is not itself evidence that the specific action is authorized.

### T3 — Authority → request

Sufficient evidence:
- exact input or artifact revision;
- target;
- operation/request identity;
- authority context used;
- timestamp/attempt information;
- transport/request evidence.

Failure boundary:
- authorization record alone does not prove a request was sent.

### T4 — Request → acceptance

Sufficient evidence:
- externally generated response/acknowledgement, or durable external operation/job identifier;
- correlation to the request;
- acceptance/rejection semantics.

Failure boundary:
- local HTTP/client success without a received external response is not acceptance evidence.

### T5 — Acceptance → execution

Sufficient evidence:
- authoritative completion/result tied to the operation identity;
- or a documented synchronous contract that makes the acceptance response itself the authoritative completion result.

Failure boundary:
- `accepted`, `queued`, `202`, or equivalent asynchronous acknowledgement is not execution completion.

### T6 — Execution → external effect

Sufficient evidence, strongest form:
- resulting external object/state identity;
- exact affected revision/state where available;
- operation identity linking the result to the action;
- authoritative effect result or independent state read.

Failure boundary:
- generic `success` without affected-state identity does not prove a specific external mutation.

### T7 — Effect → observation

Sufficient evidence:
- observation source identity;
- observed target/object/state;
- observation timestamp and temporal scope;
- representation/revision/value sufficient to establish the state claim.

For consequential operations, independence from the actor is preferred or required when the actor's own acknowledgement cannot exclude alternative states.

### T8 — Observation → verification

Sufficient evidence:
- explicit expected property/claim;
- observed value/state;
- identity/revision/time alignment;
- rule determining whether the observation satisfies the claim;
- contradiction/uncertainty handling.

Verification is therefore a comparison of a claim against evidence, not a synonym for “received a response”.

### T9 — Verification → consequence

Sufficient evidence:
- evidence that directly measures the desired domain consequence;
- causal or attribution link where causal attribution matters;
- time boundary sufficient to distinguish the consequence from unrelated state.

Failure boundary:
- technical mutation success does not prove audience response, revenue, conversion, delivery, or any other downstream consequence unless the system semantics explicitly define that mutation as the consequence.

## 8. Role-specific minimum proof profiles

### Source systems

Minimum sufficient proof for acquisition is:

`source identity + query/retrieval scope + retrieved representation + retrieval time + provenance/revision where available`.

Independent observation is not automatically required because the retrieved representation is itself the observation. Corroboration becomes necessary when freshness, correctness, adversarial provenance, or high-consequence claims require it.

### Execution systems

Minimum sufficient proof for pure computation is:

`operation identity + exact input/revision + authority context + completion/result`.

For external mutation, this expands to:

`... + resulting external object/state identity + effect evidence`

and often:

`... + post-effect observation`.

### Publication systems

Minimum sufficient proof is stricter than ordinary execution because the semantic goal is external visibility:

`accepted artifact revision + publication target + publication operation identity + acceptance/completion evidence + resulting external object/visibility evidence`.

### Transaction systems

Minimum sufficient proof is strongest:

`authorized subject + exact transaction + preconditions + transaction identity + authoritative commit/result + resulting authoritative state + reconciliation capability`.

If a response is lost after a potentially committed transaction, `UNKNOWN` is safer than failure until reconciliation establishes the state.

### Control systems

Minimum sufficient proof concerns effective authority/policy rather than ordinary execution:

`policy subject + requested change + authority + scope/duration/conditions + policy decision + effective-state observation where propagation/caching can intervene`.

### Observation systems

Minimum sufficient proof is:

`observation source + target + query/observation scope + observation time + returned state/object/revision`.

To serve as independent verification, the observation source must have enough independence from the action executor to rule out the specific failure mode under investigation.

## 9. Contradictions and negative evidence

### N1 — “HTTP 2xx proves the desired external result”

Rejected.

RFC 9110 defines 2xx as successful receipt, understanding, and acceptance of the request; it does not establish a universal later business consequence. citeturn0search2

### N2 — “A successful client span proves the external mutation”

Rejected.

OpenTelemetry HTTP conventions capture request/response operation evidence and explicitly distinguish attempts, response status, and resend behavior. They are observability semantics, not a universal business-effect proof. citeturn0search0

### N3 — “One response is enough for every role”

Rejected.

The six roles have different proof targets: acquisition, execution, visibility, durable state, effective policy, and observation.

### N4 — “Observation proves causality”

Rejected.

An observation proves a state claim at a time; causal attribution requires provenance linking the state to the relevant action. W3C PROV explicitly models causal/provenance relations rather than relying on correlation alone. citeturn1search3

### N5 — “Independent observation is mandatory for every operation”

Rejected.

For synchronous operations with authoritative resulting-state semantics, the response can itself be sufficient. Independence is required according to ambiguity, consequence, reversibility, and failure/recovery semantics.

### N6 — “Error response proves no external effect occurred”

Rejected as a generic rule.

Machine-readable error details can establish why a request was rejected, but asynchronous or distributed systems can fail after partial processing. RFC 9457 provides structured error information; it does not define a universal rollback guarantee. citeturn1search0

## 10. Candidate common evidence contract

The research supports a common semantic envelope, but not one universal mandatory schema:

```text
EvidenceClaim
├── claim_id
├── claim_type
├── parent_action_id
├── interaction_id
├── source_or_actor
├── target
├── authority_context [conditional]
├── input_or_revision [conditional]
├── operation_or_request_id [conditional]
├── observed_object_or_state [conditional]
├── timestamp / temporal_scope
├── evidence_payload / reference
├── provenance_links
├── confidence / verification status
└── uncertainty / recovery state [conditional]
```

Role-specific evidence requirements should constrain this envelope rather than replacing it with six unrelated contracts.

This remains a candidate conceptual contract, not a repository implementation primitive.

## 11. Inference boundary

### Directly supported by external evidence

- Provenance needs semantic relationships beyond correlation IDs. citeturn1search3turn1search2
- Request/response protocol status is bounded to the protocol operation's semantics. citeturn0search2
- Observability systems distinguish operation identity, request attempts, responses and errors. citeturn0search0turn0search5
- Machine-readable error responses can identify the problem type and occurrence without being equivalent to a state rollback guarantee. citeturn1search0

### Inferred for Content Factory

- Evidence should attach to explicit claims rather than merely to an operation record.
- A common semantic evidence envelope is preferable to six independent evidence primitives.
- Evidence sufficiency should be defined by transition and external-system role.
- Material mutations should normally require effect evidence and, where ambiguity warrants it, post-effect observation.
- Consequence evidence must remain separate from technical effect evidence.

### Not yet proven

- Exact persistence schema for `EvidenceClaim`.
- Whether `claim_id` should be a new identity or derived from existing event/evidence identities.
- Exact independence criteria for every future integration class.
- Universal rules for when a synchronous response is authoritative enough to serve as effect evidence.
- Whether all business consequences can be represented with one generic consequence evidence structure.

## 12. Conclusion

Result: PROVEN at the transition-semantics level; CANDIDATE at the generic contract level.

The six external-system roles do not require six different evidence architectures. They require one common evidentiary language with role- and transition-specific sufficiency rules.

The strongest general rule is:

`A piece of evidence is sufficient only for the strongest claim that its semantics actually establish.`

The resulting proof ladder is:

`INTENT/TARGET → AUTHORITY → REQUEST → ACCEPTANCE → EXECUTION → EFFECT → OBSERVATION → VERIFICATION → CONSEQUENCE`

with the following default boundaries:

- request evidence proves attempt;
- acceptance evidence proves external acceptance;
- execution evidence proves processing/completion;
- effect evidence proves external state/effect;
- observation evidence proves observed state at a time;
- verification proves a defined claim against evidence;
- consequence evidence proves the desired domain outcome.

No transition may silently inherit proof from the preceding transition.

## 13. Decision

`EXTENDS_CURRENT_MODEL`

No production code, ontology class, or generic evidence primitive is justified yet.

The research tree already contains the necessary conceptual separation. This result adds a stronger rule for evidence sufficiency and constrains future implementation:

1. use one common semantic evidence envelope;
2. define sufficiency per transition;
3. specialize requirements by external-system role;
4. require independent observation when the operation's ambiguity or consequence makes actor-reported completion insufficient;
5. never promote technical execution into business consequence without direct evidence.

## 14. Repository impact

- Add this durable research record only.
- No production code changes.
- No ontology changes.
- No new generic persistence primitive.
- Future Q7-Q9 work must use these evidence boundaries when modeling external state, uncertainty, and recovery.

## 15. Post-write verification target

After writing this record, verify on `main`:

1. exact file exists;
2. the comparative six-role matrix is present;
3. transition sufficiency rules are present;
4. contradictions and negative evidence are present;
5. inference boundary is explicit;
6. decision is explicit;
7. no production files changed as part of this research cycle.

## 16. Derived questions

1. Q7: How should observed external state, desired state, verified state, divergence, and staleness be represented without confusing observation with truth?
2. Q8: Which evidence combinations justify `UNKNOWN`, `FAILED`, `EFFECT_CONFIRMED`, and `CONSEQUENCE_UNKNOWN`?
3. Q9: How can recovery/reconciliation policy be selected mechanically from evidence availability, idempotency, reversibility, object identity, and observation capability?
4. Q10: Which evidence fields are security-sensitive and require isolation or redaction?
5. Q11: How should the evidence graph connect factory provenance to external identities and later learning?
6. Q12: Which parts of this candidate evidence envelope belong in the generic integration boundary versus role-specific adapters?
7. Q14: Can GitHub demonstrate the generic matrix without becoming the definition of the generic model?
