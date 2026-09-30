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
- `EditorialPoint`: the selected angle/narrative point that groups the claims used by a production run.
- `ContentElement`: the semantic unit produced for a particular artifact format.
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

The first implementation materializes the editorial point and content element deterministically from the selected research and generated package. This is intentional: it creates explicit typed boundaries without pretending that a separate editorial model already exists.

The next required step is to make editorial selection a real persisted object before production, then bind production tasks to those object IDs.

Publication and outcome are not inferred from artifact generation. A publication record must only be created by the actual distribution boundary, and an observed outcome must be recorded separately.
