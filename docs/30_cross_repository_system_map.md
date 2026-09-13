# 30 — Cross-Repository System Map

Status: `CURRENT WORKING MODEL`
As of: 2026-09-13

This document reconciles the active repository set into one system map. It does not promote historical repository structure into current architecture. Repository boundaries are implementation boundaries unless an explicit semantic/runtime relationship is evidenced.

## 1. Current system boundary

The current working system is best represented as:

```text
CONTENT FACTORY
  system purpose / value flows / control / semantic model
        |
        v
ATLAS AGENT
  reasoning / orchestration / user-facing control
        |
        v
CONTROLLED AGENT EXECUTOR
  bounded execution / authority enforcement / durable execution evidence
        |
        v
CAPABILITIES / PRODUCTS
  Whisper Studio and future capability implementations
        |
        v
EXTERNAL EFFECTS
        |
        v
OBSERVATION / MEASUREMENT / LEARNING
        |
        +---------------------> Content Factory
```

This is a system hypothesis. The repository evidence proves the component capabilities and documented boundaries, but does not yet prove the complete runtime integration of these repositories into one deployed system.

## 2. Repository disposition

| Repository | Current role | Evidence status | System placement |
|---|---|---|---|
| `content_factory` | operating model and bounded executable factory slice | active | system / L0-L4 |
| `-atlas-agent` | interactive Atlas controller and reasoning/orchestration | active | orchestration |
| `controlled-agent-executor` | controlled foreground execution engine | stable/frozen | execution substrate |
| `whisper-studio` | local-first media production capability | active prototype | production capability |
| `ai-research-radar` | bounded local research-intake experiment | paused | candidate intelligence capability |
| `atlas-records` | historical contracts/results/decisions | read-only | evidence/history |
| `atlas-workspace` | historical reproducibility proof | retired | evidence/history |
| `ai-creative-os` | archived creative experiments and old workflow snapshots | archived | history |
| `thai-mythology-content-generator` | archived n8n content prototype | archived | history |
| `telegram_bot` | independent rental-bot prototype | parked/independent | outside system |

## 3. Capability → process → object → repository → runtime → effect

### C01 — System sensing / research intake

Process: collect or receive signals, classify, score, review, route.

Object: signal / scored item / review outcome / handoff packet.

Repository: `ai-research-radar`.

Runtime status: bounded local prototype only; no live external research integration, model call, Telegram ingestion, or automatic handoff.

Effect: none proven beyond local review records.

Status: `CANDIDATE / PAUSED`.

### C02 — Demand and work control

Process: qualify demand, create WorkItem, prioritize, route, manage dependencies/WIP/capacity.

Object: Content Work Item / Work Package.

Repository: `content_factory`.

Runtime status: WorkItem and bounded runtime exist; broad Factory Control remains specified but not implemented.

Effect: internal runtime state only.

Status: `PARTIAL`.

### C03 — Reasoning / orchestration

Process: interpret user goal, plan bounded work, select permitted tools, coordinate subordinate read-only analysis, maintain decision ownership.

Object: WorkOrder / ResultEnvelope / task event / human decision.

Repository: `-atlas-agent`.

Runtime status: implemented local agent route with typed contracts, durable task journal, scoped tools, human approval and editorial records.

Effect: repository-local changes and Telegram publication route are bounded; broader external effects are explicitly excluded.

Status: `EXISTS / BOUNDED`.

### C04 — Controlled execution

Process: bind authorized task to exact revision, claim work, apply allowlisted patch, run exact checks, re-observe evidence, stop at human gate, support cancellation/recovery.

Object: task contract / authorization / claim / patch / check evidence / decision.

Repository: `controlled-agent-executor`.

Runtime status: active ATLAS-NATIVE-V1 foreground task route; no autonomous scheduler, deployment, publication, spending or provider selection.

Effect: controlled repository mutation.

Status: `EXISTS / BOUNDED`.

### C05 — Content production

Process: assemble authored media assets, render, subtitle, export, hash and package evidence.

Object: project / scene / shot / asset / candidate / render / export.

Repository: `whisper-studio`.

Runtime status: real local renderer is implemented; brief-to-video generation, automatic publishing and analytics are not active.

Effect: local MP4 and render evidence.

Status: `EXISTS / BOUNDED`.

### C06 — Verification / acceptance / release

Process: verify conformity, separate verification from acceptance, authorize release/publication.

Object: verification result / acceptance decision / release / publication result.

Repository: `content_factory`, with bounded related mechanisms in Atlas/Whisper Studio.

Runtime status: Content Factory has the clearest semantic boundary and a bounded executable verification→acceptance→release path; factory-wide operational release is incomplete.

Effect: publication semantics are not yet independently proven across an external destination.

Status: `PARTIAL`.

### C07 — External publication / distribution

Process: release an accepted revision to an external channel, observe actual external effect, reconcile ambiguous outcomes.

Object: publication / external-effect record / reconciliation record.

Repository: no complete current implementation.

Runtime status: Telegram publication exists in the Atlas repository as a bounded owner-only route, but the broader Content Factory external-effect lifecycle is not proven.

Effect: partially implemented / not system-wide proven.

Status: `PARTIAL`.

### C08 — Measurement / learning

Process: observe external response, interpret outcome, update knowledge/editorial/production decisions.

Object: observation / metric / outcome / learning candidate / decision.

Repository: `content_factory` model; no complete external outcome integration.

Runtime status: observation exists as a bounded concept; system-wide measurement and learning loop are not implemented.

Effect: no proven closed-loop adaptation.

Status: `MISSING / PARTIAL`.

## 4. Cross-repository semantic chain

The strongest current candidate for the shared semantic path is:

```text
Signal / Demand
    -> Intent / WorkItem
    -> Knowledge / Evidence
    -> Brief / Specification
    -> Capability request
    -> Execution
    -> Output Revision
    -> Verification Evidence
    -> Acceptance Decision
    -> Release / Publication
    -> External Effect
    -> Observation
    -> Learning
```

This is a cross-system working model, not a promoted ontology. Existing repository rules require semantic jobs and competency questions before promoting terms into ontology classes.

## 5. Authority boundaries

The repositories show a consistent and useful separation:

```text
reasoning          != execution
execution          != verification
verification       != acceptance
acceptance         != release
release            != publication
publication        != external outcome
observation        != learning truth
learning           != strategy authority
```

`-atlas-agent` owns orchestration and user-facing decisions. `controlled-agent-executor` enforces bounded execution authority. `content_factory` owns the broader semantic and operating model. `whisper-studio` owns the concrete media production capability.

No repository currently has evidence sufficient to claim that these authority boundaries are enforced end-to-end across the entire system.

## 6. Runtime integration status

Proven relationships:

- Atlas documents and implements controlled reasoning/tool orchestration.
- Controlled Agent Executor implements a separate bounded task-execution route.
- Whisper Studio documents Atlas as project command center and Forge as implementation executor, while its current renderer remains independently runnable.
- Historical records preserve evidence for earlier Atlas/Whisper work.

Not yet proven:

- `content_factory -> Atlas` live runtime invocation.
- `Atlas -> controlled-agent-executor` current production integration.
- `controlled-agent-executor -> Whisper Studio` live capability invocation.
- `Radar -> Content Factory/Atlas` live handoff.
- `external publication -> measurement -> learning` closed loop.
- a single durable cross-repository identity spanning WorkItem, execution, artifact, publication and outcome.

## 7. Major gaps revealed by the map

### G01 — System-level WorkItem admission/control

The Content Factory specifies demand, routing, WIP, capacity and bottleneck management, but the implemented runtime is concentrated below this layer.

### G02 — Capability registry/binding across products

The system needs a stable mechanism for declaring what a capability can do, its constraints, evidence requirements, cost/risk characteristics and how a WorkItem invokes it. Individual repositories contain local contracts, but a cross-system capability registry is not proven.

### G03 — Cross-system identity and provenance

There is no proven durable chain equivalent to:

`work_item_id -> execution_id -> artifact_revision -> acceptance_id -> publication_id -> observation_id`.

### G04 — External effect reconciliation

Publication is not complete when a local command returns. The system needs an explicit external-effect observation and ambiguous-outcome recovery boundary.

### G05 — Measurement and learning loop

The Content Factory models learning, but no current implementation closes the loop from external outcome to changed knowledge/editorial/production behavior.

### G06 — System deployment/runtime boundary

Individual repositories can run locally and have CI evidence, but there is no proven system-level deployment topology defining which components run where, how they communicate, how secrets are granted, and how system health is observed.

### G07 — Cross-repository evidence model

Git history, runtime evidence, production artifacts, human decisions and external outcomes exist in different places. Their semantic relationship is documented only partially.

## 8. What should NOT be built yet

Do not respond to these gaps by immediately creating:

- another orchestration framework;
- another generic agent runtime;
- a new global ontology;
- a monorepo;
- a generic event bus;
- a full observability stack;
- autonomous background workers;
- provider routing/fallback;
- automatic publishing.

The current evidence is insufficient to justify those mechanisms as the next step.

## 9. Current smallest sufficient system proof

The next meaningful proof should be one complete cross-repository value slice, not another isolated subsystem:

```text
bounded demand
  -> Content Factory WorkItem
  -> Atlas orchestration
  -> controlled execution/capability invocation
  -> Whisper Studio production
  -> verification
  -> human acceptance
  -> one external or explicitly simulated release boundary
  -> observation record
```

The proof should explicitly expose identity, authority, evidence and failure/recovery boundaries. It should not require a full production deployment or autonomous operation.

## 10. Confidence classification

`VERIFIED`: repository statuses, documented boundaries, active runtime claims, and local capabilities cited by their current source files.

`DERIVED`: the four-component system arrangement and cross-repository capability relationships inferred by reconciling those sources.

`CANDIDATE`: the shared semantic chain and the proposed smallest sufficient cross-repository proof.

`UNKNOWN`: complete runtime integration, cross-system identity, external-effect reconciliation, closed learning loop, and system-level deployment topology.
