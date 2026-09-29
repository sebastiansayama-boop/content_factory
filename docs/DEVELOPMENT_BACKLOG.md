# Content Factory — Development Backlog

Status: working execution backlog
Scope: personal-use product → reliable product → SaaS foundation → scalable SaaS

Rule: a task is not complete because code exists. It is complete only when its closure evidence exists.

## Development levels

### L0 — Prototype / capability exists
Purpose: prove the mechanism can work.
Close when: implementation exists, a deterministic or controlled test proves basic behavior, failure behavior is known, and no production-readiness claim is made.
Evidence: unit/integration test, local execution, observed example result.

### L1 — Functional product / user outcome
Purpose: a real user completes the intended workflow and gets a useful result.
Close when: real end-to-end path works, output is usable, main failure states are understandable, provenance exists for factual claims, and a real run has been observed.
Evidence: E2E test, real run, human acceptance, known limitations.

### L2 — Reliable product
Purpose: the L1 outcome is repeatable and survives normal operational events.
Close when: state survives required restart/redeploy, failures do not silently corrupt state, retries are bounded/idempotent where required, provider failures are observable, deployment is reproducible, health/operational signals exist, and recovery has been executed.
Evidence: regression/E2E, recovery test, deployment verification, operational evidence.

### L3 — SaaS / scalable production foundation
Purpose: multiple users/tenants can use the product safely and economically.
Close when applicable: ownership and isolation are explicit, authorization is verified, usage/cost is measurable, quotas exist where needed, storage is production-appropriate, background work can scale, observability/recovery are defined, and security controls are tested.
L3 is not required for personal-use validation.

## Roles

Product Owner / PM — user outcome, scope, priority, acceptance criteria, non-goals, product metrics.

Product / UX Designer — user journey, workflow states, information hierarchy, error/recovery UX, accessibility.

Research / AI Engineer — discovery, research strategy, retrieval, source selection, evidence, claims, synthesis, verification, AI evaluation.

Backend Engineer — domain model, API, persistence, state transitions, idempotency, retries, provider boundaries, authorization.

Frontend Engineer — UI state, API integration, review controls, progress, errors, accessibility, results.

Editorial / Content Engineer — approved knowledge to editorial specification, coherent drafts, platform variants, provenance preservation, content quality.

QA / Evaluation Engineer — unit/integration/E2E, regression corpus, real-run verification, product-quality evaluation, defect reproduction.

Platform / SRE — CI/CD, runtime configuration, deployment, health, observability, persistence, recovery.

Security — secrets, authentication, authorization, tenant isolation, untrusted external content.

Data / Product Analytics — product metrics, run success/failure, quality/rework, cost, provider reliability, learning loops.

## P0 — Prove the core product outcome

### CF-PROD-01 — Product acceptance contract
Role: Product
Goal: define exactly what “Content Factory works” means for the primary user journey.
Close when: one canonical journey is documented; input/output/failures/human acceptance are explicit; measurable success criteria and non-goals exist.
Level: L1.

### CF-AI-01 — Real research pipeline
Role: Research / AI
Goal: demonstrate DISCOVERY → RESEARCH → EVIDENCE → SYNTHESIS → VERIFICATION.
Close when: a real topic completes the chain; sources are external and inspectable; claims link to concrete evidence; irrelevant sources are rejected; unsupported claims do not silently enter accepted knowledge; failures are diagnosable.
Level: L1.

### CF-AI-02 — Research evaluation set
Role: Research / AI + QA
Goal: fixed corpus of representative real research questions.
Close when: representative topics, expected evidence properties, relevance/grounding failure cases, and comparable rerun evaluation exist.
Level: L1 → L2.

### CF-ED-01 — Finished editorial output
Role: Editorial / Content
Goal: turn accepted knowledge into a genuinely usable article.
Close when: claims remain supported; structure is coherent; provenance survives transformation; human editorial review passes; obvious boilerplate does not dominate.
Level: L1.

### CF-FE-01 — Review-to-result workflow
Role: UX + Frontend
Goal: TOPIC → RESEARCH → REVIEW → PRODUCE → RESULT.
Close when: each state has a clear primary action; blocked actions explain why; internal IDs/status codes are hidden by default; errors are recoverable; accessibility basics are verified.
Level: L1.

### CF-QA-01 — Core E2E acceptance
Role: QA / Evaluation
Goal: prove the entire core journey.
Close when: automated E2E covers state transitions; one real external run is recorded; human verifies content; failure cases are tested.
Level: L1.

## P1 — Make the outcome reliable

### CF-BE-01 — Durable ContentRun lifecycle
Role: Backend
Close when: lifecycle is explicit; invalid transitions are rejected; state survives restart; failed runs retain diagnostics; repeated requests do not silently duplicate work.
Level: L2.

### CF-BE-02 — Idempotent external operations
Role: Backend + Platform
Close when: operation identity is explicit; provider evidence exists where applicable; duplicate semantics are tested; retry behavior is bounded.
Level: L2.

### CF-OPS-01 — Reproducible deployment
Role: Platform / SRE
Close when: CI builds the deployment artifact; deployed runtime matches the tested runtime; health check passes; required configuration is explicit; fresh deployment is verified.
Level: L2.

### CF-OPS-02 — Durable hosted storage
Role: Platform + Backend
Close when: persistent storage is configured; restart and redeploy tests pass; asset references remain valid; recovery expectations are documented.
Level: L2.

### CF-OPS-03 — Operational observability
Role: Platform / SRE
Close when: structured logs identify run/operation; provider failures are visible; duration/failure reason are observable; health endpoint exists; basic operational metrics exist.
Level: L2.

### CF-QA-02 — Reliability regression suite
Role: QA / Evaluation
Close when: core E2E is repeatable; restart/recovery and external failure cases are covered; known production defects become regression tests.
Level: L2.

### CF-AI-03 — Content quality evaluation
Role: AI/Evaluation + Editorial
Close when: factuality/grounding, relevance, completeness, structure, style and unsupported-claim rate are evaluated on a fixed corpus.
Level: L2.

## P2 — SaaS foundation

### CF-SEC-01 — Account/tenant boundary
Role: Backend + Security
Close when: every durable user object has an owner boundary; authorization is server-side; cross-account access tests fail closed; secrets are excluded from content/runtime records.
Level: L3.

### CF-SEC-02 — External-content security
Role: Security + Backend + AI
Close when: prompt-injection risks are bounded; external URLs are validated; tool permissions are constrained; untrusted content cannot directly authorize irreversible actions.
Level: L3.

### CF-DATA-01 — Product analytics
Role: Data / Product
Initial metrics: topic submission, research success/failure, approved-claim rate, time to first approved claim, time to usable content, regeneration rate, human edit/rework rate, production failure rate.
Close when: event definitions are stable and metrics can be queried and compared across releases.
Level: L2 → L3.

### CF-OPS-04 — Background execution
Role: Platform + Backend
Only introduce when observed workload requires it.
Close when: long jobs survive request disconnects; job status is observable; retry policy is explicit; the chosen queue/orchestrator is justified by measured need.
Level: L3.

### CF-DATA-02 — Cost and provider economics
Role: Data + AI + Product
Close when: provider usage is attributable to a run; cost estimates exist; expensive providers have measured alternatives; product decisions can use observed cost.
Level: L3.

## Definition of Done

L0: code → test → observed behavior.

L1: real user path → real result → human acceptance → known limitations.

L2: L1 + persistence → recovery → repeatability → observability → deployment verification.

L3: L2 + ownership → isolation → security → usage/cost → scalable operations.

## Execution order

### Slice 1 — Research truth
Product: CF-PROD-01.
AI: CF-AI-01, CF-AI-02.
UX/Frontend: CF-FE-01.
QA: CF-QA-01.
Exit: a real topic produces reviewable, evidence-backed knowledge that a human can approve.

### Slice 2 — Editorial truth
Editorial: CF-ED-01.
AI/Evaluation: CF-AI-03.
QA: extend CF-QA-01.
Exit: approved knowledge produces a human-accepted finished article.

### Slice 3 — Reliability
Backend: CF-BE-01, CF-BE-02.
Platform: CF-OPS-01, CF-OPS-02, CF-OPS-03.
QA: CF-QA-02.
Exit: the same user outcome survives restart/redeploy and failures are diagnosable.

### Slice 4 — SaaS foundation
Security: CF-SEC-01, CF-SEC-02.
Data: CF-DATA-01, CF-DATA-02.
Platform: CF-OPS-04 only if workload evidence requires it.
Exit: multiple users can be introduced without rewriting the core domain model or trusting client-side boundaries.

## Non-goals until evidence requires them

Do not introduce by default: Kubernetes, Kafka, Redis, Temporal, custom agent frameworks, microservices, complex event buses, multi-region deployment, elaborate billing infrastructure, or autonomous irreversible actions.

Each requires a concrete workload, failure mode, or product requirement that the simpler architecture cannot satisfy.

## Core operating loop

HYPOTHESIS → BUILD → REAL RUN → OBSERVE → FAILURE / EVIDENCE → CHANGE → REGRESSION TEST → REAL RUN AGAIN.

The backlog succeeds when this loop produces progressively better user outcomes, not when every checkbox is marked.
