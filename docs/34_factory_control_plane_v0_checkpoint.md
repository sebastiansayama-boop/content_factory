# Factory Control Plane v0 — Completion Checkpoint

## Scope closed

This checkpoint closes the bounded Control Plane v0 development cycle on top of the durable factory runtime v0.

The finished scope is:

- read-only local Control Plane server;
- repository value-flow navigation across factory zones;
- system-layer navigation across control kernel, execution substrate, and semantic substrate;
- durable runtime overview backed by `RuntimeStore`;
- operation view keyed by `work_item_id`;
- explicit operation identity via `operation_id`;
- attempt history with execution identity;
- durable execution, verification, acceptance, and publication projections;
- event history for lifecycle reconstruction;
- machine-model inspection from `model/content-factory-map.yaml`;
- deterministic demo path that persists runtime projections into `data/runtime.sqlite3`;
- automated HTTP/control-plane tests;
- repository CI test and container build passing on the final checkpoint commit.

## Definition of done

The milestone is complete when a user can enter the Control Plane and navigate from:

`Factory -> value-flow zone -> system layer -> operation -> attempt -> execution -> output -> verification -> acceptance -> release -> publication -> delivery -> observation`

while the runtime-backed portions are derived from durable repository state rather than demo-only in-memory state.

## Evidence

Final checkpoint commit:

`3554c4d5ef8e6d0d11f5891073242689f59d9837`

Observed CI results on that commit:

- `tests` workflow: success
- `CI` workflow: success
- CI `test` job: success
- CI `container` job: success

The deterministic demo now opens a real `RuntimeStore` and passes it into `FactoryRuntime`, so execution/verification/acceptance/publication projections are persisted and can be read by the Control Plane after the process exits.

## Explicit non-goals

This milestone does not claim the Content Factory is production-complete.

The following remain deliberately outside this checkpoint:

- real provider credential proof and real external model execution;
- real external publication/effect proof;
- distributed worker scheduling;
- queue/lease infrastructure;
- hard cancellation and timeout enforcement at the execution substrate;
- production-grade authority enforcement beyond the current runtime contract;
- full reliability/control phase;
- empirical completion of the learning loop;
- multi-provider production expansion.

These are future factory phases, not unfinished Control Plane v0 work.

## Operator rule

Treat the Control Plane as an observability and navigation surface. It is not a second source of truth and does not grant execution, acceptance, or publication authority.

The next development cycle should begin from a concrete external-proof requirement, not from additional Control Plane UI expansion.
