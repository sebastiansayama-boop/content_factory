# EXPERIMENT-003 — Acceptance Decision

Date: 2026-09-13
Status: `ACCEPTED`
Canonical work item: GitHub Issue #22
Related PR: #26

## Decision

ACCEPT.

Experiment-003 establishes the repository-level reduction boundary for GitHub-native control mechanisms in the Content Factory.

The accepted model is:

`Factory semantic control → GitHub-native repository mechanism → repository evidence/history`

The experiment does **not** authorize deletion of the semantic/runtime factory layer.

## Accepted delegation boundaries

GitHub-native mechanisms are accepted as the preferred substrate for repository-facing:

- work intake and repository work identity;
- branch/change isolation;
- pull-request lifecycle and review routing;
- repository CI execution;
- repository merge/state transition;
- repository activity/audit history;
- repository workflow secrets and infrastructure gates where applicable.

Where GitHub provides only representation or infrastructure primitives, the Content Factory retains the corresponding domain semantics.

## Retained factory boundaries

The Content Factory remains authoritative for:

- semantic WorkItem meaning and admission;
- runtime state transitions and execution lifecycle;
- durable runtime state, recovery, idempotency and reconciliation;
- capability contracts and provider abstraction;
- execution identity and semantic result binding;
- semantic verification;
- acceptance meaning and authority;
- publication/external-effect semantics;
- semantic provenance and cross-system evidence interpretation;
- business outcome and learning semantics.

## Bridge boundary

The accepted integration direction is:

`Factory semantics ↔ explicit adapter/integration boundary ↔ GitHub-native mechanism`

Repository state must not silently become runtime state, and GitHub checks/reviews/merges must not silently become semantic acceptance or publication authority.

## Evidence

Experiment-002 locally demonstrated the bounded repository lifecycle:

`Issue → branch → PR → CI → merge → repository state`.

Experiment-003 then mapped the candidate reduction against the actual implementation inventory. The repository contains an executable factory runtime, durable runtime state/event journaling, capability/provider boundaries, verification/acceptance/publication semantics, and explicit runtime-to-repository evidence synchronization.

The implementation mapping found no exact duplicate classes named `FactoryIssue`, `FactoryBranch`, `FactoryReview`, or `FactoryCI`. This is limited negative evidence and is not treated as proof that no semantic equivalent exists under another name.

## Explicit non-decisions

This acceptance does not:

- delete existing architecture;
- claim GitHub replaces the Content Factory control plane;
- claim external publication or business outcomes are solved;
- establish durable runtime recovery through GitHub;
- establish independent reviewer availability or current repository ruleset configuration;
- establish that the accepted mechanisms are universally superior outside this repository.

## Consequence

Future repository-facing implementation should prefer GitHub-native primitives over parallel custom bookkeeping when the function is within the accepted delegation boundary.

Any architectural deletion or substantive delegation must be a separate scoped change with its own verification.

The next legitimate experiment may test a semantic GitHub interaction layer that exposes higher-level operations over these primitives, without changing the factory's semantic authority boundaries.
