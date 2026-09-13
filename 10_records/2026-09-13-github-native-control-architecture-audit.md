# GitHub-Native Control Architecture Audit

Date: 2026-09-13
Status: `RESEARCH / CANDIDATE CONTROL BOUNDARY`

## Question

Which parts of the Content Factory control architecture should not be implemented as bespoke factory mechanisms because GitHub already provides a native, inspectable and enforceable mechanism?

## Epistemic boundary

GitHub documentation establishes available platform mechanisms. It does not prove that using those mechanisms will improve Content Factory outcomes. Local applicability remains a design/experiment question.

## Current repository evidence

The current factory model defines a control plane containing prioritization, intake, routing, WIP, queues, capacity, scheduling, ownership, service expectations, orchestration and bottleneck management. It also defines semantic, capability and engineering layers.

The repository already uses GitHub Actions for pytest CI and a manually dispatched workflow that executes a deterministic runtime experiment, checks repository write scope, and commits permitted evidence changes. The latter demonstrates that GitHub can already act as an explicit repository synchronization boundary.

## Matrix

| Current factory function | GitHub-native mechanism | Coverage | What should remain custom |
|---|---|---|---|
| Work intake | Issues, issue forms, issue types, labels, milestones | HIGH / partial | Domain-specific admission criteria and semantic validation |
| Work decomposition | Sub-issues, issue dependencies | HIGH | Domain-specific dependency semantics where GitHub relations are insufficient |
| Priority / status / planning | Projects, custom fields, views, iterations, milestones | HIGH | Factory-specific optimization logic and capacity model |
| Ownership | Issue/PR assignees, reviewers, CODEOWNERS | HIGH | Capability ownership and authority semantics outside repository changes |
| Work ↔ implementation linkage | Issue ↔ branch ↔ PR ↔ commit | HIGH | Factory-level work-item identity if it spans non-GitHub systems |
| Change review | Pull requests, reviews, review threads, CODEOWNERS | HIGH | Content/knowledge acceptance criteria that cannot be reduced to code review |
| Verification gate | Actions checks + PR required status checks | HIGH | Domain verification semantics and evidence interpretation |
| Merge authorization | Rulesets / branch protection / required reviews | HIGH | Business/release authority beyond repository merge |
| Workflow execution | GitHub Actions | HIGH for repository/CI automation | Long-running domain execution, external orchestration and provider-specific execution where Actions is not the right runtime |
| Manual approval before consequential action | Environments + required reviewers / protection rules | HIGH | Domain authorization model and risk classification |
| Secrets boundary | Actions secrets / environment secrets | HIGH | Secret semantics and external provider credential lifecycle beyond GitHub |
| Artifact/evidence retention | Actions artifacts + repository commits/releases | HIGH / partial | Evidence ontology, provenance interpretation, external-world observations |
| Repository state transition | Git commits, PR merge, tags/releases | HIGH | Semantic state transitions that are not repository state |
| External deployment/release gate | Environments, deployments, concurrency, protection rules | HIGH / partial | External-effect semantics, reconciliation, idempotency and outcome attribution |
| Audit trail of repository changes | Git history, PR timeline, workflow runs | HIGH | Cross-system causal/provenance chain |
| Automation of project bookkeeping | Projects workflows + Actions/API | HIGH | Factory-specific decision logic |
| Bottleneck visibility | Projects views/fields + Actions-derived metadata | PARTIAL | Factory queueing theory, WIP policy, capacity estimation and bottleneck decisions |
| Scheduling | Project iterations/date fields + Actions | PARTIAL | Factory scheduling semantics and resource constraints |
| Queues / workers / leases | Actions jobs/concurrency | PARTIAL | Durable domain queue semantics, lease/recovery guarantees and provider operation recovery |
| External operation identity | Workflow run/job IDs + external provider IDs | PARTIAL | Canonical cross-system operation identity and provider semantics |
| Idempotency / safe recovery | Actions concurrency can prevent overlapping workflows | PARTIAL | Provider-specific duplicate safety, reconciliation and recovery policy |
| Knowledge/provenance model | Git history, PR links, artifacts, issue references | PARTIAL | Semantic provenance, evidence quality, applicability, contradiction and knowledge validity |
| Learning loop | Issues/Projects/Actions can record and automate work | PARTIAL | Interpretation, knowledge promotion, applicability, causal evaluation and revision |
| External outcome observation | Actions can call external systems and collect outputs | PARTIAL | Observation semantics, attribution, uncertainty and external-world evidence |
| Business/product outcome | Issues/Projects can record experiments and outcomes | LOW | Measurement, causal inference and ecosystem/product learning |
| Factory ontology | GitHub metadata is not an ontology | NONE | Entire semantic domain model remains custom |
| Capability abstraction | GitHub can track capability work but does not define capability contracts | NONE | Capability contracts, provider abstraction, executor semantics |
| Content quality semantics | PR/checks can gate changes | PARTIAL | Editorial quality, claims, factuality, audience fit and acceptance semantics |

## Preliminary architectural conclusion

The largest likely duplication is not in the semantic model or capability layer. It is in repository-centric control mechanisms that the factory currently describes abstractly:

- intake and work tracking;
- decomposition and dependency tracking;
- status/priority/ownership;
- change review;
- repository verification gates;
- merge/release authorization;
- workflow execution;
- repository evidence materialization;
- repository audit trail;
- project bookkeeping.

These should be treated as candidates for delegation to GitHub rather than immediately reimplemented inside Content Factory.

## Important boundary

GitHub does not replace the factory's semantic or epistemic control. In particular, GitHub cannot by itself establish:

- that a claim is true;
- that evidence is sufficient;
- that a result is causally attributable to a knowledge item;
- that knowledge is applicable in a new context;
- that an external provider operation is duplicate-safe;
- that an external effect achieved the intended business outcome;
- that a content revision is editorially acceptable merely because CI passed.

Therefore the intended boundary is:

```text
GITHUB-NATIVE CONTROL
    work tracking
    change control
    review
    CI / execution
    repository authorization
    secrets / environments
    evidence transport
    repository audit trail
            ↓
CONTENT FACTORY DOMAIN CONTROL
    meaning
    capability contracts
    evidence interpretation
    acceptance semantics
    external-effect semantics
    provenance across systems
    learning / knowledge revision
    outcome attribution
```

## Design hypothesis

Before adding a new repository-centric control primitive, first ask whether GitHub Issues, Projects, PRs, Actions, rulesets, environments, artifacts, releases, CODEOWNERS or API automation already provide the required control boundary.

Adoption still requires an applicability decision and, where consequential, an experiment.

## Next empirical question

Can the existing Content Factory work-item/control-plane model be reduced by moving repository-centric work management into GitHub Issues + Projects + PRs + Actions + rulesets/environments without losing required evidence, authority, provenance or semantic control?
