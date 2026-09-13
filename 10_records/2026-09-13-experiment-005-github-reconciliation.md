# Experiment-005 — GitHub operation → observed result → reconciliation

Status: `IN PROGRESS`

## Question

Can the Factory GitHub adapter represent a real directed repository operation, observe the resulting GitHub state independently, and reconcile expected vs observed state without making GitHub semantic/runtime authority?

## Factory operation intent

```text
operation_id: op-005-live-record
work_item_id: wi-github-005
operation: update_file
repository: sebastiansayama-boop/content_factory
branch: experiment/005-github-reconciliation-proof
path: 10_records/2026-09-13-experiment-005-github-reconciliation.md
```

The intent is an adapter instruction, not proof of execution.

## Live operation

The connected GitHub integration executed the `update_file` operation above on the experiment branch.

The operation result commit must be fetched independently before it can be treated as observed evidence.

## Boundary

Prove only:

```text
Factory operation intent
→ GitHub operation
→ actual GitHub result
→ independent observation
→ normalized evidence
→ reconciliation
```

Do not infer from this experiment:

```text
GitHub state = Factory state
GitHub operation success = semantic acceptance
GitHub merge = publication authority
repository state = external business outcome
```

## Implementation

Added to `src/content_factory/github_adapter.py`:

- `GitHubOperationIntent` — explicit Factory-side operation intent;
- `GitHubOperationObservation` — independently observed GitHub result;
- `GitHubReconciliation` — explicit comparison with separate unknowns and mismatches;
- `reconcile_github_operation()` — fail-closed reconciliation function.

Added tests for successful reconciliation, missing observation, mismatched identity/path/branch, and commit mismatch.

## Verification status

Pending independent fetch of the live operation result and CI.
