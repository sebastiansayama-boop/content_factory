# Character production in the shared factory

Character runs use the existing ContentRun, KnowledgeContentBuilder, asset jobs,
registry, assembly, QC, approval, export, distribution and experience stores.
They do not have a separate application or lifecycle. A run without
`character_id` retains the thematic workflow.

## Operator workflow

1. Start `python -m content_factory.product_http` with `FACTORY_API_TOKEN`,
   `FACTORY_DATA_DIR` and the chosen text provider. `FACTORY_PROVIDER=local`
   supplies deterministic development captions; it is not live creative AI.
2. In the existing workspace, enter the token, load characters and select Luka.
   Select Instagram and enter the scene brief. A profile snapshot is pinned to
   the run; draft personality and eye-colour decisions stay unresolved.
3. Review the creator-supplied fictional context. This does not approve any
   canonical face or turn the specification into empirical research.
4. Upload an original reference and a prepared production image. The original
   must match the preserved manifest's SHA-256 and dimensions. A preview is
   rejected. Production images must be at least 512 pixels on each side.
5. Inspect the original and production image together, edit the caption if
   needed, and explicitly confirm identity, naturalism and the current caption.
   The confirmation binds to image hashes, the profile revision and the package
   revision. Any subsequent edit requires renewed review.
6. Approve and export. Instagram export is a ZIP containing the unmodified
   full-resolution image, UTF-8 caption and publication metadata/checksums.
   `EXPORTED` means ready for manual upload, not published to Instagram.
7. Telegram uses the existing distribution adapter. Publication remains a
   separate action. Record observed metrics against that publication, then
   create a learning candidate; promotion still requires an explicit decision.
   Prior accept/edit/regenerate feedback is retrieved by character and platform
   for subsequent briefs, as bounded editorial examples rather than facts.

The character-image path currently accepts **import**, not automatic generation.
Generic coloured stubs and stock photographs cannot satisfy its identity gate.
No paid provider is configured or silently selected. Non-character videos retain
the existing workflow; character video/replay is outside this first photo scenario. Use
`/regenerate` for a new character scene and repeat image import/review.

## API boundaries

- `GET /api/characters`, `GET /api/characters/luka`: profile and original inventory.
- `POST /api/imports`: authenticated binary image upload, maximum 50 MiB.
- `POST /api/characters/{id}/references/import`: JSON `reference_id` and returned
  upload `path`; preserves candidate status.
- `POST /api/runs`: ordinary run creation plus optional `character_id`.
- `POST /api/runs/{id}/factory`: review fictional context, prepare a plan,
  request an image import, then resume assembly and QC.
- `POST /api/runs/{id}/assets/import`: `job_id`, returned upload `path`,
  `provenance` containing `source`, `reference_id`, `character_revision_id`.
- `GET /api/runs/{id}/package`: includes the current identity-review challenge.
- `POST /api/runs/{id}/qc`: `character_review` containing `approved`,
  `decision_ref`, `character_revision_id`, `package_digest`, `asset_hashes`,
  `reference_id` and `reference_sha256`. Confirm only after inspecting the image
  and caption. The existing workspace constructs this request on an explicit
  human action.
- Existing `/package`, `/approve`, `/export`, `/export/download`, `/publish`,
  `/observe`, `/learn` and `/regenerate` remain the shared interfaces.

All runtime imports and exports live under `FACTORY_DATA_DIR`, outside Git.
Neither uploaded images nor tokens are committed by this workflow.

## Luka limitation

The repository preserves eight candidate references, their hashes and provenance.
Only the 80×93 face preview is locally available. ChatGPT Library originals are
not mounted or accessible through the tools in this task. Full Luka visual
production remains blocked until an original is transferred and explicitly
reviewed. No replacement face was generated, no canonical reference approved,
and no Instagram account or paid service created.
