# Shared character production cycle — 2026-10-08

Branch: `feature/experience-retrieval-v1`, existing PR #179.
Inspected base: `f06ab53427f140fffcda0240f24de2c0e189723b`.
Status: local pipeline verified; actual Luka visual/external proof remains blocked.

## Findings and implementation

The existing factory already has durable runs, explicit research promotion,
knowledge-backed editorial production, asset jobs, assembly, release gates,
Telegram distribution and experience records. The branch additionally preserves
Luka's profile and eight candidate manifests, and has experience retrieval.

Missing integration was addressed in those existing components:

- Snapshot the existing character profile and manifest revisions into a run.
- Verify original imports against stored checksums/dimensions; refuse previews.
- Import a full-resolution production image into an existing visual asset job.
- Use one visual plus caption for creator photo posts, without mandatory voice.
- Review identity/naturalism and edited caption against exact hashes/revisions.
- Export actual media and caption as an Instagram ZIP; refuse unconfigured
  Instagram publication rather than claiming a local release reached Instagram.
- Connect experience retrieval to HTTP generation, filter by platform/character
  and limit prompt examples to compact captions/feedback.
- Fix successful requests being counted as failed authentication, package QC
  losing information flow, and publication ignoring the requested channel.
- Preserve episode-specific questions while retaining the common series question
  and prior established state in the existing library preparation adapter.

No profile, candidate reference, library text or source was promoted or rewritten.

## Execution evidence and limits

`tests/test_character_cycle.py` runs real HTTP requests against
`ThreadingHTTPServer`, real SQLite stores, uploads real image bytes, edits and
rechecks the package, restarts the service, verifies ZIP bytes/checksums,
checks idempotent publication, records observations/learning and verifies that
experience reaches the next production. Its images are explicitly neutral test
fixtures, NOT photographs of Luka. Text uses the deterministic local provider;
Telegram uses its explicit fake adapter, not external delivery.

A Chromium browser scenario uses the existing UI to select a character, upload
reference/production files, edit the caption, confirm identity/QC, approve and
download the actual ZIP. It checks that Instagram publication stays disabled.
The existing thematic browser scenario is also exercised.

Each of the five stored libraries is exercised through preparation, approval and
HTTP publication of two linked episodes using the explicit test adapter: future,
computer games, cinema development, Greek pantheon and Thai spiritual world.
Original texts are checked unchanged. This proves compatibility, not renewed
scientific validation of those archived texts or real Telegram delivery.

An actual Luka HTTP run was also started:
`run-9a464d7a-b407-4cad-893b-3d2336c8348f`.
Profile/manifest revision:
`585f7fd30d0e9bddee2ad970ad9960085970b356d8b6ec2503704ccf7aa22d98`.
The plan was persisted. Inventory: 8 references, 0 verified originals available.
It correctly stopped for explicit fictional-context review. No human decisions
or external publications were fabricated. Runtime evidence is stored locally in
`/workspace/content-factory-state/luka-verification.json` and SQLite data under
`/workspace/content-factory-state/production-cycle`.

Completion requires importing a preserved original, owner identity/naturalism
review of Luka's real production image, and an authorized external delivery if
that is to be claimed. An Instagram account/API integration is not required for
this export stage. Do not use the preview as an original or substitute a new face.

## Verification results

- Non-browser suite: 332 passed, 15 skipped, 2 browser tests deselected.
- Chromium: 2 browser scenarios passed (existing thematic and character photo).
- Browser JavaScript syntax and Git whitespace checks passed.
- Existing profile/reference manifests and five library JSON files unchanged.
- GitHub API access through gh is forbidden in this environment; repository Git
  transport is available. Commit/push results are reported separately.

## Research reconciliation

Authoritative Python SHA-256 and ZIP documentation was read from the CPython
3.12 sources:
https://github.com/python/cpython/blob/3.12/Doc/library/hashlib.rst
https://github.com/python/cpython/blob/3.12/Doc/library/zipfile.rst

Classification: SUPPORTS_CURRENT_MODEL — content verification and exported file
packaging reinforce existing provenance and export boundaries; no new ontology
or lifecycle is needed. Official OpenAI image-edit SDK source was also inspected
at https://github.com/openai/openai-python/blob/main/src/openai/resources/images.py;
reference-driven generation is available as an external boundary but was not
implemented or claimed verified without originals/credentials. Direct OpenAI
and Meta documentation pages were blocked by network policy. Selection of a
paid generation provider remains deferred, not inferred from documentation.

Return point: `docs/character/production_cycle.md` and
`tests/test_character_cycle.py`.
