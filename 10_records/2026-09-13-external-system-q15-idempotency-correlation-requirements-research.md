# External-System Research — Q15 Idempotency and Correlation Requirements

Date: 2026-09-13
Research branch: External World → External Systems → Reconciliation → Idempotency / correlation
Status: COMPLETE
Decision: EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE
Confidence: HIGH for the semantic distinctions; MEDIUM for operation-specific admission thresholds

## 1. Question

Which external mutation classes require provider-side idempotency keys or client-generated correlation identifiers before execution can be admitted as safely recoverable?

The question is deliberately narrower than “which APIs support idempotency?” The factory needs to know when lack of an idempotency/correlation mechanism makes ambiguous recovery unacceptable, when a factory-side correlation identifier is sufficient for provenance but not retry safety, and when no identifier is required because the operation is naturally safe to repeat or can be reconciled by exact state comparison.

## 2. Decomposition

### Q15.1 — Duplicate consequence

Can repeating the external action create an additional material effect?

### Q15.1.1 — Operation semantics

Is the operation naturally idempotent, conditionally idempotent, non-idempotent, or unknown?

### Q15.1.1.1 — Provider support

Does the provider expose a durable idempotency key, conditional precondition, operation ID or equivalent mechanism?

### Q15.1.1.1.1 — Factory correlation

If provider identity is absent, can a factory-generated correlation ID be propagated into a provider-visible or observable field?

### Q15.1.1.1.1.1 — Reconciliation strength

Can a later observation uniquely or sufficiently correlate a prior attempt to its result?

### Q15.1.1.1.1.1.1 — Admission threshold

What combination of operation semantics, identity and evidence is sufficient to classify the operation as safely recoverable?

## 3. Source map

Primary sources:

1. AWS Builders Library, “Making retries safe with idempotent APIs.”
2. W3C PROV-DM / PROV-O for activity identity, responsibility, provenance and time.
3. GitHub Q12 mutation identity matrix for concrete provider variation.
4. Current Content Factory Q7–Q14 research and governing rules.

AWS explicitly recommends unique caller-provided request identifiers for operations where duplicate detection is necessary. It explains that the identifier makes caller intent explicit, supports auditing and allows a service to recognize a retry of the same request; it also describes parameter mismatch handling when the same token is reused with different intent. citeturn0search0

W3C PROV supports explicit identity for activities/entities/agents and provenance relations but does not define idempotency as an application-level retry guarantee. This distinction is important: provenance can identify an attempted activity without making repeating it safe. citeturn0search2turn0search5

## 4. Core distinction

Three mechanisms must not be conflated:

```text
CORRELATION ID
= identifies / links an interaction across records and observations

OPERATION ID
= identifies a provider-side execution or durable operation when the provider exposes one

IDEMPOTENCY KEY
= provider contract that gives repeated requests equivalent / duplicate-safe semantics
```

They can coexist, but one does not automatically substitute for another.

A factory-generated correlation ID without provider support cannot by itself make a retry safe.

A provider operation ID without an idempotency guarantee can identify an already-created execution without making a second execution safe.

An idempotency key without durable factory provenance can make the provider retry-safe while leaving the factory unable to reconstruct its own authorization/intent history.

Therefore a safely recoverable interaction may need more than one identity layer.

## 5. Operation classification

### Class A — Naturally idempotent state-setting operation

Definition:

Repeating the same operation against the same target produces no additional material effect beyond establishing the same desired state.

Examples may include exact state replacement or conditional configuration updates, but this classification must be established from the provider contract rather than inferred from the HTTP verb or API shape.

Requirement:

- provider idempotency key: not necessarily required;
- factory correlation ID: still recommended for provenance when material;
- exact target + desired revision/state: required for reconciliation;
- conditional precondition: required when concurrent mutation can make a stale retry unsafe.

The important point is that natural idempotency can reduce the need for a provider token, but does not eliminate the need to know what the factory intended.

### Class B — Conditionally idempotent operation

Definition:

A repeated request is safe only when a stable request identity, precondition, revision, or provider-specific deduplication rule is preserved.

Requirement:

- stable identity or conditional precondition is required;
- reuse the same provider-recognized identity for retries when the provider defines it;
- preserve the original request parameters associated with that identity;
- do not generate a fresh identity for a retry of the same unresolved interaction.

AWS's client-token pattern is the canonical example: the same caller and request identifier allows the service to recognize repeated requests, while changing parameters under the same identifier is treated as a different intent and should not silently be merged. citeturn0search0

### Class C — Non-idempotent external effect

Definition:

Repeating the action can create an additional material effect even when the input is identical.

Examples include operations whose semantic result is “create another occurrence,” “send another message,” “publish another delivery,” “charge again,” or otherwise trigger another external event.

Requirement:

- provider-side idempotency or equivalent deduplication is strongly required for automatic recovery;
- if absent, factory-generated correlation alone is insufficient;
- ambiguous outcomes should normally enter reconciliation/human decision rather than automatic retry;
- a provider operation/execution ID can improve attribution but does not substitute for duplicate-prevention semantics.

### Class D — Asynchronous operation with durable execution identity

Definition:

The initial request starts an external execution whose result is represented by a durable operation/run resource.

Requirement:

- capture the provider execution/operation ID when available;
- preserve factory correlation ID;
- reconcile execution state by that ID;
- wait/reobserve rather than issue a duplicate start when the original execution may still be active;
- if the provider does not return a durable operation ID, safe recovery depends on whether another unambiguous correlation mechanism exists.

Q12 identified GitHub workflow dispatch with a returned workflow-run identity as an example of this stronger model.

### Class E — Resource creation without provider idempotency

Definition:

A mutation can create a durable resource, but the provider exposes no idempotency key and no operation identity.

Requirement:

- factory correlation ID is required for provenance but is not sufficient for automatic retry unless it is observable on the created resource;
- reconcile target/resource state and creation attributes;
- if multiple matching resources could plausibly exist, automatic recovery should stop at ambiguity;
- human decision or provider-side search/audit evidence may be required.

AWS explicitly notes the difficulty of determining whether a resource was created by the current provisioning process or another process, which is precisely why caller-provided request identifiers can be valuable. citeturn0search0

## 6. Requirement matrix

| Operation semantics | Provider idempotency key | Provider operation ID | Factory correlation | Conditional revision/precondition | Automatic recovery eligibility |
|---|---|---|---|---|---|
| Naturally idempotent | Optional | Optional | Required for material provenance | Usually required for mutable/concurrent state | Potentially yes if exact state semantics are proven |
| Conditionally idempotent | Required when provider contract defines it | Helpful | Required | Often required | Yes, using the same identity and preconditions |
| Non-idempotent side effect | Strongly required for automatic retry | Helpful but insufficient alone | Required | Helpful but insufficient alone | Generally no without duplicate-prevention guarantee |
| Async durable operation | Helpful/required depending on start semantics | Strongly preferred | Required | Operation-specific | Yes for observation/wait when execution identity is known; retry only if start is idempotent |
| Resource creation, no provider idempotency | Absent | Absent | Required | Strongly useful | Usually no after ambiguous outcome unless exact resource correlation is available |
| Mutation with exact conditional state transition | May be unnecessary | Optional | Required | Strongly required | Potentially yes when compare-and-set semantics make duplicate execution safe |

This matrix is a policy classification, not an implementation contract.

## 7. Why factory correlation remains necessary

A provider idempotency key is scoped to the provider's semantics. The factory still needs to preserve:

```text
who / what initiated the interaction
which intent was authorized
which capability was selected
which target/revision was intended
which authority was active
which provider identity was supplied
what evidence was observed later
```

W3C PROV's separation of activity, entity and agent responsibility supports preserving these relationships independently of whether the provider has an idempotency mechanism. citeturn0search2turn0search5

Therefore:

`provider idempotency ≠ factory provenance`

and:

`factory correlation ≠ provider idempotency`.

## 8. When a factory-generated correlation ID is enough

A factory-generated correlation ID can be enough for reconciliation-oriented provenance when:

1. the external action itself is not going to be repeated automatically;
2. the ID can be attached to or correlated with provider evidence;
3. later observation can establish the resulting resource/effect without requiring duplicate execution;
4. the factory uses the correlation to connect evidence, not to claim that the provider honored it.

Example:

```text
factory interaction I
→ provider request carrying correlation C
→ provider creates resource R
→ later GET / audit record exposes C + R
→ factory attributes R to I with evidence
```

In this case C strengthens attribution. It does not become an idempotency key unless the provider contract explicitly says so.

## 9. When correlation is not enough

Correlation is insufficient when:

- the provider ignores the identifier;
- the identifier is not observable after execution;
- multiple resources can share the same correlation metadata;
- retry can create a second irreversible effect;
- provider execution may still be pending;
- provider-side deduplication is absent;
- the external operation has no reliable state query;
- the consequence of duplicate execution exceeds the evidence available for attribution.

In those cases the correct result may be:

`UNKNOWN → RECONCILIATION REQUIRED → HUMAN DECISION`

rather than:

`UNKNOWN → GENERATE NEW CORRELATION ID → RETRY`.

Generating a new ID for an unresolved original request can be especially dangerous because it explicitly tells an idempotent provider that the retry is a new request.

## 10. Admission rule candidate

A safely recoverable external operation should not be admitted merely because an API endpoint is reachable.

Candidate admission criterion:

```text
ADMIT_AS_SAFELY_RECOVERABLE
iff
    operation semantics are classified
AND duplicate consequence is bounded
AND exact intent/target can be identified
AND factory interaction identity is durable
AND authority can be revalidated
AND
    (
      provider idempotency / deduplication is available
      OR operation is proven naturally idempotent
      OR exact conditional state semantics make repetition safe
      OR a durable provider operation can be observed without restarting it
    )
AND reconciliation evidence can be obtained
AND stopping / escalation policy exists
```

If these conditions are not met, the operation may still be executable, but it should not be classified as automatically recoverable.

This distinction is important:

`EXECUTABLE ≠ SAFELY RECOVERABLE`.

## 11. Contradictions / rejected simplifications

### N1 — `every external mutation needs an idempotency key`

Rejected.

Some operations are naturally idempotent or have conditional state semantics sufficient to make repetition safe without a provider token. The contract must establish this; HTTP method names are not enough.

### N2 — `factory correlation ID makes retry safe`

Rejected.

Correlation identifies an interaction but does not create provider-side duplicate suppression.

### N3 — `operation ID makes retry safe`

Rejected.

An operation ID can identify a running/completed operation. It does not necessarily prevent starting another operation.

### N4 — `new correlation ID is a safe retry`

Rejected.

For providers that support idempotency, a new ID can explicitly convert a retry into a new operation. The original identity must be reused for a retry of the same unresolved intent.

### N5 — `no idempotency means no external action is possible`

Rejected.

The action may be executable, but its recoverability classification changes. A non-idempotent operation without reliable reconciliation may require human-controlled recovery rather than automatic retry.

## 12. Inference boundary

### Established by external evidence

- Explicit client request identifiers are a recognized mechanism for making duplicate intent unambiguous and supporting safe retries. citeturn0search0
- Provenance and responsibility are distinct from retry/idempotency semantics. citeturn0search2turn0search5

### Derived for Content Factory

- Idempotency requirement is operation-semantic, not provider-generic.
- Provider idempotency, provider operation identity and factory correlation are separate mechanisms.
- A capability can be executable while remaining not safely recoverable.
- The factory should preserve its own interaction identity even when provider-side idempotency is available.

### Unknown

- Which first real Content Factory external effect will actually require provider idempotency versus conditional state semantics.
- Whether the first external destination supports client-supplied correlation in an independently observable form.
- Whether a concrete effect class requires human-only recovery or can be made safely recoverable with a bounded provider contract.

## 13. Decision

`EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE`

Q15 establishes a classification boundary rather than a new primitive:

```text
EXECUTABLE
        ↓
RECOVERABLE
        ↓
AUTOMATICALLY RECOVERABLE
```

Each transition requires stronger evidence and semantics.

Provider idempotency is strongly required for automatic recovery of materially non-idempotent effects. Factory correlation is broadly required for material provenance, but it does not itself make retries safe. Provider operation identity is valuable for asynchronous reconciliation but is not equivalent to duplicate prevention.

No generic idempotency or correlation layer should be implemented before a concrete external-effect case establishes its exact contract.

## 14. Repository impact

- Research record added.
- No production implementation change.
- No ontology change.
- No generic idempotency primitive introduced.
- No external mutation performed.
- Q13 and Q14 remain research-level candidate criteria.

## 15. Derived questions

Q16 — What is the first concrete Content Factory external-effect class for which the Q13–Q15 criteria can be tested without introducing unnecessary infrastructure?

Q17 — Can one real external provider demonstrate the full chain `intent → authority → correlation → execution → observation → recovery` with a bounded, reversible or low-consequence effect?

Q18 — Which provider-specific fields should be preserved as evidence versus normalized into factory-level identity/provenance?

## 16. Verification

The conclusion was checked against the current repository governance: research must be reconciled rather than promoted directly to implementation; no new primitive is justified without a demonstrated problem; external effect requires explicit authority; and the final state must preserve unknowns. fileciteturn266file0turn267file0
