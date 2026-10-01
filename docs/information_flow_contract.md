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
- `PublicationRecord`: durable distribution record containing publication ID, run, channel, destination, artifact IDs, external ID, publication status/time, response and provenance.
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

`ContentBrief` persistence and immutable revisioning are implemented in SQLite. Exact revisions can be replayed into a new run without mutating the source revision.

Publication and outcome are not inferred from artifact generation. A publication record must only be created by the actual distribution boundary, and an observed outcome must be recorded separately.


## Distribution boundary

The executable product path is now:

`REVIEW → APPROVE → PREPARED PUBLICATION → DISTRIBUTE → PUBLISHED PUBLICATION RECORD`

Approval is the authorization boundary. Preparing a publication does not perform an external side effect.

Telegram is the first external distribution adapter. `TelegramDistributionAdapter` prepares a bounded text payload and publishes it only after an approved publication is selected. Automated browser E2E uses `FakeTelegramDistributionAdapter`, which performs no network call. A real Telegram proof requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` and is intentionally separate from CI.

Publication provenance retains the run, ContentBrief revision and artifact IDs. The information-flow graph adds `Artifact → Publication` edges only after a durable publication record exists.
