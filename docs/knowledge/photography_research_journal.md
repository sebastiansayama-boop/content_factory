# Luca photography research — progress journal
Started: 2026-10-08
Repository branch: feature/experience-retrieval-v1

## Objectives
500 distinct real-photo references; 50 verified independent public creators/profiles; 15 capture categories; 100 image-level visual analyses. These are **targets**, not completed results.

## Checkpoint 000 — baseline
- 22 individual source file pages documented in `everyday_photography_observations.md` (R01–R22).
- 0 originals independently inspected visually at pixel level.
- 0 independently verified author/profile identities counted yet; source metadata alone is insufficient.
- 0 independent Luca generation tests for this research phase.
- Current observation schema: `photography_observation_parameters.json` v0.3.
- Critical lesson: title, depicted device, recording camera, and processing software must not be conflated.
- Known source bias: Commons dominates early sample; expand creator/profile diversity.

## Cycle protocol
At each iteration: choose next unanswered question → find public original → inspect actual image → document visible details separately from EXIF/description → challenge hypothesis with contrary examples → commit evidence → update counters only after verifiable work → choose next question.
If research cannot access original pixels, mark metadata-only and do not increment visual-review count.

## Next task
Pixel-inspect five distinct originals among R01–R22. Record URL, visible framing, phone/hand geometry, gaze, light, clutter, occlusions, EXIF evidence, confidence, license. Then search other public photographer accounts and examine whether selfie perspective predicts crop and arm geometry.

## Progress changes
| Date | Cycle | Metadata records | Pixel reviews | Profiles verified | Change | Commit |
|---|---|---:|---:|---:|---|---|
| 2026-10-08 | Baseline 000 | 22 | 0 | 0 | Created auditable progress tracker and milestone plan | See Git history |

## Checkpoint 001 — audit 005, 2026-10-08
- Executed external search, compared camera metadata across 10 new file pages, and identified window-versus-mirror reflection question.
- References increased from 22 to 32 (metadata level); image-pixel reviews remain 0.
- Added optional `reflective_surface` field to observation schema v0.4.
- Did NOT count ambiguous titles as verified front-camera photos.
- Remaining gap: actual visual inspection; next cycle must focus on pixels rather than accumulating titles.
- Research commits: 5796cf0, 04c8919.

## Checkpoint 002 — audit 006, 2026-10-08
- Searched public image results and visually inspected eight distinct previews (V01–V08) from multiple source websites.
- Recorded observable framing, phone/hand placement, environmental details, and uncertainty per image.
- Updated schema to v0.5 with `visual_review_level`; preview inspections are **not** counted as original-pixel deep reviews.
- Progress: 32 metadata file pages; 8 additional thumbnail visual reviews (overlap with file pages not yet deduplicated); 0 original-resolution deep reviews. Do not add 32+8 as distinct image total.
- Next research question: what changes in framing and reflected geometry between a true mirror-camera output and an external photo depicting someone taking a mirror selfie?
- Commits: 565f675, 16bea76.

## Checkpoint 003 — audits 007–008, 2026-10-08
- Inspected **four full original photographs** (O01–O04) across four distinct credited creators. Three mirror examples, one direct smartphone selfie.
- Findings: camera visibility, portrait orientation, face visibility, and reflection multiplicity are independent variables; all four original images have visible ordinary imperfections with plausible causes.
- EXIF inconsistency in O04 shows why metadata is not infallible.
- Progress: 4/100 deep original reviews; 32/500 previously logged metadata records; 8 preview reviews. These groups have not been fully deduplicated, so no new 500-photo unique-total claim.
- Next cycle: widen beyond selfies into third-person everyday scenes.

## Checkpoint 004 — audit 009, 2026-10-08
- Opened six original image files and directly inspected pixels: posed group portrait, group selfie, candid cafe conversation, backlit silhouettes, coffee still life, and low-res family snapshot.
- **Two misleading filename/title examples:** `Sharing a family dinner` contains no visible dinner; `Friends + coffee = happiness` contains no people. Never auto-label image content from titles.
- Verified original reviews **10/100** (4 earlier + 6 this cycle). Credited original authors represented: 10. Metadata-only pages previously 32; avoid summing until deduplicated.
- Insight: apparent naturalness is caused by actual scene geometry and photographer position, not arbitrary visual errors.
- Commits: 865c8bd, d26d470.

## Checkpoint 005 — 500-photo category matrix and auditable manifest, 2026-10-08
- Researched public category structure: Wikimedia Commons Selfies, People in cafés, Family portrait photographs. These are discovery pools, **not** analyzed photographs.
- Defined 16 non-overlapping primary categories with quotas summing to exactly 500.
- Migrated the ten previously documented original-image reviews O01–O10 into a machine-readable per-photo manifest; no newly inspected pixels in this checkpoint.
- Category progress is **10/500**, and the remainder is 490. Legacy 32 metadata cards and eight thumbnails are not added to the 500 until visually reviewed and deduplicated.
- Category allocation is a sampling plan, not evidence of 500 completed observations.
- Repository files: photography_research_categories.json and photography_research_manifest.json.

## Checkpoint 006 — active external search, 2026-10-08
- Searched for hiking and laptop/café photos. Screened 14 distinct Commons file pages; recorded stable URLs, metadata, author where available, and possible staged-photo bias in `photography_research_candidates.json`.
- Discovered serious author skew: 9/14 candidate records belong to the same photographer (Shixart1985); do not count 9 independent profiles.
- Attempted retrieval of image originals for pixel inspection. This runtime could not resolve Commons via container networking; image search returned no images. **No candidate was falsely promoted to visual-reviewed status.**
- Verified original visual reviews remain 10/500; 14 new metadata-only candidates are held in a separate queue.
- Next work: use an image-capable retrieval route to inspect originals, then move records individually to reviewed manifest and update counters.
