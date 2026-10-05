# Claim Strength QC Calibration — 2026-10-05

## Scope

Calibration dataset: `library/telegram/computer-games-series.json`.

The library contains 10 published episodes, 51 claims, 50 evidence items and 55 source records. The expected 48-claim count was outdated; the current repository contains 51 claims.

## Policy

Claim strength:
- 0 — directly descriptive fact.
- 1 — limited interpretation.
- 2 — bounded synthesis / broad interpretation.
- 3 — material causal or broad general claim.
- 4 — decisive, universal, or exclusive causal/general claim.

Evidence strength:
- 0 — no resolvable evidence.
- 1 — evidence reference exists but is not directly source-backed.
- 2 — structural evidence/source linkage exists without direct excerpt support.
- 3 — at least one direct, source-backed evidence item.
- 4 — direct evidence backed by at least two distinct source IDs.

Support index:

`evidence_strength - claim_strength`

- >= 0: PASS
- -1: REVIEW
- <= -2: FAIL

Repair:
- PASS -> NONE
- REVIEW on causality/generalization -> WEAKEN
- REVIEW on lower-risk claims -> ADD_EVIDENCE
- FAIL without evidence on strong claims -> REMOVE
- FAIL with partial evidence -> WEAKEN

## Calibration Result

| Metric | Result |
|---|---:|
| Claims | 51 |
| PASS | 51 |
| REVIEW | 0 |
| FAIL | 0 |
| Fact claims | 39 |
| Causality claims | 11 |
| Generalization claims | 1 |
| Interpretation claims | 0 |

No current claim exceeds its measured evidence-strength level under this deterministic policy.

## Important limitation

This first version measures claim strength from surface language and evidence structure. It does not yet verify semantic scope expansion (for example, turning a claim about some games into a claim about the entire industry). That should be the next calibration layer, not a hidden assumption.

## Implementation

The policy lives in `src/content_factory/claim_strength_qc.py`.

It is enforced by `QualityGate` and exposed as `claim_strength_assessments` in the QC result.

The test suite includes both synthetic boundary cases and regression calibration against the 51-claim historical dataset.
