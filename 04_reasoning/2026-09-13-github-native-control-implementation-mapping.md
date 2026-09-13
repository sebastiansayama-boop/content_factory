# EXPERIMENT-003 — Implementation-Level Mapping

Date: 2026-09-13
Status: `IMPLEMENTATION MAPPING / REVIEW REQUIRED`
Canonical work item: GitHub Issue #22
Related matrix: `04_reasoning/2026-09-13-github-native-control-reduction-matrix.md`

## Purpose

Check the reduction matrix against the actual implementation inventory before any delegation or deletion decision.

This record does not authorize architecture deletion. It records what is currently implemented, what is already delegated to GitHub, and where the matrix must preserve a Content Factory-owned semantic/runtime boundary.

## Inventory inspected

The repository contains an executable Python package under `src/content_factory/` and GitHub Actions workflows under `.github/workflows/`.

The relevant runtime implementation files inspected are:

- `src/content_factory/runtime.py`
- `src/content_factory/runtime_store.py`
- `src/content_factory/artifacts.py`
- `src/content_factory/integrations.py`
- `src/content_factory/openai_adapter.py`
- `src/content_factory/openai_capability.py`
- `src/content_factory/__main__.py`
- `.github/workflows/test.yml`
- `.github/workflows/materialize-runtime.yml`
- `pyproject.toml`

The implementation inventory therefore changes the confidence level of the matrix: the repository does contain a real factory runtime and semantic control model. The reduction target is not an empty planning abstraction.

## Direct mapping

| Existing implementation | Function represented | GitHub replacement status | Decision |
|---|---|---|---|
| `WorkItem` in `runtime.py` | semantic work-item identity/objective/outcome/inputs/capabilities/acceptance/release constraints | PARTIAL | Keep domain WorkItem; GitHub Issue may represent the repository-facing work item |
| `FactoryState` + `_allowed` transitions | runtime state machine | NONE | Keep; GitHub Issue/PR state cannot replace runtime transitions |
| `FactoryRuntime.submit()` | runtime admission/start of a work item | PARTIAL | GitHub can provide repository work intake; runtime admission remains factory-owned |
| `FactoryRuntime.run()` | capability execution and semantic orchestration | NONE | Keep; Actions may execute bounded repository automation but cannot replace factory semantics |
| `Capability` registry | capability contract/provider boundary | NONE | Keep |
| `ExecutionResult` | execution identity/output revision/evidence linkage | NONE | Keep |
| `VerificationResult` | semantic verification result | PARTIAL | GitHub Actions can execute repository checks; result binding and content semantics remain factory-owned |
| `AcceptanceDecision` | semantic acceptance + authority | PARTIAL | PR review/checks can provide infrastructure gates; acceptance meaning and authority remain factory-owned |
| `PublicationResult` / `Publisher` | external publication/effect | PARTIAL mechanically, NONE semantically | Keep external-effect boundary and publication identity |
| `RuntimeStore` | durable runtime state + event journal + recovery | NONE | Keep; GitHub history is not a runtime recovery store |
| `ArtifactStore` | runtime evidence projection into repository workspace | PARTIAL | Keep explicit evidence projection; Git history can supply repository audit trail after sync |
| `.github/workflows/test.yml` | repository CI verification | FULL for repository checks | Delegate to GitHub Actions |
| `.github/workflows/materialize-runtime.yml` | explicit runtime-to-repository evidence synchronization | PARTIAL | Keep the explicit synchronization boundary; GitHub Actions is the execution substrate |
| GitHub Issues / PRs / commits | repository work/change lifecycle | FULL for repository-facing lifecycle | Prefer native GitHub mechanisms over parallel repository-only equivalents |

## Evidence for the boundary

`FactoryRuntime` explicitly models `RECEIVED → ADMITTED → PRODUCED → VERIFIED → ACCEPTED → RELEASE_READY → RELEASED → DELIVERED → OBSERVED`, with failure transitions. It also binds verification and acceptance to the exact output revision and requires explicit release authority. These are domain/runtime semantics, not repository bookkeeping.

`RuntimeStore` persists work-item state and an append-only event journal in SQLite transactions. Its documentation explicitly separates recovery state from repository evidence projection. This is a direct implementation-level reason not to replace runtime state with GitHub history.

`ArtifactStore` is deliberately a filesystem evidence sink. It materializes execution, verification, acceptance, publication, observation, and runtime-case records. Repository synchronization is intentionally outside the runtime.

The repository test workflow installs the package and runs `pytest`, making GitHub Actions the natural execution substrate for repository-level automated verification. The materialization workflow explicitly runs the deterministic factory experiment and then checks and commits only the permitted evidence zones.

## Reduction decisions supported by implementation evidence

1. Do not introduce a parallel custom repository Issue/PR/CI/merge bookkeeping layer merely to represent GitHub-native repository events.
2. Keep `WorkItem` because it contains semantic fields that GitHub Issue metadata does not establish by itself.
3. Keep `FactoryState` and runtime transitions because repository issue/PR states do not represent execution lifecycle or recovery semantics.
4. Keep `RuntimeStore` because durable execution state and event journaling are operational state, not Git history.
5. Keep `Capability` and provider abstractions because GitHub Actions is an execution substrate, not the factory capability ontology.
6. Keep verification/acceptance/publication semantics while allowing GitHub checks, reviews, rulesets, and environments to serve as infrastructure mechanisms at their applicable boundaries.
7. Keep explicit runtime-to-repository evidence synchronization; GitHub can own the repository transition and audit trail after the evidence is projected.
8. Treat GitHub Issues as a candidate repository-facing representation of work intake, not as a replacement for semantic admission.

## Negative findings and limits

Code-search queries for `FactoryIssue`, `FactoryBranch`, `FactoryReview`, and `FactoryCI` returned no matches in the connected repository search. This is useful negative evidence against those exact duplicate class names, but it is not an exhaustive proof that no semantically equivalent implementation exists under another name.

The implementation inventory has not yet established the active repository ruleset/branch-protection configuration, actual Projects configuration, or independent reviewer availability. Those remain repository-configuration questions rather than source-code questions.

## Revised Experiment-003 decision

The implementation mapping supports **delegation of repository mechanics without deletion of the semantic/runtime factory layer**.

The most credible immediate reduction is therefore not “remove the control plane.” It is:

`Factory semantic control → GitHub-native repository mechanism → repository evidence/history`

while retaining:

`Factory runtime state → capability execution → verification semantics → acceptance authority → external-effect/reconciliation semantics`.

No production architecture is deleted by this experiment.

## Acceptance criterion

Experiment-003 can be considered technically complete when the reduction matrix and this implementation mapping are reviewed together and the repository records an explicit decision on the candidate delegation boundaries. Any actual deletion should be a separate scoped change with its own verification.
