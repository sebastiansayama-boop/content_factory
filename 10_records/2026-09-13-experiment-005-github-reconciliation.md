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

The connected GitHub integration executed the `update_file` operation above.

Returned commit: `4b143b3cfb5dcbe574db8cb483e4dc9f0178dda4`.

## Independent observation

The returned commit was fetched independently from GitHub. The fetched commit exists and contains the intended record path on the experiment branch.

Observed commit evidence:

```text
repository: sebastiansayama-boop/content_factory
commit_sha: 4b143b3cfb5dcbe574db8cb483e4dc9f0178dda4
path: 10_records/2026-09-13-experiment-005-github-reconciliation.md
```

The observation is evidence of repository state, not semantic acceptance.

## Reconciliation target

The adapter will reconcile the operation intent against the independent observation using:

```text
operation_id = op-005-live-record
operation = update_file
repository = sebastiansayama-boop/content_factory
branch = experiment/005-github-reconciliation-proof
path = 10_records/2026-09-13-experiment-005-github-reconciliation.md
expected_commit_sha = 4b143b3cfb5dcbe574db8cb483e4dc9f0178dda4
```

Expected result: `reconciled = true`.

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

Implementation and live observation are present. Repository CI remains pending.
