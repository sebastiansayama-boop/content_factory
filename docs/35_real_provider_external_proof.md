# External Execution Proof — Phase 2

## Status

The repository contains two proof paths. Neither is claimed passed until it is executed in the real local execution environment.

The **free primary path** is the local n8n execution substrate. The OpenAI path is optional and requires a paid/credited API account.

## Goal

Prove one real Work Item crosses an actual external execution boundary, produces a revision-bound output, persists execution and verification evidence, and reconstructs as `VERIFIED` after the process is reopened.

This milestone deliberately stops before acceptance, release, publication and observed external business effect.

## Free proof path: local n8n

```text
WorkItem
  -> factory-owned operation_id
  -> N8nExecutionAdapter
  -> local n8n webhook/workflow
  -> normalized n8n execution result
  -> ExecutionResult
  -> output_revision_id
  -> VerificationResult
  -> VERIFIED
  -> RuntimeStore persisted state
  -> process reopen
  -> VERIFIED reconstructed
```

The proof harness is `scripts/prove_local_n8n_execution.py`.

### Preconditions

A local n8n instance must be running with the existing `factory-execution` webhook/workflow. The default endpoint is:

`http://localhost:5678/webhook-test/factory-execution`

Override it with `N8N_FACTORY_WEBHOOK_URL` when necessary.

No paid model API, API credit or external secret is required for this proof.

### Run

PowerShell:

```powershell
cd C:\Users\sebas\content_factory
uv sync --extra dev
$env:N8N_FACTORY_WEBHOOK_URL="http://localhost:5678/webhook-test/factory-execution"
uv run python scripts/prove_local_n8n_execution.py
```

Expected result:

```text
EXTERNAL PROOF PASSED
work_item_id=external-proof-n8n-...
operation_id=...
execution_id=...
output_revision_id=...
evidence_refs=[...]
recovered_state=VERIFIED
recovered_events=4
provider=openai:not_used
execution_substrate=n8n:local
```

The important claims are: n8n was actually called; factory `operation_id` crossed the boundary unchanged; an execution identity and revision-bound output were returned; verification bound to that exact revision; RuntimeStore retained the projections; and a fresh process recovered the work item as `VERIFIED`.

## Optional paid provider proof

`scripts/prove_real_provider_durable.py` remains the OpenAI-specific proof path. It requires `OPENAI_API_KEY` and is not required for the free phase-2 execution-boundary proof.

The OpenAI binding uses the repository's existing Responses capability. The provider response id becomes evidence and the output revision is derived from that provider response.

## What this proves

A successful free proof establishes:

- real factory-to-execution-substrate transport;
- durable operation identity across the boundary;
- normalized execution result;
- revision-bound verification;
- durable reconstruction after process exit.

It does **not** establish:

- LLM/model generation;
- real public publication;
- externally observable business/content outcome;
- production-grade distributed execution;
- the learning loop.

Those require separate proofs.
