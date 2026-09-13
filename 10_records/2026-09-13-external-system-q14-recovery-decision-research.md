# External-System Research — Q14 Conditions for an Authorized Recovery Decision

Date: 2026-09-13
Research branch: External World → External Systems → Reconciliation → Recovery authorization
Status: COMPLETE
Decision: EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE
Confidence: HIGH for the decision criteria; MEDIUM for operation-specific thresholds because consequence/risk is domain-dependent

## 1. Question

Which conditions are sufficient to convert an observed external state into an authorized recovery decision?

The central distinction is:

`reconciliation evidence ≠ recovery authorization`

An observation may resolve what currently exists without establishing that a retry, compensation, wait, stop, or other action is safe.

## 2. Decomposition

### Q14.1 — Claim resolution

What exact unresolved claim must recovery resolve?

### Q14.1.1 — Evidence sufficiency

What observation is sufficient to resolve that claim?

### Q14.1.1.1 — State compatibility

Does the observed external state satisfy the intended target state and expected transition?

### Q14.1.1.1.1 — Attribution and concurrency

Can the observed state be attributed to the relevant interaction, and can concurrent changes be excluded or bounded?

### Q14.1.1.1.1.1 — Authority and idempotency

Is the proposed recovery action still authorized, and is repeating it semantically safe under the operation's duplication semantics?

### Q14.1.1.1.1.1.1 — Consequence and stopping rule

Are the consequence risk, time/retry budget and stopping conditions explicit enough to permit the action rather than merely observe more?

## 3. Source map

Primary sources:

1. AWS Builders Library, “Making retries safe with idempotent APIs.”
2. W3C PROV model for provenance, activity, agent responsibility and time.
3. GitHub mutation matrix from Q12.
4. Current Content Factory Q7–Q12 research records and governing rules.

AWS states that safe retry depends on idempotent operation semantics and explicit client request identity; it also describes parameter mismatch handling rather than assuming identical-looking requests represent identical intent. It emphasizes that reconciliation can still leave uncertainty about who created a resource. citeturn0search0

W3C PROV provides the provenance vocabulary needed to distinguish an activity, its inputs/outputs, responsible agents and temporal context. citeturn0search1turn0search2turn0search5

The repository rules explicitly require contextual/scoped authority, explicit unknowns, separation of observation/interpretation/decision/effect, and no automatic promotion of observation into knowledge or authority. fileciteturn266file0

## 4. Candidate recovery-decision predicate

The research supports this candidate predicate:

```text
RECOVERY ACTION IS AUTHORIZED
iff
    CLAIM IS EXPLICIT
AND EVIDENCE IS SUFFICIENT FOR THAT CLAIM
AND OBSERVED STATE IS COMPATIBLE WITH THE INTENDED TARGET
AND RELEVANT CONCURRENCY / REVISION BOUNDARY IS KNOWN
AND CAUSAL ATTRIBUTION IS SUFFICIENT OR THE ACTION IS SAFE WITHOUT IT
AND CURRENT AUTHORITY IS VALID FOR THIS ACTION
AND OPERATION DUPLICATION SEMANTICS ARE KNOWN
AND PROPOSED ACTION HAS BOUNDED CONSEQUENCES
AND RETRY / RECOVERY BUDGET IS WITHIN LIMIT
AND NO HIGHER-RISK UNKNOWN REMAINS UNRESOLVED
```

This is a research criterion, not a runtime contract.

## 5. The decision process

### Step 1 — State the claim

Recovery must start with a concrete claim, for example:

`Did interaction I cause target T to reach revision R?`

or:

`Is it safe to resend the mutation for target T?`

These are different claims and require different evidence.

A GET that proves current target state may answer the first only partially and may answer the second not at all.

### Step 2 — Identify the evidence boundary

Determine what is directly observed, what is inferred and what remains unknown.

For example:

```text
Observed: branch X currently points to commit C.
Inferred: desired target state may already hold.
Unknown: whether our previous mutation caused C to become current.
```

The unknown must remain explicit.

### Step 3 — Test state compatibility

The observed state must be compared against the exact intended target and revision, not merely against a broad notion of “success.”

A state is compatible only if the material properties required by the claim are satisfied.

Examples:

- file mutation: path + expected resulting blob/revision;
- ref update: exact ref + expected target SHA + relevant predecessor/concurrency semantics;
- PR update: PR identity + relevant desired fields/head/base/state;
- workflow: run identity + relevant run state/conclusion and desired consequence.

### Step 4 — Evaluate attribution

If the recovery action is safe regardless of who caused the observed state, causal attribution may not be necessary.

If the action depends on whether this interaction already executed, attribution becomes material.

This yields an important rule:

`attribution requirement is claim-dependent, not universally mandatory.`

For example, if the desired state is an idempotently enforced configuration and the current state exactly matches it, a recovery decision may stop without proving which actor produced it. Conversely, if repeating the action would create a duplicate charge, duplicate publication or irreversible side effect, causal attribution becomes much more important.

### Step 5 — Evaluate concurrency

The recovery decision must account for intervening changes.

A previously observed state can become stale before recovery is authorized. Mutable external systems therefore require either:

- a fresh observation;
- an exact revision/precondition;
- a compare-and-set / conditional mutation;
- or another mechanism that bounds concurrent change.

Without such a boundary, the factory may make a recovery decision against a state that no longer exists.

### Step 6 — Revalidate authority

Authority must be valid for the proposed recovery action at the time of recovery.

The original authority to attempt an operation does not automatically imply authority to retry, compensate, cancel, publish again or mutate a different revision.

This follows the repository rule that authority is contextual and scoped and cannot be inferred from process completion or object ownership. fileciteturn266file0

### Step 7 — Evaluate duplication semantics

The question is not “can the request technically be sent again?” It is:

`what happens if the original request actually succeeded and this recovery action happens too?`

If the answer is “no additional side effect and same semantic outcome,” retry may be eligible.

If the answer is “another resource, charge, publication, message, workflow or irreversible effect may occur,” automatic retry is not justified without stronger idempotency/correlation evidence.

AWS's idempotency guidance explicitly uses caller-provided request IDs to distinguish repeated requests and warns against assuming that identical parameters necessarily represent duplicate intent. citeturn0search0

### Step 8 — Bound consequence

Even a technically safe retry may be operationally inappropriate if the consequence is high-risk or the evidence is weak.

Recovery must therefore consider:

- financial/irreversible consequence;
- external audience or publication scope;
- authority sensitivity;
- duplication impact;
- privacy/security consequence;
- time sensitivity;
- downstream propagation;
- compensation availability.

### Step 9 — Apply stopping rule

The system needs an explicit terminal decision rather than indefinite retries.

Candidate actions are:

```text
STOP / CLAIM SATISFIED
OBSERVE_AGAIN
RECONCILE
WAIT_FOR_OPERATION
RETRY
COMPENSATE
ESCALATE_TO_HUMAN
```

The action should be selected from the unresolved claim and evidence state, not from a generic “error = retry” rule.

## 6. Recovery decision matrix

| Evidence / condition | Candidate decision | Why |
|---|---|---|
| Desired state exactly observed, no harmful duplicate possible | STOP / CLAIM SATISFIED | Repeating provides no benefit and may add risk |
| Desired state not observed, original execution definitely not possible | RETRY if authority and preconditions valid | No ambiguous prior effect remains |
| Desired state not observed, prior execution may have occurred, idempotency supported | RETRY WITH SAME IDENTITY | Provider can distinguish duplicate from new intent |
| Desired state not observed, prior execution may have occurred, no idempotency | RECONCILE / HUMAN DECISION | Duplicate consequence remains possible |
| State observed but causal attribution matters and is unresolved | OBSERVE / RECONCILE / ESCALATE | State alone does not answer the claim |
| Observation stale or concurrent change possible | OBSERVE_AGAIN / CONDITIONAL ACTION | Decision must use current revision boundary |
| Authority expired or changed | STOP / REAUTHORIZE | Original authority cannot silently be reused |
| Operation still plausibly pending | WAIT_FOR_OPERATION / OBSERVE | Retry may duplicate a live operation |
| High-risk irreversible effect and evidence incomplete | HUMAN_DECISION | Automation should not manufacture certainty |

This matrix is intentionally policy-level. It does not define automatic retry behavior.

## 7. The important distinction: safe action versus proven history

A recovery action can be safe without proving the exact history.

Example:

```text
Claim: target should equal revision R.
Observation: target currently equals R.
Duplicate consequence: none.
Authority: no further mutation required.

Decision: STOP.
```

There is no need to prove who caused R because the desired state itself satisfies the claim and no additional action is required.

Contrast:

```text
Claim: one external publication was performed exactly once.
Observation: publication target contains matching content.
Duplicate consequence: second publication is harmful or materially different.

Decision: attribution/reconciliation remains necessary.
```

Therefore “sufficient evidence” is defined relative to the recovery claim and consequence, not by a universal evidence level.

## 8. Evidence freshness

A recovery decision is a temporal claim. Evidence sufficient at time `t1` may become insufficient at `t2` if the external state is mutable or authority expires.

Therefore the record should distinguish:

```text
observed_at
observation_revision
observation_source
authority_valid_at
recovery_decision_at
```

These are not interchangeable timestamps. W3C PROV explicitly treats time as relevant to when entities are generated/used and when activities start/end, supporting the need for temporal provenance without dictating a local schema. citeturn0search2

## 9. Contradictions / rejected simplifications

### N1 — `observed desired state = retry is safe`

Rejected.

If desired state already holds, retry may be unnecessary or harmful. Observation can instead justify stopping.

### N2 — `not observed = retry`

Rejected.

The original action may still be pending or may have succeeded without visible state yet.

### N3 — `attribution is always required`

Rejected.

Attribution is necessary only when the recovery claim or consequence depends on it.

### N4 — `same request parameters = same intent`

Rejected.

AWS explicitly identifies cases where identical parameters may represent separate legitimate intent and recommends explicit client request identity for idempotent semantics. citeturn0search0

### N5 — `original authorization covers recovery indefinitely`

Rejected.

Authority is contextual and scoped; recovery can be a distinct action.

## 10. Inference boundary

### Established

- Idempotency and explicit request identity can make repeated actions safely distinguishable. citeturn0search0
- Provenance must preserve identifiable activities/entities/agents and relevant temporal context. citeturn0search1turn0search2
- Current repository rules require explicit authority and unknowns and prohibit collapsing observation into decision or authority. fileciteturn266file0

### Derived

- Recovery authorization should be claim-specific.
- Attribution is conditional on the claim/consequence, not a universal prerequisite.
- Safe recovery requires a conjunction of evidence, state compatibility, concurrency control, authority, duplication semantics and bounded consequence.

### Unknown

- Exact risk thresholds for different Content Factory effect classes.
- Whether a future implementation should encode these as policy rules, decision tables or capability-specific contracts.
- What the first real external effect will reveal about missing criteria.

## 11. Decision

`EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE`

The repository should not introduce a universal “recovery allowed” boolean or generic retry state from this research alone.

The current model is sufficient if recovery is treated as a claim-specific decision requiring explicit evidence and current authority.

The next research question is Q15: where provider-side idempotency or factory-generated correlation identifiers become necessary prerequisites for safely recoverable external operations.

## 12. Repository impact

- Research record added.
- No production implementation change.
- No ontology change.
- No recovery primitive introduced.
- Existing Q7–Q12 recovery/reconciliation model extended with a decision boundary.

## 13. Verification

The conclusion was checked against the current governing rules and protocol. The repository requires external research for unresolved structural questions, explicit evidence-to-decision bridges, preservation of unknowns and post-write consistency verification. fileciteturn267file0
