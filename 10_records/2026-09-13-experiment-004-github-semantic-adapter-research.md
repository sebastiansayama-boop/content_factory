# Experiment-004 — GitHub semantic adapter research and execution record

Status: `COMPLETED / BOUNDED PROOF`

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

## Implementation

Implemented `src/content_factory/github_adapter.py` with a small typed boundary:

- `GitHubWorkContext` binds Factory `work_item_id` to GitHub issue, branch and repository identity;
- `GitHubChangeEvidence` represents normalized repository observations;
- `FactoryChangeVerification` separates verification evidence from semantic acceptance and preserves unknowns;
- `verify_github_change()` rejects failed CI and closed-unmerged changes while never granting acceptance authority.

Tests were added in `tests/test_github_adapter.py` covering identity binding, passing CI, failed CI, missing review evidence and closed-unmerged changes.

## Live GitHub proof

Issue: #27.

Initial PR #28 was closed because its first Actions run evaluated an earlier merge revision before the narrow acceptance-boundary fix. No production merge occurred.

Replacement PR: #29.

Head revision: `21a79fc2a5ecf06dd53b537e320995dadc532b60`.

GitHub Actions check: `pytest`, check run `103713827095`, workflow run `34753482893`.

Observed result: `COMPLETED / SUCCESS` on the exact head revision. The run executed the repository's existing `.github/workflows/test.yml` and passed the full test suite after the adapter fix.

Review observation: no independent human review was observed. The PR discussion contains a Codex connector comment reporting that its code-review usage limit had been reached; this is not an approval and is therefore not treated as one.

Factory interpretation:

```text
GitHub change mechanics: VERIFIED
CI evidence: VERIFIED
Independent review: UNKNOWN / NOT OBSERVED
Semantic acceptance: NOT GRANTED BY GITHUB EVIDENCE
Publication authority: NOT GRANTED
External outcome: NOT CLAIMED
```

## What the experiment proves

The repository can support an explicit adapter boundary in which GitHub-native mechanics become normalized Factory evidence without becoming Factory semantic authority.

The proven path is:

```text
Factory identity
→ GitHub issue/branch/PR
→ Actions verification
→ exact head revision
→ normalized Factory verification evidence
```

## What remains unproven

- whether interactive connector operations are sufficient for sustained operation;
- whether event-driven webhooks become necessary once autonomous execution exists;
- whether a GitHub App is required for durable non-user-bound integration;
- whether GraphQL materially reduces integration complexity for actual Factory projections;
- whether GitHub Projects solve a demonstrated Factory Control problem;
- independent-review availability in the current repository configuration;
- autonomous Factory ↔ GitHub reconciliation;
- external publication or business outcome.

## Decision

`ACCEPTED AS A BOUNDED INTEGRATION PROOF WITH EXPLICIT LIMITATIONS`

The experiment does not justify replacing Factory runtime state, semantic acceptance, authority, publication semantics, or external outcome tracking with GitHub state.

The implementation should remain the smallest adapter boundary until a demonstrated operational problem justifies additional mechanisms such as webhooks, a GitHub App, GraphQL or Projects.
