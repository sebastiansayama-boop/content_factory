# Information flow contract

The Content Factory treats semantic content lineage as a first-class graph. A run is not allowed to collapse into an untraceable sequence of prompts.

## Canonical flow

```text
SOURCE
  ↓
EVIDENCE
  ↓
CLAIM
  ↓
EDITORIAL POINT
  ↓
CONTENT ELEMENT
  ↓
ARTIFACT
  ↓
PUBLICATION
```

The current executable contract is implemented in `src/content_factory/information_flow.py`.

## Object responsibilities

- `Source`: external origin identified by title and URL.
- `Evidence`: concrete supporting material from one source.
- `Claim`: atomic assertion with confidence, scope, known unknowns, source references and evidence references.
- `EditorialPoint`: an explicit editorial decision with selected claim/evidence references.
- `ContentBrief`: the durable editorial contract containing selected claims, editorial points, content elements, formats and constraints.
- `ContentElement`: a typed content unit linked to one or more editorial points and its claim/evidence basis.
- `Artifact`: the generated deliverable and its direct claim/evidence dependencies.
- `PublicationRecord`: reserved for the real distribution boundary. It is intentionally empty until an actual publication operation occurs.
- `LineageEdge`: explicit directed relation between two objects.

## Fail-closed rules

The graph rejects:

1. claims without source or evidence references;
2. evidence that points to an unknown source;
3. artifacts that reference unknown claims or evidence;
4. artifacts with claims but without explicit evidence references;
5. claims whose evidence is not present in the artifact evidence set;
6. editorial/content/artifact nodes with missing upstream references;
7. lineage edges pointing to unknown objects.

This is validation, not a claim that the source itself is true.

## Runtime separation

Semantic lineage and execution trace are different concerns:

```text
Information flow:
Source → Evidence → Claim → Editorial → Content → Artifact

Execution trace:
Intent → Run → Stage → Task → Tool → Action → Result → Decision
```

The existing RuntimeStore already persists an append-only event journal. The next integration boundary is to make research, editorial and production provider calls emit the same trace identity rather than bypassing the runtime.

## Current boundary

Research is first captured as candidate knowledge and requires explicit promotion before editorial generation. The editorial stage now creates an explicit `ContentBrief` containing selected claims, `EditorialPoint` objects and `ContentElement` objects. The production plan carries the `ContentBrief` ID and content-element IDs into every asset request.

The information-flow graph is materialized after production requests have been bound to those IDs. The research-only vertical slice therefore reports lineage as deferred until the editorial contract exists; it no longer synthesizes a fake editorial point from the research summary.

The next integration boundary is persistence and versioning of `ContentBrief` as its own database entity rather than storing it only inside `ContentRun.result`.

Publication and outcome are not inferred from artifact generation. A publication record must only be created by the actual distribution boundary, and an observed outcome must be recorded separately.
