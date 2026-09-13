# EXPERIMENT-002 — GitHub-Native Control Path

Date: 2026-09-13
Status: `COMPLETE / BOUNDED LOCAL PROOF`

## Objective
Test whether a bounded repository work item can use GitHub as the repository-centric control plane without adding a bespoke factory control mechanism.

## Path under test

`Issue → branch → PR → CI → merge → repository state`

## Scope
One durable evidence record only. No runtime change, no ontology change, no external publication, no irreversible external effect, no new queue/worker/retry/idempotency mechanism.

## Expected evidence

1. The work item exists as a GitHub Issue.
2. The implementation exists on a dedicated branch.
3. The branch is represented by a Pull Request.
4. The Pull Request runs repository CI.
5. The resulting repository state is reconstructable from GitHub history.
6. The experiment can identify which repository-centric controls were supplied by GitHub rather than by Content Factory code.

## Observed lifecycle

- The bounded work item was represented by the experiment Issue.
- A dedicated branch `experiment/002-github-native-control` carried the implementation.
- PR #12 represented that branch and proposed only the bounded evidence-record change.
- The PR-triggered Actions run `34751548950` completed successfully; the `pytest` job passed.
- The PR was merged with squash as commit `b3bc93998fb8f441c8eef62ce57fd1f7ab83beee`.
- The resulting repository state and change history are reconstructable from the Issue/PR/commit/Actions chain.

## Control observations

GitHub supplied the repository-centric mechanisms for:

- work intake via Issue;
- work isolation and implementation identity via branch;
- change container and implementation linkage via Pull Request;
- automated verification execution via Actions;
- review boundary as a distinct PR mechanism;
- merge/repository-state transition;
- durable repository audit trail through PR and Git history.

The review boundary was observable, but independent approval was not available under the current GitHub identity. A review/comment therefore must not be interpreted as independent acceptance. The experiment does not establish that an independent-review ruleset is currently enforced; that configuration remains an explicit repository-level unknown.

## Result

The tested path is locally applicable as a repository-centric control path. For this bounded work item, adding a separate Content Factory mechanism for intake, branch/change linkage, CI verification, merge transition, or repository audit would duplicate controls already supplied by GitHub.

This is a local applicability result, not a general proof that GitHub improves factory outcomes.

The result supports delegation/reduction analysis for repository-centric controls. It does not authorize deleting existing architecture until the reduction matrix is recorded and accepted under EXPERIMENT-003.

## Non-goals / non-claims

This experiment does not establish:

- semantic correctness;
- evidence interpretation;
- knowledge promotion;
- external-effect semantics;
- idempotency or reconciliation;
- causal attribution;
- business outcomes;
- learning effectiveness;
- general superiority of GitHub over a bespoke mechanism.

## Next decision

Use the existing canonical EXPERIMENT-003 Issue to produce a reduction matrix: Content Factory function → GitHub-native mechanism → FULL / PARTIAL / NONE → local evidence → remaining own mechanism → candidate for delegation/deletion. Do not delete architecture before that matrix is reviewed and accepted.
