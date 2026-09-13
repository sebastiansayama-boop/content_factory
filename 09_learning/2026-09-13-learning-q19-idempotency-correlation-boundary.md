# Learning Record — Q19 Idempotency vs Correlation

Date: 2026-09-13
Learning ID: LEARN-2026-09-13-001
Status: PROMOTED
Promotion decision: `05_decision/2026-09-13-learning-001-promotion.md`
Promoted memory: `02_memory/2026-09-13-memory-001-idempotency-vs-correlation.md`
Promoted memory revision: `MEM-2026-09-13-001-r1`

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

Rejected by Q15.

B. `A factory correlation ID is sufficient for safe retry.`

Rejected by Q15.

C. `A provider operation ID is sufficient for safe retry.`

Rejected by Q15.

D. `No idempotency mechanism means the external action cannot be executed.`

Rejected by Q15.

## 6. Uncertainties

The learning does not establish:

- which concrete first Content Factory provider will expose which identity/idempotency mechanisms;
- whether a specific provider supports factory-visible correlation after execution;
- whether a concrete external effect can be made automatically recoverable;
- the provider-specific admission threshold for any particular capability.

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

The promoted memory does not authorize an implementation change, external action, new ontology class, or generic idempotency infrastructure.

## 9. Promotion result

Explicit promotion decision `DEC-2026-09-13-001` accepted this proposition as bounded reusable knowledge.

The promotion preserves the distinction between research evidence, learning interpretation, reusable knowledge and authority. It also preserves the unresolved provider-specific questions.

## 10. Evidence boundary

### Supported by source research

- correlation, operation identity and idempotency are distinct mechanisms;
- correlation alone does not make retry safe;
- operation identity alone does not make retry safe;
- automatic recoverability requires stronger conditions than mere executability.

### Not established by this learning

- universal provider requirements;
- correctness of any future provider-specific implementation;
- real-world external effect behavior for Content Factory.

## 11. Decision

`PROMOTED / REUSABLE_MEMORY_CREATED`

## 12. Derived questions

- Q21: If promoted, can a subsequent bounded work item retrieve this memory and demonstrably change its decision rather than merely cite it?
- Q22: What observable result would strengthen, weaken, or falsify the promoted proposition in a concrete provider case?
