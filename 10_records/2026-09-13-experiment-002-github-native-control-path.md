# EXPERIMENT-002 — GitHub-Native Control Path

Date: 2026-09-13
Status: `EXECUTION / BOUNDED`

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

## Control requirements being tested

- work intake;
- work identity;
- implementation linkage;
- review boundary;
- verification boundary;
- acceptance/merge boundary;
- repository evidence/audit trail.

## Non-goals

GitHub capability is not evidence that GitHub improves factory outcomes. This experiment only tests local applicability of the repository-centric control path.

The following remain outside this experiment: semantic correctness, evidence interpretation, knowledge promotion, external-effect semantics, idempotency, reconciliation, causal attribution, and business outcomes.

## Result placeholder

Result is intentionally completed only after the PR/CI/merge lifecycle has been observed. No claim of success is made by the existence of this record alone.
