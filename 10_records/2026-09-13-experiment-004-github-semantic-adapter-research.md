# Experiment-004 — GitHub semantic adapter research and execution record

Status: `IN PROGRESS`

## Research question

What is the smallest useful integration boundary between Content Factory semantic operations and GitHub-native repository/control mechanisms, and which GitHub mechanisms should be used at that boundary?

## Current repository model

The governing protocol requires repository inspection before structural changes and requires external research for unresolved technology-selection questions. Research must be reconciled with the repository model rather than promoted directly to truth.

The current capability/engineering model already separates factory semantics from tools/providers and explicitly identifies APIs, webhooks, governance, observability and infrastructure as engineering concerns. Repository synchronization is an explicit boundary: runtime evidence → workspace evidence → repository sync → Git history.

## External sources consulted

1. GitHub Docs — GitHub Apps: https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps
2. GitHub Docs — Choosing GitHub App permissions: https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app
3. GitHub Docs — Webhooks: https://docs.github.com/en/webhooks/about-webhooks
4. GitHub Docs — REST API: https://docs.github.com/en/rest
5. GitHub Docs — GraphQL API: https://docs.github.com/en/graphql
6. GitHub Docs — Actions: https://docs.github.com/en/actions
7. GitHub Docs — Environments: https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment
8. GitHub Docs — Artifact attestations: https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations

## Findings and reconciliation

### SUPPORTS_CURRENT_MODEL

GitHub repository state, pull requests, checks, Actions, environments and repository history are appropriate infrastructure mechanisms for repository-facing change control, deterministic automation and technical gates.

This supports the existing separation between Factory semantics and engineering/integration mechanisms.

### EXTENDS_CURRENT_MODEL

A persistent integration boundary can be implemented as an adapter that translates Factory-level operations into GitHub primitives and normalizes GitHub observations back into Factory evidence.

REST is suitable for explicit GitHub operations. GraphQL is useful for complex read projections but is not required for the first bounded proof. Webhooks and GitHub Apps are appropriate for persistent/event-driven integration but are not required to prove the basic adapter boundary.

### REVEALS_GAP

The repository did not previously contain an explicit, minimal representation of the mapping between a Factory work identity and GitHub repository/change identity, nor a normalized interpretation of GitHub change evidence.

### NOT_APPLICABLE / DEFERRED

GitHub Projects, GraphQL, GitHub Apps and webhooks are not introduced by this experiment. No concrete problem in the bounded proof requires them yet.

## Experiment boundary

Prove only:

```text
Factory work identity
    ↓
GitHub Issue + Branch + Pull Request
    ↓
GitHub Actions / checks
    ↓
GitHub change evidence
    ↓
Factory-side normalized verification evidence
```

Do not prove or imply:

```text
GitHub state = Factory state
GitHub CI = semantic acceptance
PR merge = publication authority
repository history = external outcome
```

## Implementation decision

Implement the smallest typed adapter boundary in `src/content_factory/github_adapter.py`.

The adapter provides:

- explicit binding of Factory `work_item_id` to GitHub issue/branch/repository identity;
- normalized GitHub change evidence;
- Factory-side verification result with evidence references and explicit unknowns;
- no acceptance or publication authority grant.

The corresponding tests verify the boundary without requiring live GitHub credentials or network calls from application code.

## Live GitHub proof target

The same experiment is executed through the repository itself using Issue #27 and branch `experiment/004-github-semantic-adapter`, followed by a pull request and repository CI. The live result must be recorded separately from the adapter's unit tests.

## Remaining unknowns

- whether interactive connector operations are sufficient for sustained operation;
- whether event-driven webhooks become necessary once autonomous execution exists;
- whether a GitHub App is required for durable non-user-bound integration;
- whether GraphQL materially reduces integration complexity for actual Factory projections;
- whether GitHub Projects solve a demonstrated Factory Control problem.

## Decision status

`SUPPORTED / EXTENDED / GAP IDENTIFIED — bounded implementation authorized`
