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
