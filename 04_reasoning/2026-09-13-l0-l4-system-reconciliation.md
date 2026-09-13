# L0-L4 Content Factory System Reconciliation

Status: `WORKING RECONCILIATION / NO MODEL PROMOTION`

Date: 2026-09-13

## Purpose

Reconcile the newly constructed L0-L4 system map against the current repository model and distinguish what already exists from what is partial, missing, contradicted, or unknown.

This record does **not** promote the L0-L4 map to canonical architecture. It is a reasoning/evidence artifact used to decide whether the current model is sufficiently complete to resume implementation work.

## Evidence hierarchy used

1. Current repository contracts and machine-readable model.
2. Existing executable implementation and tests referenced by the repository.
3. Current operating-model and direction documents.
4. External business-architecture and content-supply-chain references.
5. Hypothesis / proposed synthesis.

External references:

- SAP LeanIX: business architecture connects capabilities, value streams, information and organization; capabilities describe what the organization can do and value streams show end-to-end value delivery.
- Deloitte (2026): content supply chain is an end-to-end system for planning, creation/storage, activation, and measurement/optimization, underpinned by people, processes, technology and operating model.
- Deloitte: operating-model design should connect strategy, capabilities, processes, technology/data/AI, organization, governance and measurement.

These references support the mapping method; they do not prove that the proposed Content Factory model is locally correct.

## Status vocabulary

- `EXISTS` — explicit and materially represented in repository model and/or implementation.
- `PARTIAL` — represented, but only a bounded subset is implemented or specified.
- `MISSING` — required by the current system hypothesis but no sufficient local representation was found.
- `CONTRADICTED` — current evidence conflicts with the proposed map.
- `UNKNOWN` — cannot be established from current evidence.
- `CANDIDATE` — plausible architectural element not yet admitted to the current model.

## L0 — System purpose

### L0.1 System boundary

Status: `EXISTS`

Current repository explicitly places Content Factory inside Content Ecosystem, with upstream strategy/intent, audience/market and product/business context, and downstream experience/channel and business outcomes.

Evidence: `README.md`, `docs/23_content_factory_operating_model.md`, `model/content-factory-map.yaml`, `SPACE_MAP.md`.

### L0.2 Factory purpose

Status: `EXISTS`

Current purpose is to convert bounded demand and evidence-backed knowledge into verified, authorized and externally releasable content products while preserving provenance and reusable meaning.

This is narrower and more precise than the broader hypothesis that the Factory is an operating system for the entire content-value loop.

### L0.3 End-to-end external outcome loop

Status: `PARTIAL`

The repository models `external effect → learning → next cycle`, but real external effect and business/product outcome remain explicitly unproven. Learning is active research with external proof pending.

### L0.4 Strategy-to-execution operating model

Status: `PARTIAL`

Strategy/intent, Factory, capability system and engineering system are represented, but the actual operational relationship between strategic portfolio decisions, factory demand, production and business outcomes is not yet executable.

## L1 — Value system

Proposed L1:

`Sense & Prioritize → Define & Plan → Build Knowledge → Create & Produce → Assure & Authorize → Activate & Distribute → Measure & Learn`

### L1.1 Sense & Prioritize

Status: `PARTIAL`

Factory Control conceptually contains demand, priority, intake, routing and bottleneck management. No dedicated operational control plane is claimed.

### L1.2 Define & Plan

Status: `PARTIAL`

WorkItem contains objective, requested outcome, constraints, dependencies, capabilities, acceptance criteria, release requirements and success signals. Strategic portfolio planning and editorial planning are not implemented as a complete process.

### L1.3 Build Knowledge

Status: `PARTIAL`

Knowledge is an explicit value-flow stage and research/claim/provenance semantics exist. The repository also has a learning/memory model. A complete production knowledge pipeline from research intake to reusable knowledge used by execution is not proven.

### L1.4 Create & Produce

Status: `PARTIAL`

Runtime v0 can execute one bounded capability and produce an exact output revision. Real provider execution is Phase 2 and remains pending real proof. General multi-format production is not implemented.

### L1.5 Assure & Authorize

Status: `EXISTS` for semantic boundary; `PARTIAL` for operational system.

Verification, acceptance, authority and release are explicitly separated. Runtime enforces these boundaries. A general review/approval system is not implemented.

### L1.6 Activate & Distribute

Status: `PARTIAL`

Publisher boundary and delivery state exist in Runtime v0. No real external destination is proven; distribution is not a general capability layer yet.

### L1.7 Measure & Learn

Status: `PARTIAL`

Effects, observations and learning zones exist, and the learning model is explicit. Real outcome ingestion, attribution and outcome-driven learning remain unproven.

## L2 — Value streams

The following streams are candidates, not canonical model entries.

| ID | Candidate value stream | Status | Current evidence / gap |
|---|---|---|---|
| VS-01 | Signal → Decision | `PARTIAL` | Observation, reasoning and decision zones exist; no end-to-end demand-to-decision operating process. |
| VS-02 | Idea/Demand → Content Product | `PARTIAL` | WorkItem → runtime → verification/acceptance exists; editorial planning and general production are incomplete. |
| VS-03 | Knowledge → Content | `PARTIAL` | Knowledge basis is part of WorkItem; no complete proven knowledge-to-editorial-to-production stream. |
| VS-04 | Content → Audience | `PARTIAL` | Publisher/delivery boundary exists; real destination and channel activation are not proven. |
| VS-05 | Content → External Effect | `PARTIAL` | External-effect semantics exist; real externally observable effect is not started/proven. |
| VS-06 | Result → Learning | `PARTIAL` | Learning model and effect/feedback zones exist; real outcome feedback and causal attribution remain unproven. |
| VS-07 | Existing Content → New Value | `UNKNOWN` | Reuse is represented as a semantic requirement, but no complete value stream was found. |
| VS-08 | Portfolio Intent → Production Portfolio | `MISSING` | Portfolio context exists upstream, but no operational portfolio-control capability is implemented. |

Important reconciliation: the existing `INPUT → KNOWLEDGE → EDITORIAL → PRODUCTION → QUALITY → DISTRIBUTION → LEARNING` model is explicitly described as a value-flow projection, not a single global object lifecycle. Therefore the candidate L2 streams must not be collapsed into one state machine.

## L3 — Capability map

### A. Strategy / Intelligence

Status: `PARTIAL`

Strategy, audience/market and product/business context are explicit upstream boundaries. Signal detection, audience intelligence and portfolio decision capabilities are not operationally represented.

### B. Factory Control

Status: `PARTIAL`

Explicitly specified: prioritization, intake, routing, WIP, queues, capacity, scheduling, ownership, service expectations, orchestration and bottleneck management. The direction map explicitly says this control plane is not implemented.

### C. Knowledge

Status: `PARTIAL`

Research, extraction, analysis, evidence, claims, provenance, memory and learning are represented. A production-grade knowledge service/retrieval/update lifecycle is not proven.

### D. Editorial / Creative Planning

Status: `PARTIAL`

Editorial is a value-flow stage and WorkItem includes objective/outcome/constraints. Briefing, concept development, format/channel planning and reusable editorial process are not yet a complete capability system.

### E. Production

Status: `PARTIAL`

Capabilities such as write/design/generate/transform/localize are candidates in the model. Runtime has one selected capability and provider-neutral executor boundary. Multi-capability production is explicitly out of Runtime v0.

### F. Assurance

Status: `PARTIAL`

Verification, acceptance, authority and release semantics are strong and executable in bounded runtime. Broader factuality, rights, safety, brand, review routing and acceptance operations are not yet implemented as a general assurance system.

### G. Distribution / Activation

Status: `PARTIAL`

`publish` exists as a capability concept and injected publisher boundary exists. Real destination, channel adapters, scheduling and activation operations are not proven.

### H. Measurement / Learning

Status: `PARTIAL`

Measure/learn capabilities are present in the model and learning architecture is researched. Event collection, attribution, experiment measurement and business-outcome linkage are not operationally complete.

### I. Governance

Status: `EXISTS` for semantic rules; `PARTIAL` for operational governance.

Authority, provenance, policy and explicit transitions are strong repository principles. Sustained operational governance is explicitly parked.

## L4 — Operational processes

### P01 Demand intake and qualification

Status: `PARTIAL`

WorkItem admission exists. General demand intake/qualification/routing is conceptual rather than implemented.

### P02 Planning and routing

Status: `PARTIAL`

Required capabilities, dependencies, constraints and ownership are represented. Dynamic capacity/WIP/scheduling/routing are not implemented.

### P03 Research and knowledge formation

Status: `PARTIAL`

Research/evidence/interpretation/knowledge promotion chain exists as an operating-memory model. A complete executable knowledge-production process is not proven.

### P04 Brief and specification

Status: `PARTIAL`

WorkItem provides bounded objective/outcome/inputs/constraints/acceptance/release requirements. A distinct editorial brief/specification object/process is not yet established.

### P05 Production and assembly

Status: `PARTIAL`

Runtime executes one capability. Multi-step/multi-asset assembly is not implemented.

### P06 Quality / verification / acceptance

Status: `EXISTS` for bounded runtime semantics; `PARTIAL` for factory-wide process.

Exact revision verification, explicit acceptance and authority are implemented and tested in Runtime v0.

### P07 Release / publication / distribution

Status: `PARTIAL`

Release authority, publisher and delivery state exist. Real external publication is not started.

### P08 Observation / measurement

Status: `PARTIAL`

Observation/effect zones and metrics are defined. Real external observation ingestion is not implemented.

### P09 Learning / adaptation

Status: `PARTIAL`

Learning candidate and promotion model exists. Real external outcome-driven learning remains unproven.

### P10 Portfolio / capacity control

Status: `MISSING`

This is one of the clearest gaps between the current repository and the broader system hypothesis. Factory Control describes it, but no operational mechanism exists.

## Cross-cutting object model

A separate reconciliation is needed for the objects that move through the value system. Current strong objects include:

`WorkItem → ExecutionResult → Output Revision → VerificationResult → AcceptanceDecision → PublicationResult → Observation`

The broader candidate object chain is:

`Signal → Intent/Demand → WorkItem → Research/Claim/Knowledge → Brief/Specification → Asset Revision → Candidate → Verification Evidence → Accepted Package → Publication → Performance/Outcome → Learning`

Status: `PARTIAL`

The first chain is executable in bounded runtime. The second chain is a system hypothesis and should not yet be promoted into ontology classes. RULES.md explicitly requires semantic jobs and competency questions before ontology promotion.

## Cross-cutting decision / authority model

Status: `EXISTS` for core boundaries; `PARTIAL` for ecosystem-wide decisions.

Current strong boundaries:

`execution ≠ verification ≠ acceptance ≠ release ≠ publication ≠ outcome`.

Missing broader decision operations include portfolio selection, editorial planning, channel strategy and outcome-driven strategy changes.

## Cross-cutting information/provenance

Status: `PARTIAL`

Identity, revision, provenance, evidence, dependencies and authority are explicit. Runtime evidence and repository history are deliberately separated. A complete cross-system lineage from strategic intent through business outcome is not yet proven.

## Cross-cutting actors

Status: `UNKNOWN / PARTIAL`

Human authority and runtime/provider roles are explicit. A complete actor map across strategy, editorial, production, assurance, distribution, customer/audience and external platforms has not yet been established.

## Cross-cutting metrics

Status: `PARTIAL`

Flow, quality/governance and outcome metric families are defined in the operating model. Actual telemetry and outcome measurement are not operationally connected.

## Main reconciliation findings

1. The repository already contains a credible L0/L1 skeleton. We are not starting from zero.
2. The current implementation is concentrated in a narrow vertical slice: WorkItem → capability execution → verification → acceptance → release → publisher → observation, with durable local runtime state.
3. The largest missing architectural region is not another execution primitive. It is the operational layer above execution: demand/portfolio planning, editorial planning, routing, capacity/WIP, and general factory control.
4. The largest missing end-to-end region below distribution is real measurement/outcome integration and learning from external effects.
5. Knowledge is represented strongly as a semantic/operating-memory concept, but the production path from research to reusable knowledge to changed execution is not yet proven.
6. The current value-flow stages must not be turned into one global state machine. Existing documentation explicitly rejects that interpretation.
7. GitHub, Runtime, provider adapters and deployment belong below L4 as mechanisms/engineering infrastructure. They are not L0-L4 system definitions.
8. The next architecture decision should therefore be made against the complete L0-L4 map, not against the current Runtime roadmap alone.

## Current coverage summary

| Level | Current coverage | Main missing region |
|---|---|---|
| L0 purpose/boundary | `STRONG` | real business/outcome proof |
| L1 value system | `PARTIAL` | operational planning + outcome loop |
| L2 value streams | `PARTIAL` | explicit bounded streams and ownership |
| L3 capabilities | `PARTIAL` | control, editorial, distribution, measurement capabilities |
| L4 processes | `PARTIAL` | end-to-end operational processes outside bounded runtime |

## Decision status

No canonical model change is made by this record.

The record establishes a reconciliation baseline. Before implementation resumes, the next legitimate step is to decide which L0-L4 elements form the first **system-level MVP slice** and which remain intentionally outside scope.

## External research reconciliation

- `SUPPORTS_CURRENT_MODEL`: value streams and capabilities should be separated; capabilities are stable abilities rather than implementation details.
- `EXTENDS_CURRENT_MODEL`: information architecture and explicit end-to-end operating-model alignment should be treated as first-class mapping dimensions.
- `SUPPORTS_CURRENT_MODEL`: content supply chain should be viewed end-to-end across planning, creation/storage, activation and measurement/optimization.
- `REVEALS_GAP`: content decisions should connect more explicitly to measurable business outcomes and cross-functional ownership.
- `NOT_APPLICABLE`: external maturity claims and ROI figures are not evidence of local Factory effectiveness.

## Next legitimate step

Select the first system-level MVP slice from L0-L4 before implementing additional Runtime/deployment primitives.
