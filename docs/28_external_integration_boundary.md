# 28 — External Integration Boundary

Status: `implemented design / awaiting real credentials and provider`

## Purpose

Define the boundary between Factory Runtime and external tools, APIs, credentials, compute, and publication systems.

The factory must never treat an external provider as part of its semantic model.

```text
WORK ITEM
  ↓
CAPABILITY CONTRACT
  ↓
EXECUTOR
  ↓
ADAPTER
  ↓
EXTERNAL SERVICE
  ↓
OBSERVED RESULT
```

## Integration classes

### 1. Compute

The runtime needs a place to execute continuously or on demand.

Minimum v0.1:
- one Linux host or managed container runtime;
- SSH administration;
- outbound HTTPS;
- persistent storage for runtime records;
- process supervision/restart;
- backups before durable state is introduced.

A VPS is an infrastructure option, not a factory capability. Do not couple the domain model to a particular host provider.

### 2. Secrets

Credentials are configuration/authority material, not content records.

Required separation:

```text
SECRET VALUE
    ↓
SECRET STORE / ENVIRONMENT
    ↓
ADAPTER
    ↓
PROVIDER
```

Never store raw API keys in:
- Git;
- content records;
- provenance events;
- test fixtures;
- logs;
- prompts or generated output.

The repository may contain only secret names/references, for example `OPENAI_API_KEY`, `N8N_WEBHOOK_URL`, or a provider-specific secret identifier.

### 3. Provider adapter

Every real integration must expose a narrow adapter contract.

Minimum adapter responsibilities:
- validate configuration without exposing secret values;
- translate canonical input to provider request;
- execute request;
- normalize provider response;
- return provider request/effect identity where available;
- classify timeout/error/ambiguous outcome;
- preserve enough evidence for verification.

Provider-specific response fields must not leak into the core Work Item model.

### 4. n8n boundary

n8n is treated as an external orchestration/service provider, not as the Factory Runtime itself.

Preferred boundary:

```text
Factory Runtime
    ↓ HTTPS
n8n Webhook / API
    ↓
n8n workflow
    ↓
external service(s)
    ↓
n8n result
    ↓ HTTPS
Factory Runtime
```

n8n may coordinate provider-specific work, but the factory remains the authority for Work Item state, acceptance, release authorization, and provenance identity.

For a webhook integration, the factory must record at least:
- integration_id;
- request_id / execution correlation id;
- work_item_id;
- input revision;
- capability;
- n8n execution reference if available;
- normalized result;
- returned external-effect identifier if any;
- outcome classification.

An n8n HTTP 2xx response is not by itself proof that the downstream external effect happened.

### 5. API keys and credentials

Credentials are introduced only when a real adapter is ready to consume them.

Sequence:

```text
adapter contract
  ↓
credential requirement
  ↓
secret provision
  ↓
connectivity test
  ↓
provider operation test
  ↓
normalized result
  ↓
verification
```

Do not provision a large set of credentials before their corresponding adapters and tests exist.

### 6. Network boundary

For a public server, expose only required inbound ports. Administrative SSH should be restricted to the administrator's source IP/range where practical. Public application traffic should use HTTPS.

The runtime should prefer outbound connections to providers and avoid exposing provider credentials or internal runtime APIs directly to the public Internet.

### 7. External-effect boundary

Publishing/delivery is a separate authority boundary:

```text
EXECUTION
  ≠
RELEASE AUTHORIZATION
  ≠
EXTERNAL EFFECT
```

A real publisher adapter must return an externally inspectable identifier or URL whenever the target system supports one.

If the provider response is ambiguous, the runtime must enter an `unknown`/recovery path rather than blindly retrying.

## Connection sequence

The recommended order is:

```text
1. Runtime contract
2. Local deterministic tests
3. CI execution
4. Compute environment
5. Secret mechanism
6. One provider adapter
7. Provider credentials
8. Connectivity test
9. Real capability execution
10. Verification
11. Release authority
12. One external publisher
13. External-effect observation
14. Durable storage
15. Recovery / idempotency
16. Additional providers and n8n orchestration
```

The order deliberately postpones broad infrastructure and multiple providers until one end-to-end path is proven.

## First real integration target

The first target should be a low-risk, reversible external effect.

Recommended shape:

```text
one Work Item
→ one capability
→ one provider
→ one verified output
→ one explicit release decision
→ one external delivery
→ one externally inspectable identifier
```

No automatic public publishing should be enabled merely because an API credential exists.

## Boundary tests

Each integration must have separate tests for:

1. missing credentials;
2. invalid credentials;
3. connectivity failure;
4. provider rejection;
5. timeout;
6. ambiguous timeout after request submission;
7. valid normalized result;
8. duplicate/replay request;
9. external effect observation;
10. credential non-disclosure in logs.

## What is intentionally not implemented yet

- provider-specific credentials;
- public server;
- production n8n instance;
- durable secrets manager;
- real external publication;
- automatic retries for ambiguous external effects;
- production database;
- multi-provider routing.

These are integration steps, not prerequisites for the semantic model.
