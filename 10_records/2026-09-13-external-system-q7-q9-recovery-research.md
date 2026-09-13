# External-System Research — Q7–Q9: State, Uncertainty, Recovery

Date: 2026-09-13
Research branch: External World → External Systems → State/Time → Uncertainty → Reliability/Recovery
Status: COMPLETE FOR CURRENT SCOPE
Decision: EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE
Confidence: HIGH for the safety distinctions; MEDIUM for a future generic recovery contract

## 1. Question

How should Content Factory distinguish external state over time, represent ambiguous outcomes, and select safe recovery behavior without fabricating an external result?

The research target is the chain:

`external state/time → uncertainty classification → recovery decision → retry/reconcile/observe/stop`

The objective is not to create a universal retry engine. It is to determine which facts must be known before a recovery action is safe.

## 2. Decomposition

### Q7.1 — State identity

What state existed before the action, what state was requested, and what state was later observed?

### Q7.1.1 — Temporal identity

Can the evidence establish the relevant state revision and observation time?

### Q7.1.1.1 — Divergence

How can the factory distinguish intended state, observed state, stale state and conflicting state?

### Q7.1.1.1.1 — Ambiguous transitions

What happens when the action may have occurred but the response/result is unavailable?

### Q7.1.1.1.1.1 — Recovery preconditions

Which combinations of idempotency, operation identity, object identity, authority validity and observability permit retry, and which require reconciliation first?

### Q8.1 — Outcome uncertainty

Can `FAILED` and `UNKNOWN` be separated by evidence rather than by timeout alone?

### Q8.1.1 — Unknown boundary

Is the unknown located at request, acceptance, execution, effect, observation or consequence?

### Q8.1.1.1 — Resolution

What new evidence can collapse the unknown into a known outcome?

### Q8.1.1.1.1 — Safe action

Can the system act while the unknown remains, or must action be prohibited until reconciliation?

### Q9.1 — Recovery semantics

Can recovery be derived from operation properties rather than from a generic retry flag?

## 3. Source map

### A. Protocol semantics

1. RFC 9110 HTTP Semantics.

It defines idempotent request semantics and explicitly distinguishes cases where a request may be repeated after communication failure from non-idempotent requests that should not be automatically retried without additional knowledge. It also defines `Retry-After` as server guidance for delaying a follow-up request. citeturn0search1turn1search4

### B. Distributed-service retry design

2. AWS Builders' Library — Making retries safe with idempotent APIs.
3. AWS Well-Architected retry guidance.
4. AWS Architecture Blog — Exponential Backoff and Jitter.

These sources establish a recurring operational pattern: transient faults can justify retry, but safe retry depends on idempotency; ambiguous mutation outcomes may require reconciliation; retries should be bounded and use backoff/jitter. citeturn0search0turn0search4turn1search0

### C. State/version evidence

5. Kubernetes API Concepts.

Kubernetes uses resource versions to identify server-side object versions and supports exact/not-older-than consistency semantics. This is concrete evidence that recovery and observation can depend on state revision, not only object identity. citeturn0search3

### D. Comparative retry policy

6. Google Cloud retry guidance.

The documented pattern distinguishes transient errors, idempotent/non-idempotent operations, exponential backoff, jitter, and bounded retry counts/deadlines. citeturn1search5turn1search11

## 4. Evidence

### E1 — Communication failure does not establish operation failure

RFC 9110 explicitly permits retrying idempotent requests after a connection failure because the client can repeat the intended effect safely. For non-idempotent operations, automatic retry is discouraged unless the client can establish that the operation was not applied or otherwise knows the operation is safe to repeat. citeturn0search1

Therefore:

`no response ≠ operation failed`.

The result can be `UNKNOWN` when the boundary between request and external processing has become unobservable.

### E2 — Idempotency changes the safe recovery set

AWS describes the central ambiguity directly: a request can time out from the client's perspective while the remote operation actually succeeds. Retrying without an idempotent contract can create duplicate side effects; reconciliation can determine whether the original effect occurred. Client request identifiers can also make repeated requests semantically equivalent and auditable. citeturn0search0

Therefore idempotency is not merely a performance feature. It is recovery evidence/semantics that can change `UNKNOWN → RETRY_ALLOWED`.

### E3 — Retry is not the same as recovery

A retry is one possible recovery action. It is safe only after the operation semantics permit repeating the operation.

Other recovery actions include:

`OBSERVE_AGAIN`
`RECONCILE`
`RECHECK_AUTHORITY`
`WAIT_FOR_OPERATION`
`COMPENSATE`
`STOP / HUMAN_DECISION`

AWS guidance also requires bounded retry counts/time and recommends exponential backoff and jitter rather than uncontrolled repetition. citeturn1search0turn1search6

### E4 — State revision can be essential to reconciliation

Kubernetes resource versions demonstrate a concrete model where object identity alone is insufficient to establish which state was observed. Exact or minimum-version reads can express consistency requirements. citeturn0search3

For Content Factory this supports retaining:

`external_object_id + observed_revision/version + observed_at`

when the external system exposes such identity.

### E5 — Backoff controls amplification, not semantic safety

Exponential backoff and jitter reduce synchronized retry pressure and retry storms, but they do not make a non-idempotent operation safe. AWS and Google Cloud guidance treats backoff, retry predicates, idempotency and retry limits as separate concerns. citeturn1search0turn1search11

Therefore:

`backoff ≠ idempotency`
`retry limit ≠ proof of safety`

## 5. State model derived from the evidence

The evidence supports keeping at least these distinct concepts:

```text
INTENDED_STATE
STATE_BEFORE
ACTION_INTERVAL
REQUEST_STATE
EXTERNAL_OPERATION_STATE
STATE_AFTER
OBSERVED_STATE
VERIFIED_STATE
DIVERGENCE
STALE_OBSERVATION
```

These are semantic descriptions, not yet proposed ontology classes.

The key distinction is between historical facts and current knowledge:

- `ACTION_ATTEMPTED` is a historical claim about what the factory did.
- `EXTERNAL_EFFECT_UNKNOWN` is a claim about what the factory does not currently know.
- `OBSERVED_STATE=S` is a claim about an observation at time T.
- `VERIFIED_STATE=S` is a stronger claim that the observation satisfied a declared verification rule.

A later observation can change current knowledge without rewriting the fact that the earlier action was attempted.

## 6. Uncertainty taxonomy

The research supports locating uncertainty at the narrowest unresolved boundary:

| Status | What is known | What remains unknown | Default recovery posture |
|---|---|---|---|
| NOT_SENT | No external request evidence | Whether anything crossed boundary | Safe to prepare/send if still authorized |
| REJECTED | External rejection evidence | No accepted operation under that request | Do not retry unless rejection is transient/retryable and semantics permit |
| ACCEPTED_PENDING | External acceptance + operation ID | Completion/effect | Wait/observe operation |
| EXECUTED_EFFECT_UNKNOWN | Execution may have occurred | Resulting external state | Reconcile/observe before repeating if mutation is non-idempotent |
| EFFECT_CONFIRMED | Resulting state/effect identified | Later consequence may remain | Do not repeat merely to obtain confidence |
| OBSERVATION_UNAVAILABLE | Action/effect evidence may exist | Current external state cannot be observed | Retry observation or reconcile through another source |
| REQUEST_OUTCOME_UNKNOWN | Request may or may not have reached external system | Acceptance/execution/effect | Reconcile if possible; otherwise prohibit unsafe retry |
| EFFECT_OUTCOME_UNKNOWN | Request/execution evidence exists | Whether target state changed | Reconcile before non-idempotent retry |
| CONSEQUENCE_UNKNOWN | Technical effect verified | Desired business consequence | Continue observation/measurement, not technical retry by default |
| DIVERGED | Observed state differs from intended/verified basis | Corrective action | Re-evaluate authority, preconditions and desired state |

The important result is that `UNKNOWN` is not one state. It is a location of epistemic uncertainty.

## 7. Recovery decision matrix

| Evidence / operation property | Safe next action | Reason |
|---|---|---|
| No request evidence + valid authority | SEND / EXECUTE | Nothing indicates the operation crossed the boundary |
| Explicit rejection + known non-transient cause | STOP / CORRECT | Repeating the same invalid operation adds no information |
| Explicit rejection + transient/retryable condition + safe semantics | RETRY_WITH_BACKOFF | External evidence identifies a retryable failure |
| Accepted + operation ID + asynchronous semantics | WAIT / OBSERVE | The operation is already externally represented |
| Timeout/no response + idempotent operation | RETRY_ALLOWED_WITH_SAME_INTENT_ID | Repetition has the same intended external effect; still bound retries |
| Timeout/no response + non-idempotent mutation | RECONCILE_BEFORE_RETRY | Original operation may already have happened |
| Timeout/no response + unknown idempotency | RECONCILE_OR_STOP | Safety cannot be inferred from transport failure |
| Effect confirmed + response lost | RECORD_RESULT / DO_NOT_DUPLICATE | External effect already established |
| Effect unknown + independent observation available | OBSERVE / RECONCILE | Observation can collapse uncertainty |
| Effect unknown + no observation path + high consequence | STOP / HUMAN_DECISION | No evidence path exists to establish safe repetition |
| Observation stale but version known | RE-OBSERVE_AT_REQUIRED_VERSION | Current evidence is insufficient for the required claim |
| Authority expired before recovery | RECHECK_AUTHORITY | Original authority cannot be silently inherited |
| Target revision changed concurrently | RECONCILE / REBASE / NEW_DECISION | Original preconditions no longer hold |
| Consequence unknown after technical effect verified | MEASURE_CONSEQUENCE | Technical retry does not address downstream uncertainty |

## 8. The recovery rule

The research supports a stronger rule than `retry on error`:

```text
RECOVERY ACTION
= f(
    unresolved boundary,
    operation semantics,
    idempotency,
    external identity,
    state/revision evidence,
    authority validity,
    observability,
    consequence/risk,
    retry budget/time
)
```

The recovery decision must first answer:

1. What exactly is unknown?
2. Could the operation already have taken effect?
3. Can that fact be established by observation/reconciliation?
4. If not, is repeating the operation semantically safe?
5. Is authority still valid for the recovery action?
6. Are the original target and preconditions still valid?
7. Is the consequence of duplication acceptable?
8. What bound stops repeated recovery?

Only then can `RETRY` become an allowed action.

## 9. Contradictions and negative evidence

### N1 — `Timeout = FAILED`

Rejected.

A timeout can occur after the external operation has succeeded. AWS uses this as the motivating case for idempotency and reconciliation. citeturn0search0

### N2 — `UNKNOWN = RETRY`

Rejected.

Unknown outcome is precisely the condition where repeating a non-idempotent mutation can duplicate the effect. RFC 9110 explicitly requires additional knowledge before automatic retry of non-idempotent requests. citeturn0search1

### N3 — `Idempotent = unlimited retry`

Rejected.

Idempotency controls semantic duplication; it does not remove operational limits. AWS and Google Cloud recommend bounded retries, backoff and deadlines. citeturn1search0turn1search11

### N4 — `Backoff = safe retry`

Rejected.

Backoff controls load amplification; it does not establish whether repeating the operation is semantically safe. citeturn1search0

### N5 — `Object ID = state identity`

Rejected.

A mutable object can retain one identity across many revisions. Kubernetes resourceVersion provides a concrete example of revision-level identity. citeturn0search3

### N6 — `Technical effect = desired consequence`

Rejected.

The Q4/Q6 evidence matrix already established that consequence is a separate proof target. Technical recovery should not repeat an action merely because downstream consequence evidence is missing.

## 10. Inference boundary

### Directly supported by external evidence

- Idempotency affects whether retry after communication failure is safe.
- Non-idempotent operations require additional knowledge before automatic retry.
- Ambiguous mutation outcomes can require reconciliation.
- Retry attempts should be bounded and use appropriate backoff/jitter.
- State/version identity can be necessary to distinguish current and stale observations.

### Inferred for Content Factory

- `UNKNOWN` should be classified by the unresolved boundary rather than represented as one undifferentiated failure state.
- Recovery should be selected from operation/evidence properties, not from an unconditional retry flag.
- `RECONCILE` is a first-class recovery action conceptually, distinct from `RETRY`.
- Authority must be revalidated for recovery actions when validity may have expired or conditions changed.
- External object identity and revision should be retained whenever the provider exposes them.

### Not yet proven

- Exact persistent representation of uncertainty/recovery in Content Factory.
- Whether recovery should become a generic capability primitive or remain an operation policy.
- Exact retry budget fields required by all external-system roles.
- Universal compensation semantics.
- Whether one generic reconciliation contract can cover publication, transaction, control and execution systems.

## 11. Decision

`EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE`

The existing research tree and effect boundary already contain the necessary conceptual distinctions. Q7–Q9 strengthen them by establishing a recovery decision rule:

`unknown boundary → evidence/reconciliation → operation safety → authority validity → recovery action`

No new ontology class, state machine or runtime retry mechanism is justified yet.

In particular, do **not** implement generic automatic retries at this stage. The repository currently has no proven external-effect integration, and the operating model explicitly records external-operation idempotency/reconciliation as not yet completed. fileciteturn235file0

## 12. Repository impact

- Durable research record added.
- No production implementation changes.
- No ontology changes.
- No new top-level folder.
- Existing `UNKNOWN_EXTERNAL_OUTCOME` boundary is strengthened rather than replaced.
- Existing separation of verification, acceptance and external effect remains valid. fileciteturn234file0

## 13. Research consistency

The result is consistent with:

- `RULES.md`: unknowns remain explicit; authority is contextual; no new primitive without demonstrated need. fileciteturn232file0
- `docs/32_external_system_research_tree.md`: Q7/Q8/Q9 explicitly cover state/time, uncertainty and recovery. fileciteturn243file0
- Q3 composition research: constituent operations retain independent recovery semantics. fileciteturn237file0
- Q4/Q6 evidence research: evidence must prove the specific claim/transition, not generic success. fileciteturn239file0
- `docs/10_effect_and_authority_boundaries.md`: ambiguous external effect remains `UNKNOWN_EXTERNAL_OUTCOME` and requires reconciliation rather than automatic retry. fileciteturn234file0

## 14. Derived questions

1. What is the minimum generic reconciliation contract across publication, transaction, execution and control systems?
2. Which external roles can expose authoritative operation identity and state revision?
3. When can reconciliation itself be performed safely without creating another external effect?
4. How should a recovery decision record preserve the exact evidence that permitted retry?
5. How should recovery interact with acceptance of an already-approved content revision?
6. Which GitHub operations provide enough identity/revision/effect evidence to instantiate this generic model?
7. What real external system should be used as the first controlled experiment for `UNKNOWN → RECONCILED → RECOVERY`?

## 15. Post-write verification

Required verification:

1. Fetch the exact record from `main`.
2. Confirm the commit and blob identity.
3. Confirm the record contains the decomposition, source map, evidence, uncertainty taxonomy, recovery matrix, contradictions, inference boundary and decision.
4. Confirm no production/model artifact was changed by this research cycle.
5. Confirm direct consistency with the Q4/Q6 evidence record and current external-effect boundary.
