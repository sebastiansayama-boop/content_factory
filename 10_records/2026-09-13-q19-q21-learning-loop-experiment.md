# Learning Loop Experiment Record — Q19 → Q21

Date: 2026-09-13
Record ID: REC-2026-09-13-LEARNING-LOOP-001
Status: COMPLETE

## Purpose

First bounded experiment of the Content Factory learning mechanism itself: convert existing research into a learning candidate, explicitly promote it into reusable memory, consume that memory in later work, and test whether the decision changes.

## Reconstruction

```text
Q15 research
  ↓
Q19 learning candidate
  ↓
Q20 explicit promotion decision
  ↓
MEM-001 reusable memory
  ↓
Q21 bounded provider evaluation
  ↓
decision delta
```

## Evidence chain

1. Research source: `10_records/2026-09-13-external-system-q15-idempotency-correlation-requirements-research.md`.
2. Learning candidate: `09_learning/2026-09-13-learning-q19-idempotency-correlation-boundary.md`, revision `8811878383a2e6a6847e2f4143a226fb1697e4e6`.
3. Promotion decision: `05_decision/2026-09-13-learning-001-promotion.md`, decision `DEC-2026-09-13-001`.
4. Reusable memory: `02_memory/2026-09-13-memory-001-idempotency-vs-correlation.md`, revision `MEM-2026-09-13-001-r1`.
5. Later work item: `03_working_context/2026-09-13-q21-memory-consumption-github-contents-recovery.md`, revision `WI-2026-09-13-001-r1`.
6. Decision demonstrating downstream effect: `05_decision/2026-09-13-q21-github-contents-recovery-posture.md`, decision `DEC-2026-09-13-002`.

## What was observed

The Q21 work item explicitly consumed MEM-001 while evaluating a concrete GitHub Contents API mutation class already described by Q12.

The memory caused the analysis to keep provider result identity separate from duplicate-safe retry semantics.

## Decision change

Counterfactual baseline recorded in Q21:

`result identity → stronger recovery posture`

Actual memory-informed posture:

`result identity → state evidence → evaluate duplication semantics → conditional recovery / reconciliation`

The selected decision therefore became `CONDITIONAL_RECOVERY_WITH_RECONCILIATION_FIRST`, rather than treating file/blob/commit identity alone as sufficient for automatic recovery.

## What was not observed

- No external GitHub mutation was performed.
- No new provider behavior was experimentally observed.
- No automatic retry was executed.
- No production outcome was measured.
- No claim is made that the promoted proposition is universally correct for all providers or operations.

## Interpretation

This experiment demonstrates a repository-level learning loop mechanism from research-derived learning through explicit promotion to downstream decision use.

It does **not** yet demonstrate closed-world empirical learning from Content Factory's own external effect. The downstream case reused previously researched GitHub behavior rather than generating a new external observation.

## Result classification

- Q19: `COMPLETED`
- Q20: `COMPLETED`
- Q21: `COMPLETED`
- Learning-loop mechanism: `DEMONSTRATED_FOR_INTERNAL_BOUNDED_USE`
- Real external-effect feedback loop: `NOT_PROVEN`

## Unknowns / next research

Q22 remains open: determine what concrete observable provider result would strengthen, weaken or falsify MEM-001 in an actual provider case. The first real external-effect case may provide the stronger test required to close the production feedback loop.

## Repository impact

No production implementation, ontology or generic infrastructure was changed. The experiment added one learning record, one explicit promotion decision, one reusable memory item, one bounded downstream work item, one downstream decision, and this durable reconstruction record.
