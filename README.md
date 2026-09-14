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

`POST /run` выполняет реальную capability execution через OpenAI, revision-bound verification, explicit acceptance authority и explicit release authority. Если `PUBLISH_URL` не задан, публикация невозможна и runtime fail-closed.

`PUBLISH_URL` должен быть HTTPS webhook. Только успешный HTTP 2xx от webhook считается `externally_observable=True`. Это доказывает доставку к webhook, но не доказывает audience/business outcome.

Persistent state and evidence are stored under `FACTORY_DATA_DIR`.

## Container / deployment

Deployment files:

- `Dockerfile`
- `render.yaml`
- `.github/workflows/ci.yml`

The Render Blueprint defines a Docker web service, `/health` HTTP health check, persistent `/data` disk and secret environment variables. Render supports Blueprint-based Docker services and HTTP health checks; secrets marked `sync: false` are supplied during deployment rather than committed to Git. urlRender Blueprint specificationhttps://render.com/docs/blueprint-spec urlRender health checkshttps://render.com/docs/health-checks

Required deployment secrets:

```text
OPENAI_API_KEY
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

## Current status

```text
semantic / research chain       COMPLETE FOR BOUNDED V0
factory runtime                 COMPLETE
persistent runtime state        COMPLETE
real provider boundary          IMPLEMENTED
HTTP deployment surface         IMPLEMENTED
container                        IMPLEMENTED
CI / container verification      IMPLEMENTED
live hosted instance             NOT YET DEPLOYED
real external destination        NOT YET CONFIGURED
real external proof              PENDING DEPLOYMENT + DESTINATION
```

The repository is now deployable, but it is not truthful to call it live until a hosting account actually creates the service, the secrets are provisioned, `/health` passes, and one real authorized Work Item reaches a real destination.
