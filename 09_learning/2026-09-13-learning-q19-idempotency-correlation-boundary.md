# Learning Record — Q19 Idempotency vs Correlation

Date: 2026-09-13
Learning ID: LEARN-2026-09-13-001
Status: CANDIDATE

## 1. Trigger / question

Can an existing research result be converted into a learning candidate without adding facts that were not observed or established by the research?

Source research: `10_records/2026-09-13-external-system-q15-idempotency-correlation-requirements-research.md`.

Specific learning question:

> What reusable distinction from Q15 should affect future Content Factory external-effect design and recovery analysis?

## 2. Source and evidence

Primary source record:

- `10_records/2026-09-13-external-system-q15-idempotency-correlation-requirements-research.md`

Q15 reports external evidence from AWS Builders Library and W3C PROV, plus the repository's Q12–Q14 research. The research explicitly distinguishes:

- factory correlation ID: identifies/links an interaction across records and observations;
- provider operation ID: identifies a provider-side execution or durable operation when exposed;
- provider idempotency key: a provider contract that gives repeated requests duplicate-safe semantics.

Q15 also rejects the propositions that a factory correlation ID automatically makes retry safe, or that an operation ID automatically makes retry safe.

The source record classifies the distinction as established by external evidence where the external sources directly support it, and as derived for Content Factory where the repository applies that evidence to factory design.

No production execution, external mutation, or local provider behavior is claimed here.

## 3. Observation / established input

The source research establishes that provenance/correlation and retry/idempotency are different semantic mechanisms, and that a factory-generated correlation identifier does not itself provide provider-side duplicate suppression.

The source research further classifies external operations by their duplication semantics and concludes that `EXECUTABLE` is not equivalent to `SAFELY RECOVERABLE`.

## 4. Interpretation

Reusable learning candidate:

> When evaluating an external capability for automatic recovery, do not treat correlation identity or provider execution identity as evidence of duplicate-safe retry. Recoverability must be evaluated from the operation's duplication semantics and the provider's actual deduplication/idempotency or equivalent conditional-state contract.

This learning is narrower than a rule that every external mutation requires an idempotency key. Q15 explicitly rejects that simplification because some operations may be naturally idempotent or safely repeatable through proven conditional state semantics.

## 5. Alternative explanations / competing interpretations

A. `Every externally mutating operation needs a provider idempotency key.`

Rejected by Q15. The required mechanism depends on operation semantics; natural idempotency or exact conditional state semantics can sometimes provide sufficient safety.

B. `A factory correlation ID is sufficient for safe retry.`

Rejected by Q15. Correlation supports attribution/provenance but does not create provider-side duplicate suppression.

C. `A provider operation ID is sufficient for safe retry.`

Rejected by Q15. It can identify an existing execution without preventing a second execution.

D. `No idempotency mechanism means the external action cannot be executed.`

Rejected by Q15. The action may be executable while remaining unsuitable for automatic recovery.

## 6. Uncertainties

The learning candidate does not establish:

- which concrete first Content Factory provider will expose which identity/idempotency mechanisms;
- whether a specific provider supports factory-visible correlation after execution;
- whether a concrete external effect can be made automatically recoverable;
- the provider-specific admission threshold for any particular capability.

These remain unknown until a concrete provider/capability case is examined.

## 7. Proposed consequence

For future external-capability analysis, explicitly classify these separately before claiming recoverability:

```text
operation semantics
provider idempotency / deduplication
provider operation identity
factory correlation identity
reconciliation evidence
```

A capability should not be classified as automatically recoverable merely because an endpoint is callable or an execution can be identified.

## 8. Impact scope

`external-effect design / recovery / provider capability evaluation`

This candidate does not authorize an implementation change, external action, new ontology class, or generic idempotency infrastructure.

## 9. Promotion eligibility assessment

The candidate is eligible for consideration for explicit promotion because:

- its source research is reconstructable;
- the proposition is stated separately from the underlying evidence;
- competing simplifications are recorded and rejected;
- uncertainty and applicability limits are explicit;
- the proposed consequence is bounded.

Promotion is not implied by this record. An explicit decision must determine whether this proposition becomes reusable memory.

## 10. Evidence boundary

### Supported by source research

- correlation, operation identity and idempotency are distinct mechanisms;
- correlation alone does not make retry safe;
- operation identity alone does not make retry safe;
- automatic recoverability requires stronger conditions than mere executability.

### Not established by this record

- universal provider requirements;
- correctness of any future provider-specific implementation;
- real-world external effect behavior for Content Factory.

## 11. Decision

`CANDIDATE / USER-DECISION-REQUIRED-FOR-PROMOTION`

No implementation or model change follows from Q19 alone.

## 12. Derived questions

- Q20: Is this learning proposition sufficiently scoped and evidenced to be explicitly promoted into reusable memory?
- Q21: If promoted, can a subsequent bounded work item retrieve this memory and demonstrably change its decision rather than merely cite it?
- Q22: What observable result would strengthen, weaken, or falsify the promoted proposition in a concrete provider case?
