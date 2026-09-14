# n8n Execution Contract v0

Status: PROPOSAL
Date: 2026-09-14

## Purpose

Define the boundary between the Content Factory control plane and an external workflow/agent execution runtime such as n8n.

The contract keeps factory semantics independent of n8n while allowing n8n workflows and LLM agents to execute bounded work.

## Ownership boundary

Content Factory owns:

- work_item_id and revision_id;
- process_id and process_revision_id;
- requested outcome and process constraints;
- capability identity and capability contract;
- authority and approval requirements;
- execution identity as the factory-facing execution record;
- output_revision_id;
- verification, acceptance, release, publication and observation states;
- evidence references and provenance;
- durable factory event history.

n8n owns:

- workflow graph execution;
- node-level execution;
- agent loop execution;
- tool calls and provider-specific credentials;
- workflow-local retries/waits/branching;
- n8n execution identifier and workflow execution metadata.

External providers own the actual provider-side operation and provider response identity.

## Invocation contract

The factory sends an execution envelope to the configured n8n entrypoint.

```json
{
  "contract_version": "n8n.execution.v0",
  "operation_id": "op-...",
  "work_item_id": "wi-...",
  "revision_id": "r1",
  "process_id": "content.research.v1",
  "process_revision_id": "pr-1",
  "capability_id": "research.web.agent",
  "requested_outcome": "...",
  "inputs": [],
  "knowledge_basis": [],
  "constraints": [],
  "success_signals": [],
  "authority_context": {
    "required": [],
    "grants": []
  },
  "callback": {
    "execution_status_target": "factory-defined"
  }
}
```

### Required fields

`contract_version`, `operation_id`, `work_item_id`, `revision_id`, `process_id`, `process_revision_id`, `capability_id`, and `requested_outcome` are required.

`operation_id` is the idempotency boundary for one factory dispatch operation. n8n must treat repeated delivery of the same operation as the same requested execution rather than creating an unbounded new logical operation.

## Return contract

The execution runtime returns a normalized envelope.

```json
{
  "contract_version": "n8n.execution.v0",
  "operation_id": "op-...",
  "work_item_id": "wi-...",
  "revision_id": "r1",
  "execution": {
    "runtime": "n8n",
    "runtime_execution_id": "12345",
    "status": "SUCCEEDED",
    "started_at": "...",
    "completed_at": "..."
  },
  "output": {
    "output_revision_id": "out-r2",
    "payload": "...",
    "evidence_refs": []
  },
  "provider_refs": [],
  "tool_calls": [],
  "agent_runs": [],
  "failure": null
}
```

A failed execution uses the same envelope with `execution.status = FAILED` or `UNKNOWN` and a structured `failure` object. Secrets must never appear in the envelope.

## Identity mapping

The factory remains the source of truth for the semantic chain:

```text
work_item_id
  -> operation_id
  -> runtime_execution_id
  -> output_revision_id
  -> verification
  -> acceptance
  -> release
  -> publication
  -> observation
```

n8n `runtime_execution_id` is evidence about execution inside n8n; it does not replace the factory `operation_id` or `execution_id`.

Agent and tool identities are subordinate execution evidence:

```text
operation_id
  -> runtime_execution_id
     -> agent_run_id
        -> tool_call_id
           -> provider/external reference
```

## Agent boundary

An LLM agent may execute inside an n8n workflow and may select tools dynamically. The agent does not own factory authority.

A tool call can produce a proposed action, but the factory remains responsible for policy/authority checks that are outside the n8n workflow boundary.

For sensitive tool calls, n8n human-in-the-loop may provide an operational approval step. That approval must still be mapped back to a factory authority/approval record when the action affects factory-owned state, acceptance, release or publication.

## Webhook transport

The first adapter may use an n8n Production Webhook as the execution entrypoint. n8n documents separate Test and Production webhook URLs; Production webhooks are registered when the workflow is published. Webhooks can authenticate callers and can return workflow-generated JSON responses.

The transport is replaceable. The factory contract must not depend on the webhook URL shape.

## First vertical proof

The first implementation should prove only:

```text
Factory Work Item
 -> n8n Production Webhook
 -> n8n workflow
 -> LLM Agent
 -> one or two tools
 -> normalized return envelope
 -> Factory ExecutionResult
 -> Factory verification
```

No publication is part of the first proof.

## Non-goals for v0

- no generic n8n workflow parser;
- no automatic import of arbitrary n8n workflows;
- no replacement of the Content Factory state machine with n8n state;
- no assumption that an agent's self-reported approval is authoritative;
- no provider-specific fields in the core factory contract;
- no requirement that n8n be the only execution backend.
