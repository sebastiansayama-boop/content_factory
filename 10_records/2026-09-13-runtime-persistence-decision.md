# Runtime → Repository Persistence Decision — 2026-09-13

## Problem

The previous `ArtifactStore` solved filesystem materialization but not Git repository durability. Calling a local filesystem sink "durable repository artifacts" was therefore too strong.

## Decision

Keep runtime evidence materialization as a filesystem sink, but make synchronization into the Git repository an explicit infrastructure operation outside `FactoryRuntime`.

The first implementation boundary is a manually dispatched GitHub Actions workflow. It may run the factory against the checked-out repository, verify the resulting artifacts, and commit only the generated evidence artifacts. It must not be triggered automatically by every runtime execution.

## Why

1. The runtime must not acquire GitHub credentials merely to execute a work item.
2. Repository writes are consequential and must remain explicitly authorized.
3. GitHub Actions supports repository-scoped `GITHUB_TOKEN` permissions and manual `workflow_dispatch` triggers.
4. The repository protocol requires an explicit verification step after material writes.
5. Automatic commits on every execution would turn execution into uncontrolled repository history churn and would blur execution with repository governance.

## Boundary

```text
FactoryRuntime
    ↓
ArtifactStore (workspace evidence)
    ↓
explicit repository-sync workflow
    ↓
Git commit / repository history
```

This does not make Git history part of runtime state.

## Synthetic execution rule

The current `__main__` program is a demo experiment, not a real editorial case. It must not claim an externally observable effect. Repository materialization from this demo is experiment evidence only.

## Required verification

The synchronization workflow must:

- execute the current runtime;
- verify the generated files are inside the allowed evidence zones;
- fail if unexpected repository files are modified;
- commit only when an explicit workflow invocation authorizes the repository write;
- leave real editorial observations to real external effects;
- preserve the generated event/provenance record.

## Not decided

This decision does not establish the final production repository-sync mechanism. GitHub Actions is the first controlled implementation boundary. A later real case may justify a different persistence service, API, or repository adapter.
