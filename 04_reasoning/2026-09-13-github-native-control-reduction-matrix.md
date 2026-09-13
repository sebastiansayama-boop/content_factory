# EXPERIMENT-003 — GitHub-Native Control Reduction Matrix

Date: 2026-09-13
Status: `CANDIDATE MATRIX / ACCEPTANCE REQUIRED`
Canonical work item: GitHub Issue #22

## Purpose

Determine which repository-centric Content Factory control functions should be delegated to GitHub-native mechanisms, which are only partially covered, and which remain proprietary factory mechanisms.

This matrix is a reduction decision aid. It is not authorization to delete architecture. Deletion or delegation becomes valid only after the matrix is reviewed and accepted against current repository behavior and the relevant external mechanism documentation.

## Evidence basis

Local evidence: EXPERIMENT-002 demonstrated the bounded path `Issue → branch → PR → CI → merge → repository state` in this repository. PR #12 merged as `b3bc93998fb8f441c8eef62ce57fd1f7ab83beee`; the PR-triggered Actions run `34751548950` completed successfully.

Repository architecture basis: `docs/23_content_factory_operating_model.md`, `docs/24_capability_and_engineering_layer.md`, `docs/25_chat_repository_operating_protocol.md`, and `docs/28_project_operating_memory.md`.

External mechanism basis: GitHub Issues/Projects provide planning and tracking primitives; Pull Requests provide proposal/review/merge workflow; Actions provide repository automation; rulesets/protected branches can enforce merge conditions; environments can gate jobs with approvals and branch restrictions.

Official documentation consulted:
- https://docs.github.com/en/issues
- https://docs.github.com/en/pull-requests
- https://docs.github.com/en/pull-requests/reference/managing-and-standardizing-pull-requests
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments
- https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/automating-projects-using-actions

External documentation establishes GitHub capability, not Content Factory effectiveness. Local applicability is established only where this repository has observed the mechanism.

## Classification

`FULL` = the GitHub-native mechanism can replace the repository-centric control function for the bounded repository case without preserving a parallel factory mechanism.

`PARTIAL` = GitHub supplies useful control primitives, but the factory retains domain-specific semantics or cross-system behavior.

`NONE` = the function is outside GitHub's repository-centric responsibility and remains a Content Factory / engineering mechanism.

## Matrix

| Content Factory function | GitHub-native mechanism | Coverage | Local evidence / basis | What remains proprietary | Candidate action |
|---|---|---|---|---|---|
| Work intake | Issues / issue forms | FULL for repository work intake | EXP-002 observed Issue as bounded work item | Strategic demand semantics, admission criteria beyond repository tasking | Delegate repository task intake to GitHub Issues |
| Work identity | Issue + branch + PR + commit identity | FULL for repository change work | EXP-002 lifecycle reconstructable | Cross-system operation identity | Remove duplicate repository-only work identity if one exists |
| Decomposition | Sub-issues / tasklists / Projects | PARTIAL | GitHub provides hierarchical task tracking | Factory-specific semantic decomposition and capability graph | Use GitHub for work decomposition; retain domain semantics |
| Priority | Projects fields / views / issue metadata | PARTIAL | GitHub supports structured planning metadata | Strategic priority model and portfolio decision rules | Delegate repository prioritization representation |
| Status tracking | Projects status fields / PR state | FULL for repository work state representation | GitHub provides issue/PR state and project fields | Domain execution states such as running/unknown/recovery_required | Delegate repository-facing status; retain runtime state machine |
| Dependencies | Issue/PR dependency mechanisms | PARTIAL | GitHub supports work dependencies | Semantic/data/provider dependencies and execution dependency semantics | Delegate task dependencies; retain domain dependencies |
| Scheduling | Projects date/iteration fields | PARTIAL | GitHub provides planning/scheduling primitives | Runtime scheduler, timing guarantees, external deadlines with semantics | Do not build repository scheduler; retain execution scheduling only where needed |
| Ownership | Assignees / CODEOWNERS / requested reviewers | PARTIAL | GitHub routes repository responsibility/review | Capability ownership, service expectations, authority model | Delegate repository ownership routing |
| Review routing | CODEOWNERS / requested reviewers | FULL for repository review routing | GitHub PR mechanism observed; independent approval not locally available under current identity | Domain review policy and authority semantics | Delegate repository review routing |
| Review gate | PR reviews + rulesets | PARTIAL | PR review boundary exists; current repo did not establish enforced independent approval | Required independence, semantic acceptance, domain authority | Use GitHub as mechanism; verify/configure required rules separately |
| CI verification | GitHub Actions | FULL for repository-executable checks | EXP-002 Actions run passed pytest | Semantic/content verification and external-effect verification | Delegate repository CI execution |
| Merge / repository acceptance transition | PR merge + rulesets | FULL for repository state transition; PARTIAL for semantic acceptance | EXP-002 squash merge observed | Content acceptance, publication authorization | Remove bespoke repository merge-control duplicate |
| Repository audit trail | Git history + PR/Issue/Actions records | FULL for repository activity history | EXP-002 lifecycle reconstructable | Cross-system causal/provenance record | Delegate repository audit trail |
| Evidence transport into repository | Actions artifacts / commits / repository files | PARTIAL | Existing materialization workflow and EXP-002 commits provide repository evidence path | Evidence interpretation, external observation truth, provenance semantics | Keep explicit evidence projection; do not duplicate Git history as semantic evidence |
| Project bookkeeping / automation | Projects + Actions | PARTIAL | GitHub documents project automation | Factory-specific state transitions and semantics | Prefer native automation before custom bookkeeping |
| WIP visibility | Projects views / fields | PARTIAL | Native planning views can represent work | Runtime WIP limits, admission control, queue semantics | Delegate visibility; retain control semantics only if runtime requires them |
| Queue management | Projects + Actions | PARTIAL at representation level | GitHub can represent pending work and trigger workflows | Durable queue, worker ownership, lease, ordering, retry, recovery | Do not build queue solely for repository bookkeeping; retain runtime queue if required |
| Capacity management | Projects metadata | NONE for actual execution capacity | Planning metadata does not establish provider/worker capacity | Capacity model, reservation, resource accounting | Keep own mechanism only when real execution requires it |
| Bottleneck management | Projects visibility + Actions | PARTIAL | Native views/automation expose work state | Bottleneck identification model, constraint policy, intervention logic | Keep domain bottleneck analysis |
| Workflow orchestration | Actions workflows | PARTIAL | Actions can orchestrate repository automation | Capability routing, semantic transitions, long-running/external orchestration | Use Actions for repository automation; retain factory orchestration boundary |
| Secrets storage | GitHub repository/environment secrets | FULL for repository workflow secret storage | Supported GitHub mechanism | Secret selection policy and external provider authorization | Delegate storage; never copy secrets into repository evidence |
| Deployment/release gating | Environments + rulesets | PARTIAL | GitHub supports approvals, branch restrictions and protection rules | Domain release semantics, external-effect authority, outcome verification | Use GitHub as infrastructure gate; retain domain release decision |
| Runtime state / recovery | GitHub workflow state | NONE | No experiment established durable factory execution recovery | pending/running/completed/failed/unknown/recovery_required semantics | Keep own runtime state/recovery mechanism |
| Idempotency / reconciliation | GitHub Actions primitives | NONE | Not tested by EXP-002 and not supplied by repository history | Operation identity, idempotency keys, external reconciliation | Keep own mechanism |
| Provider/capability abstraction | Actions/providers | NONE | GitHub is an execution platform, not the semantic capability model | Capability contracts, adapters, provider substitution | Keep own capability layer |
| Semantic provenance | Git commits/PRs | PARTIAL | GitHub records repository change ancestry | Claim/evidence provenance, source lineage, cross-system provenance | Keep semantic provenance model |
| Identity/revision semantics | Git object identity + PR | PARTIAL | GitHub gives strong repository revision identity | Content entity/revision semantics and authority | Keep domain identity/revision model |
| Verification → acceptance semantics | PR checks/reviews | PARTIAL | GitHub separates checks and reviews | Domain acceptance meaning and exact content revision acceptance | Keep acceptance boundary; use GitHub as enforcement substrate where applicable |
| Acceptance → publication authorization | Rulesets/environments | PARTIAL | GitHub can gate repository/deployment actions | Content publication authority and external authorization | Keep domain authority; use GitHub gates as infrastructure control |
| External publication/effect | Actions/deployments | PARTIAL mechanically, NONE semantically | GitHub can execute workflows, but EXP-002 had no external effect | External destination semantics, idempotency, observation and attribution | Keep own external-effect boundary |
| Outcome measurement / attribution | Projects/Actions only as transport | NONE | No external outcome tested | Outcome model, causal attribution, learning evaluation | Keep own mechanism |
| Learning / knowledge promotion | Issues/Projects/Actions | NONE | Not tested; repository operating memory has explicit semantic learning transitions | Knowledge validity, applicability, promotion, contradiction handling | Keep own learning model |
| Ontology / semantic model | GitHub metadata | NONE | GitHub metadata cannot define factory domain meaning | Factory ontology and semantic substrate | Keep own ontology |

## Reduction conclusion

The repository-centric control plane should not reimplement GitHub's native mechanisms where the required function is specifically repository work management and repository change control.

The strongest delegation candidates are:

1. repository work intake;
2. repository work identity and change linkage;
3. repository review routing;
4. repository CI execution;
5. repository merge/state transition;
6. repository audit history;
7. repository planning/status representation;
8. repository secret storage;
9. repository/deployment infrastructure gates where applicable.

The strongest mechanisms that remain Content Factory-owned are:

1. semantic work-item meaning and admission policy;
2. capability contracts and provider abstraction;
3. runtime execution state, recovery and idempotency;
4. semantic provenance and evidence interpretation;
5. acceptance meaning and authority semantics;
6. external-effect semantics and reconciliation;
7. outcome measurement and causal attribution;
8. learning and knowledge promotion;
9. ontology and shared semantic substrate.

## Critical boundary

`GitHub merge != semantic acceptance`.

`GitHub review != independent acceptance unless repository policy actually requires and enforces the relevant reviewer conditions`.

`GitHub Actions success != external outcome`.

`Git history != semantic provenance`.

`GitHub Issue != complete factory work-item ontology`.

These distinctions prevent the reduction effort from replacing domain semantics with repository mechanics.

## Current unknowns

- The exact active branch-protection/ruleset configuration for this repository has not been established through the available inspection path.
- Independent reviewer availability/enforcement under the current repository identity is not established.
- Whether Projects is configured and actually used for this repository's planning flow has not been established.
- Whether any existing Content Factory code duplicates the identified GitHub-native functions beyond the documented model has not yet been exhaustively mapped at implementation level.

## Decision status

`CANDIDATE / REVIEW REQUIRED`

No architecture is deleted by this record.

Acceptance should be recorded only after checking the matrix against the actual implementation inventory and confirming which duplicate mechanisms, if any, exist. The next legitimate step is implementation-level mapping of candidate reductions, followed by a scoped decision on delegation/deletion.
