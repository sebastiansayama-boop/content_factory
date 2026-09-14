# Real Provider External Proof — Phase 2

## Status

Harness implemented. Real-provider proof is **not yet claimed passed** until the operator runs it with valid `OPENAI_API_KEY` in the execution environment.

## Goal

Prove one real Work Item reaches a real provider-generated output and a revision-bound `VERIFIED` state, with durable reconstruction after process exit.

This is Phase 2 (`real_execution`). It intentionally stops before acceptance, release, publication, and external-effect observation, which belong to later phases.

## Proof path

```text
WorkItem
  -> FactoryRuntime submit/admit
  -> OpenAI Responses API
  -> provider response id
  -> ExecutionResult
  -> output_revision_id
  -> VerificationResult
  -> VERIFIED
  -> RuntimeStore persisted state
  -> process reopen
  -> VERIFIED reconstructed
```

The proof harness is `scripts/prove_real_provider_durable.py`.

## Preconditions

The execution environment must provide `OPENAI_API_KEY`. The harness reads the secret through the existing integration boundary; the value is not written to the repository or proof report.

The provider binding uses the repository's existing OpenAI Responses capability and the current configured GPT-5.6 Luna model.

## Run

PowerShell:

```powershell
$env:OPENAI_API_KEY="<your key>"
uv run python scripts/prove_real_provider_durable.py
```

Expected terminal result:

```text
EXTERNAL PROOF PASSED
work_item_id=external-proof-...
operation_id=...
execution_id=...
output_revision_id=openai-response:...
provider_response_id=...
verification_revision_id=openai-response:...
events=4
report=data/external_proof/external-proof-....json
```

The exact event count may increase if the runtime emits additional recovery/evidence events; the important requirements are durable `operation_id`, execution identity, provider response evidence, exact output revision binding, and reconstructed `VERIFIED` state.

## Proof report

The report stores identifiers and a SHA-256 digest of the provider output. It deliberately does not store the API key or raw provider text.

## Acceptance conditions

The proof passes only when all of the following are true:

- the provider call returns HTTP success and a provider response id;
- the generated output is non-empty and contains `CONTENT_FACTORY_EXTERNAL_PROOF_OK`;
- `ExecutionResult.output_revision_id` is the revision verified by `VerificationResult`;
- execution evidence contains the provider response id;
- RuntimeStore contains the work item, attempt, execution projection, verification projection, and lifecycle events;
- a fresh `FactoryRuntime` opened after the first process exits reconstructs the same Work Item as `VERIFIED`.

A successful proof establishes real provider execution and durable reconstruction. It does **not** establish real publication or real external effect.
