# 24 — Capability and Engineering Layer

This document extends the Content Factory operating model with the execution layers required to turn abstract work into controlled capabilities and concrete external effects.

## 1. Boundary

The Content Factory defines value-flow work and required outcomes. It should not be coupled directly to individual tools, models, vendors or infrastructure.

The execution boundary is:

```text
CONTENT ECOSYSTEM
        ↓
CONTENT FACTORY
        ↓
CAPABILITY SYSTEM
        ↓
ENGINEERING SYSTEM
        ↓
TOOLS / MODELS / SERVICES / PROVIDERS
        ↓
EXTERNAL EFFECT
        ↓
OBSERVATION ↺
```

## 2. Capability System

A capability is an abstract operation the factory may require. It is not a specific tool.

Candidate capabilities include:

```text
discover
research
extract
analyze
write
design
generate
transform
localize
verify
package
publish
measure
learn
```

A capability contract should define at minimum:

```text
capability_id
input contract
output contract
preconditions
constraints
quality requirements
authority requirements
failure semantics
observability requirements
```

The factory requests a capability. It does not select a vendor merely because that vendor exists.

## 3. Executor boundary

The executor turns a capability request into a controlled execution.

```text
CAPABILITY
    ↓
EXECUTOR
    ↓
TOOL / MODEL / SERVICE / PROVIDER
    ↓
RESULT / EFFECT
```

Example:

```text
generate_image
    ↓
image_generation_executor
    ↓
provider A / provider B
    ↓
image revision
```

The executor owns the translation between the capability contract and provider-specific mechanics.

## 4. Engineering System

The engineering layer provides the mechanisms needed to make capability execution reliable, inspectable and replaceable.

```text
ENGINEERING SYSTEM
├── DOMAIN MODEL
│   ├── identities
│   ├── revisions
│   ├── contracts
│   └── state
│
├── EXECUTION
│   ├── orchestration
│   ├── queues
│   ├── retries
│   ├── leases / recovery
│   └── idempotency
│
├── STORAGE
│   ├── content
│   ├── metadata
│   ├── evidence
│   ├── provenance
│   └── execution records
│
├── INTEGRATION
│   ├── provider adapters
│   ├── APIs
│   ├── webhooks
│   └── external systems
│
├── GOVERNANCE
│   ├── permissions
│   ├── authorization
│   ├── policy enforcement
│   └── release controls
│
├── OBSERVABILITY
│   ├── events
│   ├── logs
│   ├── metrics
│   ├── traces
│   └── audit records
│
└── INFRASTRUCTURE
    ├── compute
    ├── networking
    ├── secrets
    └── deployment
```

This is an engineering decomposition, not another value-flow stage.

## 5. Tool/provider boundary

Tools, models and external services are replaceable implementations behind engineering adapters.

```text
FACTORY REQUIREMENT
        ↓
CAPABILITY CONTRACT
        ↓
EXECUTOR CONTRACT
        ↓
ADAPTER
        ↓
PROVIDER
```

A provider must not become the semantic definition of a factory capability.

Changing provider A to provider B should not require changing the editorial process when the capability contract remains satisfied.

## 6. Authority boundary

Execution capability does not imply authority to create an external effect.

```text
CAN EXECUTE
≠
CAN AUTHORIZE
≠
CAN PUBLISH
```

Consequential operations therefore require an explicit authority check at the relevant boundary.

## 7. Result boundary

An execution result is evidence about an operation. It is not automatically an accepted content state.

```text
EXECUTION RESULT
    ↓
OBSERVED RESULT
    ↓
VERIFICATION
    ↓
ACCEPTANCE
    ↓
RELEASE AUTHORIZATION
    ↓
EXTERNAL EFFECT
```

The exact transition depends on the work item's contract and risk class.

## 8. Failure and recovery

The engineering layer must preserve enough identity and history to distinguish at least:

```text
not_started
pending
running
completed
failed
unknown
recovery_required
```

An ambiguous external result must not be treated as a safe failure merely because the provider request returned an error or timed out. Retry policy must account for possible external effects.

## 9. Shared semantic substrate

Capability and engineering layers consume the same semantic substrate as the factory:

```text
identity
revision
state
provenance
dependency
authority
transition
```

This prevents execution infrastructure from becoming a second, incompatible source of truth.

## 10. Existing project mapping

Existing engineering projects can be evaluated as implementations of capabilities or engineering mechanisms rather than being inserted directly into the factory's business flow.

Examples for investigation:

```text
Atlas
→ controlled orchestration / execution capabilities

Whisper Studio
→ media generation / transformation capabilities

Research Radar
→ discovery / signal-processing capabilities

controlled-agent-executor
→ execution reliability / authority / recovery mechanisms
```

These mappings are candidates, not final architectural assignments. Each must be validated against its actual contracts and production behavior.

## 11. Design rule

The factory asks:

```text
WHAT outcome/capability is required?
```

The capability system asks:

```text
WHAT operation can satisfy it?
```

The engineering system asks:

```text
HOW can that operation be executed reliably and observably?
```

The provider layer answers:

```text
WHICH concrete mechanism performs it?
```

The authority system answers:

```text
WHO/WHAT is allowed to cause the resulting effect?
```

## 12. Repository synchronization boundary

Runtime evidence and Git repository history are separate concerns.

```text
FACTORY RUNTIME
      ↓
WORKSPACE EVIDENCE SINK
      ↓
EXPLICIT REPOSITORY-SYNC OPERATION
      ↓
GIT HISTORY
```

The runtime must not silently commit or push repository changes. Repository synchronization is an explicit infrastructure operation with its own authority and verification boundary.

The first controlled implementation is a manually dispatched GitHub Actions workflow with repository contents write permission. It executes the runtime experiment against a checked-out repository, verifies that only permitted evidence zones changed, and commits the resulting artifacts only when changes exist.

This mechanism is a persistence boundary, not a new factory stage and not a source of content truth. A synthetic runtime experiment must not create an `01_observation` record because no external effect has been observed.

## 13. Status

`candidate / integrated working model`

This layer should be challenged against real production cases before concrete implementation architecture is selected.
