# Production Specification v0 — What Is Common Across Different Species?

## 1. Specification identity

- `production_specification_id`: `PROD-SPEC-2026-09-14-001`
- `work_item_ref`: `WI-2026-09-13-002-r4`
- `editorial_specification_ref`: `SPEC-2026-09-14-001`
- `claim_graph_ref`: `RG-2026-09-14-001`
- `status`: `PRODUCTION_REVIEW`
- `execution_authorized`: `NO`
- `publication_authorized`: `NO`

## 2. Production target

Create one short-form explanatory vertical video asset from the bounded editorial specification.

Target representation:

```text
bounded editorial specification
        ↓
authored shot pack
        ↓
Whisper Studio local renderer
        ↓
vertical MP4 asset revision
        ↓
verification / human acceptance
```

The production target is the video asset and its reconstructable production metadata, not publication.

## 3. Existing execution capability

- `capability_ref`: `whisper-studio / active local renderer`
- `repository`: `sebastiansayama-boop/whisper-studio`
- `execution_mode`: `local-first`
- `provider_mode`: `local authored inputs`
- `external_provider_call`: `NO`
- `credential_required`: `NO`

The current renderer can assemble PNG and WAV assets into a synchronized vertical MP4 and can produce subtitles, H.264/AAC export, a manifest and hashes. It does not currently generate the script, images or speech from the brief in the active route.

Therefore this production specification treats the authored shot pack as an explicit production input rather than assuming an unavailable generation capability.

## 4. Required production input

The authored shot pack must contain, at minimum:

- one approved visual asset per shot;
- one approved audio asset per shot;
- shot ordering and timing;
- text/subtitle content consistent with the bounded editorial specification;
- provenance for each substantive factual statement used in the asset.

The pack must not introduce claims outside `C1–C9` without a new research pass.

## 5. Content structure

The rendered video must preserve the narrative spine of `SPEC-2026-09-14-001`:

1. inherited biological toolkit;
2. recurring functional/environmental problems;
3. qualified role of constraints;
4. recurring locomotion solution;
5. camera-eye convergence;
6. reuse of ancient biological components;
7. similarity classified at the level being compared.

Required examples:

- thunniform locomotion across distantly related large aquatic vertebrates;
- vertebrate and cephalopod camera eyes.

## 6. Epistemic constraints

The production must preserve:

- C5 as `QUALIFIED`;
- C10 as `UNKNOWN`;
- organ/phenotype-level convergence versus component/gene-level homology or reuse;
- direct evidence versus bounded synthesis.

The asset must not assert that constraints force one solution, that similar phenotypes imply common ancestry, that convergent phenotypes generally imply convergent genes, or that physics alone explains convergence.

## 7. Output requirements

Expected primary output:

- vertical MP4;
- synchronized visual/audio sequence;
- subtitles where used;
- renderer manifest;
- output hash or equivalent integrity identifier;
- identifiable asset revision.

The exact output resolution and duration remain a production execution parameter and must be selected before execution according to the active renderer contract. They are not silently inferred from this specification.

## 8. Production identity

When execution begins, the production record must preserve the chain:

```text
work_item_revision
→ production_specification
→ production_id
→ execution identity
→ asset_id
→ output_revision_id
→ result_ref
```

The production specification itself does not assign an execution identity or output revision identity.

## 9. Acceptance criteria

A produced asset can proceed to verification only if:

- the exact source specification and claim graph are reconstructable;
- every substantive factual assertion is traceable to an allowed claim or separately researched evidence;
- both required examples are represented within their evidence boundaries;
- C5 remains qualified;
- C10 remains unknown;
- the organ/phenotype versus component/gene distinction is preserved;
- no forbidden deterministic or universal claim is introduced;
- the rendered artifact is identifiable by asset/revision metadata;
- renderer result and integrity metadata are preserved;
- production failure or uncertainty is recorded explicitly rather than treated as success.

## 10. Failure and boundary conditions

The production attempt must stop or enter rework if:

- the authored pack contains unsupported factual claims;
- a required input cannot be traced to the approved specification;
- the renderer cannot produce a reconstructable output;
- execution status is uncertain;
- the requested representation requires a capability not currently implemented.

Production success does not imply editorial acceptance and does not authorize publication.

## 11. Current gate

`PRODUCTION_REVIEW`

Execution remains blocked until the production input pack, concrete renderer parameters, production identity, and execution authorization are established.

## 12. Provenance

- Work Item: `WI-2026-09-13-002-r4`
- Editorial specification: `SPEC-2026-09-14-001`
- Claim graph: `RG-2026-09-14-001`
- Renderer reference: `sebastiansayama-boop/whisper-studio`
