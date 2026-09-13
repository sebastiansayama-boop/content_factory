# EXPERIMENT-001 — Memory-informed real external outcome

Status: PROTOCOL READY / EXECUTION PENDING
Issue: #2

## Question
Can reusable memory change a subsequent decision and execution in a bounded real external case while preserving enough evidence to evaluate the resulting external outcome?

## Chain under test
`MEM-2026-09-13-001-r1 → decision delta → execution delta → external outcome → evaluation`

## Memory consumed
`MEM-2026-09-13-001-r1`

Proposition: correlation identity, provider operation identity, and duplicate-safe semantics are distinct. Recoverability requires evidence about duplication semantics or an equivalent conditional-state contract; identity alone is insufficient.

## Experimental design
1. Establish target state before any mutation.
2. Establish the baseline action that would have been selected without the memory proposition.
3. Explicitly record the memory-informed decision and how it differs from that baseline.
4. Execute one bounded real external operation.
5. Capture provider-side and target-state evidence.
6. Do not infer causality from the outcome alone. Evaluate competing explanations.
7. Classify the memory proposition as STRENGTHENED, WEAKENED, UNCHANGED, or UNRESOLVED.

## Controls
- No automatic retry.
- No automatic authority escalation.
- No automatic memory promotion.
- No self-modifying policy.
- No production-wide behavior change.
- If required execution/evidence capability is absent, the absence is itself the experimental result.

## Evidence required
- memory revision consumed
- decision record
- baseline/counterfactual action
- actual action
- external target identity and pre-state
- provider operation/request identity
- post-state
- externally observable result
- provenance links
- uncertainty and attribution assessment

## Outcome interpretation
A positive external result is not sufficient to establish that memory caused the result. The strongest result is a reproducible chain showing that memory changed the decision, the decision changed execution, execution changed the external state, and the evidence supports or weakens the memory proposition.

## Execution status
No external mutation performed by creating this protocol. Actual execution remains pending until the runtime/provider boundary is inspected and the bounded target is selected.