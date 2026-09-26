# Reference-driven Content Factory capability-gap analysis

Date: 2026-09-26

Status: research baseline; not a product decision.

## Purpose

This document changes the product strategy from:

> build an AI/agent/content runtime and then find uses for it

to:

> use strong existing AI products as references/providers, identify what they already solve, and build only the capabilities that remain materially missing from the end-to-end production workflow.

Atlas is not a required product dependency for this strategy. Existing Atlas work is historical/experimental input until a concrete capability gap justifies reusing part of it.

## Target production chain

```
BRIEF
  ↓
RESEARCH
  ↓
SOURCES / EVIDENCE
  ↓
CLAIMS / KNOWLEDGE
  ↓
EDITORIAL
  ↓
PRODUCTION PLAN
  ↓
TEXT / IMAGE / VIDEO / AUDIO
  ↓
QC
  ↓
HUMAN REVIEW
  ↓
PACKAGE / DISTRIBUTION
  ↓
LEARNING
```

The key question for every stage is:

> Can an existing product already perform this sufficiently well, and can we connect to it?

Only a demonstrated gap should become custom Content Factory functionality.

## Reference set

| Reference | Primary capability | Evidence status | Candidate role |
|---|---|---|---|
| Perplexity | web research / retrieval / cited synthesis / agent API | verified from official product/API material | research provider |
| Storyflow | research-to-structure, editorial planning, scripts, calendars, repurposing plans | verified from official product pages | editorial reference / possible integration |
| Manus | general agent tasks and multi-step workflow execution via API | verified from official API docs | agent/execution reference |
| Genspark | general agent workspace / research / artifact production | needs independent verification in this pass | competitive reference |
| Runway | creative generation and reusable workflows | needs independent verification in this pass | media provider/workflow reference |
| Higgsfield | image/video generation API and model catalog | verified from official API material | media provider |
| Adobe Firefly | creative production workflows, batch execution, MCP, reusable workflows | verified from official Adobe material | production/workflow reference |
| ElevenLabs | voice/audio generation and asynchronous integrations/webhooks | verified from official API material | audio provider |
| Luma | image/video generation jobs, references and chaining | verified from official API material | media provider |
| Canva | conversational/agentic design, connectors, web research, brand intelligence, editable design | verified from official product material | design/packaging reference |

“Verified” here means that the stated capability was checked against an official source during this research pass. It does not mean the capability was executed or benchmarked by Content Factory.

## What existing products already cover

### Research

Perplexity is a strong external reference for retrieval and research. Its current Agent API exposes web search and agent-oriented capabilities, so Content Factory should not begin by building its own web search/crawler stack.

Decision:
- integrate a research provider boundary;
- preserve source/provenance data in our own product model;
- do not rebuild search ranking or a web index.

### Research → structure / editorial

Storyflow explicitly covers research-to-outline, visual research organization, content planning, video planning, scripts, calendars and repurposing plans. It can keep research, references and editorial structures together on a canvas.

Decision:
- our planner is not a defensible product moat;
- study Storyflow's representation of research-to-structure;
- only build a custom editorial layer if we need a capability Storyflow or another provider cannot supply.

### General agent execution

Manus exposes agents and tasks through an API and supports multi-turn task interaction, projects and file attachments.

Decision:
- do not build a generic autonomous agent merely because Content Factory needs multi-step work;
- use an agent provider when it is sufficient;
- keep our own orchestration thin and domain-specific.

### Creative production

Adobe Firefly now exposes reusable creative workflows, API execution, batch execution, progress tracking, cancellation, per-asset results and an MCP connector for agent-driven workflow discovery/execution.

Higgsfield exposes a developer API with a model catalog and programmatic image/video generation.

Luma exposes asynchronous generation jobs with IDs, polling, reference images and chaining from previous generations.

ElevenLabs exposes webhooks and integration mechanisms for asynchronous product events.

Decision:
- generation engines are provider capabilities;
- Content Factory should describe required outputs, references, constraints and quality criteria;
- providers should perform the expensive media generation.

### Design / packaging

Canva's current AI surface includes conversational design, iterative editing, persistent memory, connectors, web research and brand intelligence. Its AI connector exposes Canva capabilities to external AI assistants.

Decision:
- do not build a general design editor;
- use Canva or another design provider for editable visual packaging where appropriate;
- preserve the Content Factory's content identity and asset relationships independently of the design editor.

## Capability gap matrix

Legend:
- EXISTING = strong external capability exists
- CONNECT = use external capability through API/MCP/integration
- CUSTOM CANDIDATE = potentially worth building, but requires validation
- UNKNOWN = insufficient evidence; do not build on assumption

| Capability | Existing references | Current conclusion |
|---|---|---|
| Web research | Perplexity, Manus, Genspark | CONNECT |
| Source retrieval | Perplexity + provider APIs | CONNECT |
| Source provenance | Partial across products | CUSTOM CANDIDATE |
| Evidence → claim binding | Not established as a common cross-product primitive | CUSTOM CANDIDATE |
| Claim-level provenance into final content | Not established | CUSTOM CANDIDATE |
| Research → editorial structure | Storyflow | CONNECT / reference |
| Content calendar | Storyflow, Canva | CONNECT |
| Script generation | Storyflow, Manus, general LLMs | CONNECT |
| Image generation | Higgsfield, Luma, Firefly and others | CONNECT |
| Video generation | Higgsfield, Runway, Luma, Firefly | CONNECT |
| Voice/audio | ElevenLabs and others | CONNECT |
| Visual design | Canva, Firefly | CONNECT |
| Reusable media workflows | Runway, Firefly, Higgsfield patterns | CONNECT / reference |
| Cross-provider routing | Usually provider-specific | CUSTOM CANDIDATE |
| One canonical ContentRun across all providers | Not established | CUSTOM CANDIDATE |
| Asset provenance across providers | Fragmented | CUSTOM CANDIDATE |
| Dependency graph across claims/scripts/assets | Not established | CUSTOM CANDIDATE |
| Change invalidation / selective regeneration | Partially visible in some creative systems, not established end-to-end | CUSTOM CANDIDATE |
| Cross-format semantic consistency | Not established end-to-end | CUSTOM CANDIDATE |
| Deterministic + semantic QC across heterogeneous providers | Fragmented | CUSTOM CANDIDATE |
| Human review as a product-level state | Present in some products/workflows | CUSTOM CANDIDATE |
| Final package assembled from one canonical content identity | Not established | CUSTOM CANDIDATE |
| Generic agent runtime | Manus/Genspark/etc. | DO NOT BUILD initially |
| Generic workflow engine | Firefly/Runway/etc. already demonstrate the pattern | DO NOT BUILD initially |
| Generic MCP control plane | Multiple vendors already expose MCP | DO NOT BUILD initially |
| Own image/video/voice models | Strong specialist providers exist | DO NOT BUILD |

## The potentially valuable missing layer

The most promising gap is not generation. It is the semantic layer between research and multiple production providers.

Candidate model:

```
SOURCE
  ↓
EVIDENCE
  ↓
CLAIM
  ↓
EDITORIAL UNIT
  ↓
CONTENT ASSET REQUIREMENT
  ↓
PROVIDER OUTPUT
  ↓
QC
```

The important property is traceability across the chain.

Example:

```
YouTube sentence #47
    ↓
editorial statement E-018
    ↓
claim C-012
    ↓
evidence EV-042
    ↓
source SRC-009
    ↓
retrieved source + content hash
```

The same claim could then feed:

- YouTube script;
- narration;
- subtitles;
- Telegram post;
- article;
- infographic;
- thumbnail copy.

If the underlying claim or evidence changes, the system can identify affected downstream assets rather than regenerating everything.

This is a hypothesis, not yet a validated market gap.

## Second candidate gap: provider-independent content identity

A ContentRun should describe the content itself, not a particular provider.

Example:

```
ContentRun
  ├── canonical topic
  ├── approved claims
  ├── editorial decisions
  ├── visual language
  ├── asset requirements
  ├── generated assets
  └── distribution variants
```

A video provider, image provider, voice provider and design provider become replaceable execution components.

This is more specific than building another workflow engine.

## Third candidate gap: dependency-aware regeneration

Potential rule:

```
claim changes
    ↓
find dependent editorial units
    ↓
find dependent assets
    ↓
invalidate only affected outputs
    ↓
regenerate only affected outputs
```

This should be tested against actual provider capabilities before implementation. If a reference product already solves it adequately, integrate instead.

## What we should NOT build now

1. A new general-purpose agent runtime.
2. A new generic workflow/DAG engine.
3. A new MCP control plane.
4. A proprietary image/video/voice generation engine.
5. A web search engine/crawler.
6. A generic content calendar.
7. A generic visual editor.
8. A second parallel Atlas runtime.
9. A large provider abstraction layer before at least two real providers are exercised.

## Proposed build order

### Phase 1 — Reference validation

For each major reference, execute one real workflow or API path where access permits.

Record:
- input;
- output;
- lifecycle;
- API/MCP surface;
- state;
- artifacts;
- references;
- provenance;
- failure behavior;
- cost/limits where observable.

### Phase 2 — End-to-end production test

Take one real topic and attempt:

```
brief
→ research
→ evidence
→ claims
→ editorial
→ script
→ image
→ video
→ voice
→ social post
→ QC
→ final package
```

Use external products wherever possible.

### Phase 3 — Gap validation

For every handoff that fails, ask:

1. Is the capability actually missing?
2. Is it merely missing from our integration?
3. Is another provider already solving it?
4. Is the problem semantic rather than generative?
5. Would solving it benefit multiple content formats?

Only a repeated, provider-independent gap becomes a build candidate.

### Phase 4 — Minimal implementation

Build the smallest component that closes the validated gap.

Do not introduce a general platform abstraction unless two or more concrete integrations require it.

## Evidence sources

Official sources checked during this pass:

- Adobe Firefly Run-Workflow MCP:
  https://helpx.adobe.com/firefly/web/work-with-enterprise-features/creative-production/run-workflow-mcp-overview.html
- Adobe Firefly Workflow API:
  https://developer.adobe.com/firefly-services/docs/workflow-builder-api/
- Adobe Firefly published workflows:
  https://developer.adobe.com/firefly-services/docs/workflow-builder-api/guides/publishing/
- Canva AI 2.0:
  https://www.canva.com/newsroom/news/canva-create-2026-ai/
- Canva AI Connector:
  https://www.canva.com/ai-connector/
- Higgsfield API quick start:
  https://open.higgsfield.ai/quick-start
- Higgsfield API overview:
  https://higgsfield.ai/creator-hub/help-center/integrations/what-is-the-higgsfield-api
- Luma generation API:
  https://docs.agents.lumalabs.ai/api/resources/generations/methods/create
- ElevenLabs webhooks:
  https://elevenlabs.io/docs/eleven-api/resources/webhooks
- Manus API introduction:
  https://open.manus.ai/docs/v2/introduction
- Manus agents:
  https://open.manus.ai/docs/v2/agents-overview
- Storyflow research-to-outline:
  https://storyflow.so/research-to-outline
- Storyflow content planner:
  https://storyflow.so/ai-content-planner
- Storyflow content planning:
  https://storyflow.so/content-planning-tool

Runway and Genspark remain in the reference set, but their capabilities should receive a separate official-source verification before they are used as architectural evidence.

## Current conclusion

The working product hypothesis is now:

> Content Factory should not compete with specialist AI products at generation. It should connect them around a canonical content identity, research/evidence, semantic dependencies, provenance, cross-format consistency, QC and final packaging — but only where real experiments demonstrate that existing products do not already solve the problem.

This conclusion is deliberately falsifiable. The next experiment is an actual end-to-end production run, not another architecture exercise.

## First implementation from the gap analysis

The first gap candidate has now been implemented as a deliberately small domain layer: `src/content_factory/content_provenance.py`.

It records relationships between editorial units and provider-generated assets while preserving source/evidence/claim references. It does not execute providers, orchestrate jobs, replace provider workflows, or introduce a generic runtime. Tests are in `tests/test_content_provenance.py`.

This is an implementation of the hypothesis, not proof that the gap is commercially valuable. The next end-to-end experiment must use at least two distinct production providers and verify that the graph provides information that neither provider can preserve across the handoff.
