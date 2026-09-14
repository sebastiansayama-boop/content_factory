# Local n8n Execution Proof Workflow

## Purpose

This workflow is the reproducible local execution substrate for the free external-proof path. It is intentionally deterministic and does not require a paid model/provider.

The factory sends an `n8n.execution.v0` envelope to a webhook. The workflow validates the three factory identity fields, creates an n8n execution identity, creates a revision-bound output, and returns the contract expected by `N8nExecutionAdapter`.

## Workflow

`Factory Webhook → Build Factory Execution Result`

The workflow export is stored at:

`integrations/n8n/factory_execution_proof.workflow.json`

n8n supports importing workflow JSON through the Editor UI. citeturn942212search2

## Import

1. Open `http://localhost:5678`.
2. Import `integrations/n8n/factory_execution_proof.workflow.json` through the workflow menu.
3. Open the imported workflow.
4. For the current free proof command, keep the Webhook node in test mode and click **Listen for test event** before invoking the factory proof. n8n documents that test webhooks must be registered by listening before the request and remain active for a limited period. citeturn942212search5
5. Leave the workflow inactive for the test-URL path.

## Endpoint

The imported Webhook node uses the path:

`factory-execution`

The local test URL is therefore:

`http://localhost:5678/webhook-test/factory-execution`

When the workflow is later published/activated, n8n also provides a production webhook URL; production webhooks run automatically without the editor's test-listening step. citeturn942212search5

## Proof command

```powershell
$env:N8N_FACTORY_WEBHOOK_URL="http://localhost:5678/webhook-test/factory-execution"
uv run python scripts/prove_local_n8n_execution.py
```

## Expected result

The proof script must report:

```text
EXTERNAL PROOF PASSED
...
recovered_state=VERIFIED
...
execution_substrate=n8n:local
```

The result is not an LLM/provider proof. It proves a real external execution boundary, preservation of factory identity across the boundary, normalized execution/output evidence, and durable reconstruction after reopening the runtime store.
