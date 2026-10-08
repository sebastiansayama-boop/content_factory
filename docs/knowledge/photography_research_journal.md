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

## Checkpoint 007 — multi-source category search, 2026-10-08
- Used external search for hiking, café, friend groups and everyday photos; located 10 additional stable file pages (C015–C024). Candidate queue is now 24 items, all metadata-only, not counted in the 500 analyzed originals.
- Increased distinct known authors in candidate queue (e.g., Altitonantis, Michael Martin, Marta Borchiellini, Bernhard Hanakam, Abe.gova), avoiding single-author saturation.
- Explicit ambiguity: a camera photograph **depicting** a couple taking a selfie is not necessarily the **output** of their phone camera. C023 flagged for capture-type review.
- Wikimedia Commons photo challenge enforces own-work entries and max four entries per author, which may help diversify future sampling, but challenge participation is not evidence of amateur candidness.
- Tried retrieving image pixels through container network; unavailable. The external image results for this query returned unrelated stock-like visuals, so none were promoted to visually inspected status.
- Verified visual-original total remains 10/500. Source: Wikimedia Commons file pages and 2025 February photo challenge.

## Checkpoint 008 — external verification and deduplication (2026-10-08)
- Queried public Commons source records for café/family/outdoor candid categories and opened metadata for multiple files.
- Checked 8 URLs; **7 novel** candidate URLs added after deduplication, 1 already existed. Candidate queue now **31** (metadata-only, not counted toward 500).
- Source diversity: WabbitWanderer (Flickr-origin 2020 garden scene, Panasonic DMC-ZS50), David Atoroyo Sika (South Sudan family outdoor, 2017), Irsam Photography (2020 outing), Linda Bartlett (US NIH archival family), Mike from Vancouver (2013 cafe), and historical unknown amateur photographer. Contemporary and archival examples must not be mixed for style prevalence.
- EXIF observation: WabbitWanderer original lists Panasonic DMC-ZS50, 57.7mm focal length, 1/20 s, ISO400; camera information supports provenance, not claims about the visible image composition.
- **Failed image retrieval test:** container HTTPS request to upload.wikimedia.org failed with ConnectionError. No image pixels inspected in this cycle. The web image lookup surfaced text pages rather than usable images.
- No new schema fields justified. **Verified original image visual reviews remain 10/500**, candidates 31; source card count and visual-review count must not be conflated.
- Next action: prioritize a functioning image-delivery pathway before further metadata-only expansion; once images are visible, annotate scene geometry and compare claims.
- Commit: b11d52e.

## Checkpoint 009 — visual web inspection without downloading, 2026-10-08
- Used image search previews and **looked at eight visible images directly**, across mirror selfies, café groups and hiking. Source/image URLs and concrete image-level observations are stored in `photography_research_visual_web.json` (W01–W08).
- Distinction: visual preview != full-resolution original; commercial marketing/stock-like sources != verified amateur photos. W08 may be generated, so is excluded from any verified real-photo denominator.
- Patterns: mirror selfies show visible phone + reflective environment; café groups may be posed or conversational; outdoor group perspective produces depth-dependent body sizes. These are **qualitative**, not frequency statistics.
- Research method correction: there is no requirement to download original files to inspect available web images; keep visual evidence level explicit. Previous 10 original reviews remain unchanged. Eight new previews do not count toward 500 original-verified images.
- Next question: which of these compositional properties remain when sampling verified user-authored amateur photos rather than marketing imagery?
- Commit: 2493b07.

## Checkpoint 010 — visual comparison of web search image results (2026-10-08)
Eight image previews were returned and directly inspected in this turn, **not verified amateur photographs**:
- X01 https://www.ybibasel.ch/post/hiking-restaurants-in-the-basel-area — three hiking companions in close row, each smiling; arm over shoulder, trekking poles, and background foliage. Commercial/travel source; origin unknown.
- X02 https://events-heinsberg.de/ — hikers walk abreast; coordinated equipment and all-visible faces; marketing/event illustration source; cannot assume natural unstaged capture.
- X03 https://www.rawpixel.com/image/17387036/friends-hiking-nature-trail-together — front-facing smiling walkers, balanced spacing and near-even exposure; stock site. Exclude from amateur prevalence.
- X04 https://www.rawpixel.com/image/17415666/happy-hikers-enjoying-scenic-trail — three people walk close to camera, balanced visible faces; stock site. Exclude from amateur prevalence.
- X05 https://www.visitbergen.com/ting-a-gjore/tekstilindustrimuseet-museumssenteret-i-hordaland-p826873 — family table scene with cups; child and adult interacting; left empty chair is cut by frame; commercial tourism photo.
- X06 https://www.gettyimages.com/ — mother and child at café table, both clearly lit, eye contact, neat separation; stock photography. Exclude from amateur prevalence.
- X07 https://www.gettyimages.com/ — café family around table with different gaze directions and people partially cropped; stock provenance.
- X08 https://www.gettyimages.com/ — group hikers with arm over shoulder and uneven framing; stock provenance.
These are qualitative *visual* comparisons only, not source-level verified amateur records. Marketing images can include believable cropping and mixed gaze: those properties are **not reliable standalone authenticity classifiers**.

Independent source cross-check:
- https://www.flickr.com/photos/31603030%40N08/53261010431/ — photographer Charlie Wambeke describes bright café portrait background due to a window behind subject; concrete causal lighting explanation, but image not pixel-reviewed in this cycle.
- https://commons.wikimedia.org/wiki/File:A_man_and_woman_enjoy_a_sunny_day_at_a_cafe,_taking_a_selfie_together.jpg — file title describes people taking a selfie; EXIF Nikon Z6, 85mm; recording camera differs from depicted selfie device. Do not classify as front-camera output.
- https://www.gettyimages.co.uk/detail/photo/medium-shot-of-happy-family-in-cafe-royalty-free-image/1994970134 — marketed as 'candid' but licensed stock with model releases; label does not prove spontaneity.

**New conclusion:** do not use 'messy framing', 'uneven gaze', or 'ordinary props' as a binary amateur-vs-commercial authenticity test. Both types can contain these. Stronger evidence comes from provenance, creator account, EXIF, and documented shooting context.
**Counters:** 10 prior original-level reviews; 8 new web previews (not added to 500 verified originals). 31 metadata-only candidates remain queued.
**Next question:** compare actual creator-owned casual snapshots against marketed stock using author evidence, then test whether differences survive matching subject, setting, and camera.

## Checkpoint 011 — sequential research, source control and falsification (2026-10-08)
### Cycle A: 12 photographic source records
Verified author, source, license and camera data for 12 Wikimedia Commons file pages; machine-readable audit: `photography_research_source_audit_2026_10_08.json`. Examples: Carlos Ebert/Sony NEX-5 at a café (Flickr), John Hill/Sanyo Hong Kong café, Mahjuja Islam/OPPO A17 coffee scene, Mona Hassan Abo-Abda/Nikon D750 Egyptian tea gathering. This was source inspection, **not** new pixel-level visual inspection.

### Cycle B: temporal duplicate hypothesis
Mahjuja Islam's `Friends + coffee = happiness` (2024-09-03 16:43:23) and `Coffee time with friends` (2024-09-03 16:43:04) are 19 seconds apart, same creator and same 3072x4080 resolution. Hypothesis: correlated shots from one session; do not claim duplicate without image comparison. Counts by source photo and by independent capture session must remain separate.

### Cycle C: title/author sampling confound
`Friends Restaurant.jpg` is a restaurant name; `Friends & Neighbours Cafe` is a business name; `Coffee and friends` metadata indicates cups of coffee. Word "friends" in a title is not evidence of people in the frame. A source file can be self-uploaded yet staged. Sony NEX-5 EXIF focal length 0 mm and f/1 are unreliable for physical lens inference; missing lens metadata is a plausible explanation.

### Cycle D: targeted challenge source check
Opened Commons records for Egyptian folklore photos: `Friends and tea`, `Group family photo`, `Family members`, `Mother and daughter in the farm`. They share photographer Mona Hassan Abo-Abda and several share Nikon D750. Their diversity of subjects does **not** imply diversity of creators; cap creator/session contributions when measuring photographic conventions. One file explicitly records 1/20 s, f/6.3, ISO1800, 32mm, illustrating that low-light gathering photos can use high ISO and slow exposure.

### Cycle E: hypothesis refinement
Provenance plus metadata can validate authorship, capture conditions and correlations, but cannot establish visible framing/pose/lighting without actual image inspection. Do not silently relabel these metadata audits as visual reviews. An authenticity classifier based solely on uneven framing, mixed gaze or everyday props is unsound because staged commercial photos can reproduce these cues.

### State after checkpoint
Original-level visually reviewed photographs: **10/500 (unchanged)**.
Metadata-only candidate queue: **31**.
New source audits in this checkpoint: **12**.
Remaining: 490 original-level reviews. Do not confuse source records, web previews, and original reviews.
Next unresolved test: directly inspect and compare the two 19-second-apart OPPO A17 photos, then evaluate whether they depict the same scene and count independent capture sessions correctly.

## Checkpoint 012 — duplicate-session hypothesis, external source verification (2026-10-08)
- Read the two actual Commons file pages for `Coffee time with friends.jpg` and `Friends + coffee = happiness.jpg` and checked their EXIF against the prior hypothesis.
- Both photographs are credited to Mahjuja Islam, made 2024-09-03 using OPPO A17, with matching dimensions 3072×4080. Times 16:43:04 and 16:43:23 yield **19 seconds** between exposures. These are *distinct files*; no claim that pixels are duplicates.
- `Coffee time with friends.jpg` EXIF: ISO4141, f/1.8, 0.040004 sec, 4.05 mm physical focal length, 28 mm equivalent, no flash, auto white balance, MediaTek camera app. This is a documented phone camera low-light/high-ISO exposure, but noise level is **not visually measured**.
- Hypothesis strengthened: one short capture session rather than independent scenes. To test visual similarity, need actual image pixels or visible preview, not merely file-page metadata. Keep both source files separate but group under one *provisional* capture-session ID.
- Additional source contrast: `Friends and tea.jpg` is self-uploaded 2019 Egypt, Nikon D750, 1/20 sec, f/6.3, ISO1800, 32 mm. `Friends talking over tea (Unsplash).jpg` is credited to Matthew Henry, Canon 5D Mark III, 50 mm, ISO100, 1/4000 sec. These illustrate very different capture regimes for similar text-described social scenes, not measured visual distributions.
- **Counter integrity:** 10 legacy original visual reviews, 0 new pixel-confirmed originals this checkpoint. This cycle did not satisfy the 500-photo visual target.
- Sources: https://commons.wikimedia.org/wiki/File:Coffee_time_with_friends.jpg ; https://commons.wikimedia.org/wiki/File:Friends_%2B_coffee_%3D_happiness.jpg ; https://commons.wikimedia.org/wiki/File:Friends_and_tea.jpg ; https://commons.wikimedia.org/wiki/File:Friends_talking_over_tea_(Unsplash).jpg
