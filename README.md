# Content Factory

Исследовательская и исполняемая среда для проектирования и запуска `Content Factory`.

## Current system hierarchy

```text
CONTENT ECOSYSTEM
│
├── STRATEGY / INTENT
├── AUDIENCE / MARKET
├── PRODUCT / BUSINESS
├── CONTENT FACTORY
│   ├── VALUE FLOW
│   │   ├── INPUT
│   │   ├── KNOWLEDGE
│   │   ├── EDITORIAL
│   │   ├── PRODUCTION
│   │   ├── QUALITY
│   │   ├── DISTRIBUTION
│   │   └── LEARNING
│   ├── FACTORY CONTROL
│   └── SHARED SEMANTIC SUBSTRATE
├── CAPABILITY SYSTEM
├── ENGINEERING SYSTEM
└── EXPERIENCE / CHANNELS
```

`Content Factory` — функциональная система внутри `Content Ecosystem`. Capability и Engineering являются execution layers, позволяющими фабрике использовать абстрактные способности без прямой зависимости от конкретных инструментов и провайдеров.

## End-user Content Workspace

Первый пользовательский vertical slice теперь доступен непосредственно из HTTP service:

```text
SOURCE
  ↓
EXPLORE
  ├── summary
  ├── themes
  ├── stories + evidence
  └── moments
  ↓
SELECT STORY
  ↓
PRODUCE
  ├── long video
  ├── shorts
  ├── article
  └── social posts
  ↓
REVIEW
```

Implementation:

- `src/content_factory/workspace.py` — product orchestration and strict JSON contracts.
- `src/content_factory/product_http.py` — product HTTP surface while preserving `/health` and `/run`.
- `src/content_factory/static/index.html` — single-workspace browser UI.
- `tests/test_workspace.py` — product-layer contract tests.

The first product deliberately accepts pasted source material rather than pretending that media ingestion/transcription already exists. The semantic boundary is already the intended one: the user selects a story before production, rather than asking the model to blindly repurpose a finished asset.

## Executable Runtime

Контролируемый execution path:

```text
WORK ITEM
   ↓
ADMIT
   ↓
EXECUTE CAPABILITY
   ↓
VERIFY EXACT REVISION
   ↓
ACCEPT + AUTHORITY
   ↓
RELEASE AUTHORITY
   ↓
RELEASE
   ↓
PUBLISHER
   ↓
OBSERVABLE EFFECT
```

Реализация: `src/content_factory/runtime.py`.
Durable control state: `src/content_factory/runtime_store.py`.
Evidence projection: `src/content_factory/artifacts.py`.

Runtime сохраняет состояние Work Item и append-only event journal в SQLite WAL. State transition и соответствующее событие фиксируются атомарно. Restart recovery проверен тестами.

Ключевые инварианты:

```text
CAN EXECUTE
≠ CAN AUTHORIZE
≠ CAN PUBLISH

execution ≠ acceptance
publication ≠ outcome
```

## Real execution boundary

Первый provider boundary — OpenAI Responses API:

```text
WORK ITEM
    ↓
OpenAIResponsesAdapter
    ↓
OpenAI Responses API
    ↓
provider response id
    ↓
ExecutionResult
    ↓
revision-bound verification
```

Реализация: `src/content_factory/openai_adapter.py` и `src/content_factory/openai_capability.py`.

`OPENAI_API_KEY` читается только из environment. Секрет не хранится в repository или runtime event data.

## Deployable HTTP service

`src/content_factory/service.py` предоставляет минимальный внешний runtime API:

```text
GET  /health
POST /run   (Bearer FACTORY_API_TOKEN required)
```

`src/content_factory/product_http.py` расширяет его пользовательским интерфейсом:

```text
GET  /
POST /api/analyze
POST /api/produce
```

Все product endpoints используют тот же `FACTORY_API_TOKEN`.

`POST /run` выполняет реальную capability execution через configured provider, revision-bound verification, explicit acceptance authority и explicit release authority. Если `PUBLISH_URL` не задан, runtime использует внутреннюю release-запись без внешнего эффекта.

`PUBLISH_URL` должен быть HTTPS webhook. Только успешный HTTP 2xx от webhook считается `externally_observable=True`. Это доказывает доставку к webhook, но не доказывает audience/business outcome.

Persistent state and evidence are stored under `FACTORY_DATA_DIR`.

## Container / deployment

Deployment files:

- `Dockerfile`
- `render.yaml`
- `.github/workflows/ci.yml`

The default container command now starts `content_factory.product_http`, so the deployed service exposes both the existing runtime API and the end-user workspace.

The Render Blueprint defines a Docker web service, `/health` HTTP health check, persistent `/data` disk and secret environment variables. Render supports Blueprint-based Docker services and HTTP health checks; secrets marked `sync: false` are supplied during deployment rather than committed to Git. urlRender Blueprint specificationhttps://render.com/docs/blueprint-spec urlRender health checkshttps://render.com/docs/health-checks

Required deployment secrets:

```text
OPENAI_API_KEY
GEMINI_API_KEY       # used when FACTORY_PROVIDER=gemini
FACTORY_API_TOKEN
PUBLISH_URL
PUBLISH_AUTH_TOKEN   # optional, if the destination requires it
```

No secret value belongs in Git.

## API example

```json
{
  "work_item_id": "wi-demo-001",
  "revision_id": "request-r1",
  "objective": "produce a bounded explanatory text",
  "requested_outcome": "Write a 120-word scientifically cautious explanation of convergent evolution.",
  "knowledge_basis": ["claim:C4", "claim:C6", "source:Motani-2002"],
  "acceptance_authority": "human:owner",
  "release_authority": "human:owner"
}
```

The response exposes the Work Item state, execution identity, exact output revision, event chain and publication record when delivery succeeds. This makes the runtime inspectable from outside the chat.

## Free web retrieval + Gemini

When `FACTORY_PROVIDER=gemini`, research uses a separate retrieval layer rather than Gemini Search Grounding:

```text
USER BRIEF
   ↓
WIKIMEDIA + OPENALEX RETRIEVAL
   ↓
SOURCE / EVIDENCE PACK
   ↓
GEMINI 3.5 FLASH-LITE (plain chat)
   ↓
CLAIMS + EDITORIAL SYNTHESIS
   ↓
PRODUCTION
```

Implementation: `src/content_factory/free_research.py`.

The retrieval layer is API-key-free and stores source URLs plus concrete evidence excerpts. Gemini receives that pack as context and is not given a web-search tool. The same retrieval pack is reused for production formats in the same run.

The previous `GeminiWebResearchAdapter` remains available for isolated legacy tests, but it is no longer selected by the default `gemini` provider path.

## Evidence and research layers

The repository keeps the semantic production chain separate from execution:

```text
external evidence
→ claim graph
→ editorial specification
→ production specification
→ shot pack
→ assets
→ execution
→ verification
→ acceptance
→ publication
→ observation
```

Research and production documents must not be treated as proof of execution. External scientific claims require external evidence; repository text is the state of the work, not the source of truth for science.

## v1.0 status

```text
core web workflow               COMPLETE
research → knowledge review     COMPLETE
editorial → production → QC     COMPLETE
approval → export → publication COMPLETE
observation → learning          COMPLETE
incremental replay              COMPLETE
protected product API           COMPLETE
local credential-free smoke path COMPLETE
CI / container verification     COMPLETE
hosted Render preview           DEPLOYED
persistent hosted storage       REQUIRES /data disk deployment
real external media renderer    OPTIONAL (Whisper Studio)
real external publication       OPTIONAL (HTTPS webhook)
```

The application is v1.0 for personal/local use. The repository's production deployment definition uses a persistent `/data` disk; the current lightweight Render preview service uses ephemeral filesystem storage and therefore must not be treated as the durable production deployment until that storage configuration is applied.

See `docs/v1.0_release.md` for the release contract and explicit non-goals.

## Persistent character photo workflow

The existing workspace can select a repository character, import verified
originals and a production photo, prepare/edit a caption, perform explicit
identity/QC review, approve and export an Instagram publication ZIP.
Thematic runs and existing Telegram series use the same services.
See [shared character production](docs/character/production_cycle.md) for the
operator workflow and the precise limits of current Luka evidence.
