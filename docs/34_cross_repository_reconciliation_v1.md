# 34 — Cross-Repository Reconciliation v1

Date: 2026-09-14
Status: CURRENT WORKING RECONCILIATION — RESEARCH / ARCHITECTURE

## Purpose

Reconcile the ten repositories as a system without physically merging them.

This document supersedes neither repository-local source-of-truth files nor the earlier `docs/06_unified_state_dependency_map.md`. It records a newer cross-repository observation layer and explicitly distinguishes current GitHub evidence from older repository maps.

## 1. Repositories inspected

1. `content_factory` — editorial/control-plane model; active.
2. `thai-mythology-content-generator` — archived legacy n8n prototype.
3. `ai-creative-os` — archived research/creative/n8n workspace and historical Whisper Studio duplicate.
4. `whisper-studio` — active product prototype / media production system.
5. `ai-research-radar` — paused local research-intake tool.
6. `telegram_bot` — parked independent rental-lead bot.
7. `controlled-agent-executor` — stable/frozen bounded Atlas task engine.
8. `atlas-records` — historical read-only Atlas/Whisper evidence records.
9. `atlas-workspace` — retired pinned-workspace proof.
10. `-atlas-agent` — active Atlas orchestration/runtime product under current development.

GitHub account inventory confirms these ten repositories on 2026-09-14. The repository inventory is current platform evidence; older system-state documents that enumerate only eight repositories must therefore be treated as historical snapshots.

## 2. Important correction to the earlier unified map

The earlier `docs/06_unified_state_dependency_map.md` was a useful synthesis of the nine repositories around `content_factory`, but its purpose was semantic pattern extraction rather than current portfolio state. It also predates the current September 2026 Atlas development state.

The current architecture cannot be represented accurately by the older claim that `controlled-agent-executor` is the primary Atlas execution substrate and `-atlas-agent` is only another repository in the same historical set.

Current evidence shows two distinct Atlas-related layers:

```text
-atlas-agent
    = active orchestration / command / reasoning runtime

controlled-agent-executor
    = stable bounded execution engine with its own strict task boundary
```

They are related but not interchangeable.

## 3. Current repository role map

| Repository | Current role | Runtime status | Relationship to main system | Development posture |
|---|---|---|---|---|
| `content_factory` | editorial information/control model | active | system-level owner of demand, knowledge, editorial, production, verification, release, observation and learning semantics | active |
| `-atlas-agent` | orchestration / command / reasoning runtime | active development | receives bounded work and orchestrates execution; current I02 work preserves Factory provenance | active |
| `controlled-agent-executor` | bounded execution/control substrate | stable feature-frozen | possible executor boundary for controlled mutations; not the Atlas reasoning layer | maintenance / defect fixes |
| `whisper-studio` | media production product | active prototype | concrete production capability / first practical cross-repository target | active but bounded |
| `ai-research-radar` | research intake experiment | paused | research signal source; no automatic build route | paused |
| `atlas-records` | historical evidence store | historical read-only | evidence/history only; no authority or runtime role | read-only |
| `atlas-workspace` | historical reproducibility proof | retired | historical proof only | retired |
| `ai-creative-os` | legacy creative/n8n research | archived | reference/history; overlaps historically with Whisper Studio | archived |
| `thai-mythology-content-generator` | legacy n8n content prototype | archived | historical predecessor; overlaps with old content pipeline ideas | archived |
| `telegram_bot` | independent application prototype | parked independent | no current architectural edge to Factory/Atlas/Whisper | parked |

## 4. L0 — system boundary

The strongest current system boundary is not a single repository.

```text
                    CONTENT FACTORY
             editorial/control semantics
                       |
                       | bounded WorkItem
                       v
                  ATLAS AGENT
          orchestration / command / authority
                       |
                       | execution contract
                       v
        CONTROLLED EXECUTION BOUNDARY
          controlled-agent-executor
                       |
                       | capability / production task
                       v
                 WHISPER STUDIO
              concrete media production
                       |
                       v
              verification / acceptance
                       |
                       v
            release / publication effect
                       |
                       v
                observation / learning
                       |
                       +------> Content Factory

Supporting / historical layers:

ai-research-radar      research intake (paused)
ai-creative-os         archived creative research
thai-mythology-*       archived n8n prototype
atlas-records          historical evidence
atlas-workspace        retired proof
telegram_bot           independent application
```

This is a working architecture hypothesis, not yet a proven end-to-end runtime graph.

## 5. L1 — major value/control flows

### F1 — Editorial demand

```text
Signal / question
  -> Content Factory WorkItem
  -> editorial specification / acceptance criteria
```

### F2 — Orchestration

```text
WorkItem revision
  -> Factory/Atlas boundary
  -> Atlas parent command
  -> RepoAnalysis / other bounded command
  -> WorkOrder
```

The current Atlas I02 proof explicitly preserves `work_item_id` and `work_item_revision_id` as provenance and does not place them into `parent_command_id`. `parent_command_id` remains an Atlas command identity. The external Factory adapter is not yet implemented.

### F3 — Controlled execution

```text
Atlas execution boundary
  -> controlled execution / capability request
  -> concrete attempt
  -> observed result
```

The exact split between `-atlas-agent` execution ownership and `controlled-agent-executor` use must be proven from a real end-to-end slice rather than assumed from repository names.

### F4 — Production

```text
production request
  -> Whisper Studio
  -> asset/render candidates
  -> verification
  -> human/product acceptance
  -> release candidate
```

Whisper Studio is explicitly not an automatic publisher and currently requires human quality boundaries. Its current `PROJECT_STATE.md` states that it can assemble an authored local asset pack into a synchronized vertical MP4, but cannot yet generate an accepted video from a brief without pre-created image and speech assets.

### F5 — Research intake

```text
local research signals
  -> ai-research-radar
  -> scored rows / review outcomes / handoff packets
```

Radar is paused and has no automatic route into Whisper Studio or Content Factory.

## 6. L2 — capabilities observed

### Content Factory

Observed semantic capabilities include:

- WorkItem identity and revisioning;
- demand/intake routing;
- research/knowledge semantics;
- editorial specification;
- production and asset semantics;
- verification;
- acceptance;
- release/publication boundary;
- observation and learning model.

### Atlas Agent

Current repository evidence shows:

- command center ownership of goal/plan/permissions/records/result;
- direct repository analysis;
- optional RepoAnalyst as a bounded `Agent.as_tool()` specialist;
- typed WorkerSpec / WorkOrder / ResultEnvelope;
- hard repository scope for RepoAnalyst;
- append-only SQLite lifecycle journal;
- operation hash and atomic WorkOrder attempt capture;
- replay and ambiguous-outcome blocking;
- explicit human result decisions;
- publication version identity and Telegram approval/publication controls;
- web research tool and repository read/write controls;
- current I02 Factory provenance preservation.

### Controlled Agent Executor

Current active route:

```text
authorized task
 -> detached Git worktree
 -> Forge claim/lease
 -> allowlisted patches
 -> acceptance checks
 -> REVIEW
 -> Atlas integrity review
 -> AWAITING_HUMAN_DECISION
```

It owns bounded execution controls, not editorial truth. Its README explicitly says the active route is `atlas_native/` and historical `atlas001`–`atlas005`, `atlas_runtime`, `mr001`, and `agent_architect` paths are not parallel entry points.

### Whisper Studio

Current repository state says:

- active prototype;
- local renderer baseline;
- human quality status `REVISE`;
- no automatic next phase;
- local asset-pack assembly into vertical MP4 is proven;
- brief-to-accepted-video generation is not yet proven;
- external/paid generation, provider routing, autonomous agents, publishing and analytics remain inactive directions in the current state document.

### Radar

Observed capabilities:

- local metadata ingestion;
- deterministic scoring;
- latest-score projection;
- append-only score history;
- human review outcomes;
- handoff packets.

Explicitly excluded from current runtime:

- external search;
- scraping;
- Telegram collection;
- LLM scoring/summarization;
- publishing;
- Whisper Studio build triggers.

### Historical repositories

`atlas-records` retains contracts/results/decisions but is not an authority source. `atlas-workspace` retains pinned manifests/contracts and offline verification fixtures but is retired. `ai-creative-os` and `thai-mythology-content-generator` preserve historical creative/n8n workflows but have no active production path. `telegram_bot` is a separate parked application.

## 7. L3 — process boundaries

The current strongest process chain is:

```text
bounded demand
 -> WorkItem
 -> Atlas orchestration
 -> capability request
 -> controlled execution
 -> Whisper Studio production
 -> verification
 -> human acceptance
 -> release
 -> publication
 -> observation
 -> learning
```

Only the first part of this chain is currently demonstrated as a cross-repository contract. The current Atlas I02 work proves provenance preservation through command materialization, not the external Factory adapter and not the complete production chain.

Therefore:

```text
END_TO_END_RUNTIME=NOT YET PROVEN
I02_PROVENANCE_SLICE=PARTIALLY PROVEN / FOCUSED TEST
EXTERNAL_FACTORY_ADAPTER=NOT IMPLEMENTED
```

## 8. L4 — concrete runtime/data boundaries

### Identity layers

Do not collapse:

```text
work_item_id
work_item_revision_id
command_id
operation_id
run_id
work_order_id
execution_id
attempt_id
output_revision_id
verification_id
acceptance_id
release_id
publication_id
observation_id
```

The current Atlas I02 decision specifically confirms that Factory work-item identity is provenance, while Atlas command and execution identities remain Atlas-owned.

### Evidence layers

```text
research/source evidence
runtime execution evidence
verification evidence
human decision evidence
publication/external-effect evidence
```

These are different evidence classes and must not be silently promoted into one another.

### Authority layers

```text
information
 -> review
 -> decision
 -> authorized effect
```

A successful execution is not acceptance. A review is not publication. A publication record is not proof of external effect unless the external effect is independently observed.

## 9. What is genuinely shared across repositories

The reconciliation confirms that the following patterns recur strongly enough to remain system-level principles:

1. Current state must be separated from historical state.
2. Identity must be separated from mutable content.
3. Version/revision must participate in meaning when a decision targets mutable content.
4. Evidence must remain linked to the exact object/revision it supports.
5. Review, acceptance, release and external effect are separate boundaries.
6. Unknown/ambiguous outcome is a legitimate state.
7. Historical repositories and branches must not silently reactivate.
8. Repository existence does not imply runtime dependency.
9. A proposed next action does not itself grant execution authority.
10. Cross-repository relations should be explicit rather than inferred from shared history or naming.

These principles are stronger candidates for the system-wide model than any particular directory layout.

## 10. What must NOT be merged into one abstraction

The following remain domain-specific:

### Editorial semantics

```text
source
evidence
claim
knowledge
editorial intent
content specification
observation
learning
```

### Orchestration semantics

```text
command
operation
run
work order
authority
context
```

### Execution semantics

```text
execution
attempt
lease
worktree
patch
process evidence
recovery
```

### Production semantics

```text
scene
shot
asset
candidate
selected asset
render
verification
release
```

The architecture should connect these through explicit contracts rather than inventing one universal object to replace all of them.

## 11. Current duplication / historical overlap

### Confirmed overlap

`ai-creative-os` and `thai-mythology-content-generator` contain historical n8n/content-production structures that overlap conceptually and, in places, operationally with later Whisper Studio/content-factory ideas. Both are now explicitly archived; they should be treated as research/history, not parallel production systems.

### Confirmed Atlas historical layering

`atlas-workspace` and `atlas-records` are historical proof/evidence layers. `controlled-agent-executor` is the maintained bounded execution component. `-atlas-agent` is the current active orchestration/runtime repository. They should not be physically merged merely because they share the Atlas name.

### Independent project

`telegram_bot` has no current dependency edge into the main system and should remain independent unless a future explicit request changes that boundary.

## 12. Architecture gaps now visible

The reconciliation identifies the following concrete gaps:

1. **Factory → Atlas transport/adapter:** current I02 provenance model exists inside Atlas, but the external adapter is not implemented.
2. **Atlas → controlled execution boundary:** the precise production handoff between `-atlas-agent` and `controlled-agent-executor` requires a real traced slice.
3. **Execution → Whisper Studio capability contract:** the interface is described conceptually but not yet demonstrated as a real cross-repository runtime path.
4. **Whisper Studio → verification/acceptance:** production-local controls exist, but cross-repository evidence binding is not yet demonstrated.
5. **Release → publication → observation:** current Content Factory semantics exist, but independently verified external effect is not yet established.
6. **Observation → learning:** currently modelled conceptually, not implemented as a complete feedback loop.
7. **Portfolio source-of-truth reconciliation:** older eight-repository system-state documents do not include the current `content_factory` and `-atlas-agent` roles; this document is the current cross-repository reconciliation layer until replaced by a newer verified map.

## 13. Physical merge decision

No physical merge is authorized or implied by this reconciliation.

The current evidence supports a **federated architecture**:

```text
Content Factory
   | contract
   v
Atlas Agent
   | execution contract
   v
Controlled Executor / capability boundary
   | production contract
   v
Whisper Studio
```

Separate repositories remain appropriate because they have different ownership, state models, failure modes and authority boundaries.

The goal is therefore not repository consolidation. The goal is **contractual interoperability with explicit identity and evidence boundaries**.

## 14. Next legitimate proof

Do not expand all nine repositories further before testing the most valuable architectural claim.

The next proof should be one bounded real slice:

```text
Content Factory WorkItem revision
    -> Atlas parent command
    -> Atlas WorkOrder
    -> controlled execution request
    -> concrete executor/capability
    -> Whisper Studio operation
    -> result/evidence
```

Then add only the minimum verification/acceptance/release links required to observe the full boundary.

A successful slice would convert the current architecture from a mostly reconciled model into a demonstrated system.
