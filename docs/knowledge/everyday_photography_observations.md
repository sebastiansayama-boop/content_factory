# Everyday photography: reference survey 001
Date: 2026-10-08
Status: exploratory; source-category inspection, NOT a statistically representative study and NOT a per-image visual audit.

## Purpose
Study ordinary self-portraits and smartphone photography before specifying generation constraints for fictional character Luca. Avoid inferring "amateur" merely from deliberate blur, clutter, or bad lighting.

## Sources inspected (public image collections)
- https://commons.wikimedia.org/wiki/Category:Selfies — multiple categories: setting, posture, facial expression, time, arm extended, mirror; photographic diversity.
- https://commons.wikimedia.org/wiki/Category:Self-portrait_photographs_with_mirror — mirror self-portraits, including different devices and contexts.
- https://commons.wikimedia.org/wiki/Category:Smartphone_selfies — direct phone-selfie examples; very small set in this category.
- https://commons.wikimedia.org/wiki/Category:People_taking_smartphone_selfies — third-party views of selfie-taking; useful for physical camera/arm position, NOT equivalent to the resulting selfie.
- https://commons.wikimedia.org/wiki/Category:Men_taking_smartphone_selfies — men using phones for selfies; may contain posed/public-event photographs.

## Findings, with evidence level
1. FACT (catalog taxonomy): selfie photographs and photographs OF people taking selfies are distinct datasets. Do not use the latter as direct camera-output references.
2. FACT (catalog taxonomy): mirror portraits and extended-arm selfies are separately identifiable capture configurations.
3. HEURISTIC (not validated against a representative sample): the capture mechanism should constrain visible hand/phone, camera height, distance, framing, and gaze.
4. HEURISTIC (not validated): incidental clutter, non-centered framing, and variable lighting may support an everyday snapshot but are neither necessary nor sufficient for authenticity.
5. OBSERVATION (our generated examples): earlier Luca kitchen and outdoor collages appeared unusually polished; one knife exhibited ambiguous structural continuity. The latest selfie/mirror/café collage looked less staged, but a collage does NOT test cross-generation identity consistency.

## Parameters proposed
- capture_mode: front_camera_selfie | mirror_selfie | third_person_phone | timer_phone | other | unknown.
- photographer_relation: self | friend | stranger | unknown.
- camera_support: handheld | surface | tripod | unknown.
- visible_capture_device: true | false | unknown.
- gaze_target: lens | screen | mirror | off_camera | unknown.
- arm_camera_geometry: observable | obscured | not_applicable | unknown.
- framing_causality: plausible | implausible | uncertain.
- reflection_consistency: pass | fail | uncertain | not_applicable.
- occlusion_consistency: pass | fail | uncertain.
- object_continuity: pass | fail | uncertain.
- identity_cross_generation: pass | fail | uncertain | not_tested.

## Research rules
- Record the actual image/file page URL, date, license, visible observation, and uncertainty before claiming image-level evidence.
- Source category alone supports only taxonomy, not image-level claims.
- Do not infer EXIF, focal length, device, or provenance when not published.
- Add new parameters only when a concrete reference or generated failure motivates them.
- Keep generation schema separate from observations and hypotheses; no automatic QC gate without test.
- Archive, never delete, prior repo material.

## Next bounded experiment
Inspect 5 individual public images (2 front-camera selfies, 2 mirror selfies, 1 third-person snapshot) and fill an evidence row per image; then generate one separate Luca photo per capture mode and score physical plausibility and identity across separate runs.

## Reference audit 002 — five individual file pages (2026-10-08)
Scope: file descriptions and EXIF, NOT verified pixel-level inspection. The original 2+2+1 design was not met: search surfaced insufficient verified front-camera outputs. Do not relabel photographs OF selfie-taking as selfies.

| ID | File page | Verified source metadata | Capture role | Caveat |
|---|---|---|---|---|
| R01 | https://commons.wikimedia.org/wiki/File:Selfie_in_the_mirror.jpg | 2010-07-21; own work; CC BY-SA 4.0; 537x768 | mirror selfie | camera geometry not yet inspected |
| R02 | https://commons.wikimedia.org/wiki/File:Man_taking_whole_body_selfie_in_mirror_and_looking_strangely_due_to_status_of_high_concentration.jpg | 2022-09-02; own work; retouched file version in history; 2002x3400 | mirror selfie | published version is edited |
| R03 | https://commons.wikimedia.org/wiki/File:A_femboy_taking_a_mirror_selfie.png | 2023-10-23; own work; CC BY-SA 4.0; 826x1224; description mentions phone, bed, towel, poster | mirror selfie | background details from author description, not independent visual verification |
| R04 | https://commons.wikimedia.org/wiki/File:Selfie_with_phone.jpg | 2022-05-07; own work; CC BY-SA 4.0; 5184x3456; description: person taking selfie at festival | third-person photograph of selfie-taking | NOT a front-camera selfie output |
| R05 | https://commons.wikimedia.org/wiki/File:Man_taking_selfies_in_a_modern_bathroom_mirror_during_the_evening_with_his_smartphone.jpg | 2025-05-27; CC BY 2.0; Nikon Z6 35mm f/1.4 ISO200 1/200 | external camera photographing selfie scene | NOT smartphone output despite title; EXIF explicitly indicates Nikon |

### Evidence-based correction
The title or depiction of someone taking a selfie does NOT identify the recording camera. R05 provides a direct counterexample: a person with a smartphone photographed by a Nikon Z6. Distinguish **depicted_capture_action** from **recording_device** and **output_perspective**.

### New candidate parameters
- recording_device: smartphone_front | smartphone_rear | standalone_camera | unknown.
- depicted_capture_action: self_portrait_in_progress | mirror_self_portrait | none | unknown.
- output_perspective: camera_held_by_subject | mirror_reflection | third_party_camera | unknown.
- postprocessing_disclosed: yes | no | unknown (R02 explicitly has retouch history).
These are observational descriptors; not yet required generation constraints.

### Next verification
Find actual front-camera output files with credible device metadata or source testimony, inspect image pixels, then compare the causal constraints against Luca's separate generated photos. Do not promote a parameter to mandatory without a real failed/passed case.

## Reference audit 003 — verified metadata sample (2026-10-08)
This batch examines file-page descriptions and metadata, not the pixels. 10 new unique file pages, 15 cumulative unique references (R01–R15). All from one hosting platform; NOT 10 independent source platforms/profiles. The goal of 50 images/10 sources remains unmet. Metadata can be inaccurate or altered. Avoid treating filename as camera proof.

| ID | URL | Date | Published metadata | Classification | Evidence | License |
|---|---|---|---|---|---|---|
| R06 | https://commons.wikimedia.org/wiki/File:My_selfie,_July_2017.jpg | 2017-07-04 | own work; smartphone selfie per author | actual selfie output claimed; front camera unverified | author statement | unknown |
| R07 | https://commons.wikimedia.org/wiki/File:Olivia_Arben_selfie.jpg | 2019-10-21 | iPhone XR; 2.87mm f/2.2; ISO200; 1/60s; front camera category | front camera output | EXIF + category | CC BY-SA 4.0 |
| R08 | https://commons.wikimedia.org/wiki/File:Jokowi_selfie_with_Prabowo_and_reporters.jpg | 2019-10-11 | iPhone 7 Plus front camera 2.87mm f/2.2; ISO125 | front camera group selfie output | EXIF | check page |
| R09 | https://commons.wikimedia.org/wiki/File:Selfie_in_a_mirror_2015.jpg | 2015-07-28 | file history: monochrome conversion and white balance correction | mirror selfie; postprocessed | file history | CC BY-SA 4.0 |
| R10 | https://commons.wikimedia.org/wiki/File:Selfie_at_a_mirror_of_the_hotel.jpg | 2025-08-21 | 3072x4096; author own work | mirror selfie | author description | CC0 |
| R11 | https://commons.wikimedia.org/wiki/File:Mirror_selfie_kish.jpg | 2025-08-10 | 607x1080; author own work | mirror selfie | author description | CC0 |
| R12 | https://commons.wikimedia.org/wiki/File:K6ka_mirror_selfie_with_D7100_2020-10-10.jpg | 2020-10-10 | Nikon D7100 35mm f/1.8, mirror self-portrait | mirror selfie using DSLR, NOT smartphone | author description | check page |
| R13 | https://commons.wikimedia.org/wiki/File:Two_middle_school_students_taking_a_mirror_selfie_with_Nokia_3650_early_smartphone_(October_2004_on_Avenue_Pasteur_and_Avenue_Gallieni_in_Courbevoie,_France).jpg | 2004-10 | Nokia 3650; 640x480; author own work | mirror selfie using early camera phone | author description | CC BY 4.0 |
| R14 | https://commons.wikimedia.org/wiki/File:Selfie_of_iPhone_in_Mirror.jpg | 2019-12-16 | phone in mirror; no person | mirror phone reflection, NOT human portrait | author description | check page |
| R15 | https://commons.wikimedia.org/wiki/File:Selfie_Belarusian_scientist_Siarhei_Besarab_CERN_safety_helmet_Science_Gateway_June_2026.jpg | 2026-06-20 | Pixel 8 Pro front camera; source of digital media: Edited using generative AI | front-camera image, generatively edited | EXIF processing disclosure | check page |

### Findings from this batch
- R07/R08: some self-portrait outputs include explicit front-camera device metadata; device attribution is stronger than title alone.
- R12: mirror selfie can be captured on a DSLR; `mirror_selfie` does not imply smartphone.
- R09: a historical selfie can be white-balance corrected or monochrome; `unprocessed` is not a safe default.
- R15: an image captured on a real phone can also be edited with generative AI. Camera provenance and synthetic modification are orthogonal fields.
- R14: a mirrored phone without a human subject must be excluded from the human-portrait evaluation subset.

### Proposed parameters motivated by concrete records
- processing_type: none_reported | conventional_edit | generative_edit | unknown (R09, R15).
- human_subject_present: true | false | unknown (R14).
- recording_device_evidence: exif | author_statement | title_only | unknown (R07, R12).
- device_class and camera_facing should be separate fields (R12).
- reference_selection_status: eligible | excluded | conditional (R14 excluded from human-portrait set).

### Evidence limitations and stopping checkpoint
Completed **15 metadata-audited distinct reference file pages** cumulatively. Pixel-level compositional observations completed: **0**. Independent host platforms: **1**. Do not count these as 15 visually inspected photographs or as 10 independent platforms. Next: pixel inspection, 35 more records, diversification beyond Commons.

## Audit 004 — research loop demonstrated (2026-10-08)
Question raised by previous audit: does a mirror selfie imply a phone camera, and does an actual phone shot imply unedited output?
External checks:
- https://commons.wikimedia.org/wiki/File:Selfie_in_the_mirror.jpg — 2010 mirror selfie; Canon EOS 1000D, 28mm, ISO1600, Adobe Photoshop Elements 2.0. **Correction** to earlier R01: it is NOT evidence of phone photography.
- https://commons.wikimedia.org/wiki/File:Mirror_selfie_by_K6ka_on_December_25_2017.jpg — mirror selfie, Nikon D60, 18mm, ISO1600; Flickr-origin, independent photographer account.
- https://commons.wikimedia.org/wiki/File:Selfie_in_mirror_(41841868062).jpg — iPhone SE, 4.15mm, ISO160, Snapseed; Flickr-origin. Device and conventional editing can coexist.
- https://commons.wikimedia.org/wiki/File:Bad_mirror_selfie_(45523326702).jpg — iPhone SE, 4.15mm, ISO200; Flickr-origin.
- https://commons.wikimedia.org/wiki/File:Mirror_yourself.jpg — Samsung SM-J415GN, 3.6mm, Lightroom Android; phone origin with postprocessing.
- https://commons.wikimedia.org/wiki/File:Mirrorselfieatchibicon.jpg — itel S665L, 4.11mm, ISO2200, Lightroom Android.
- https://commons.wikimedia.org/wiki/File:The_mirror_selfie_(50211731711).jpg — Flickr-origin Oregon DOT; Photoshop CS6 metadata; no trustworthy camera identification from this record alone.

**Results:** 7 additional distinct reference file pages, 22 cumulative metadata-reviewed pages. Pixel-inspected originals: 0. More than one photographer account represented, but still mainly one hosting/index platform and Flickr-sourced mirrors; 10 independently validated source profiles NOT yet demonstrated. Do not mistake number of domains for source independence.

**New question:** how can we tell whether an image was *taken with* a phone versus merely *depicts* a phone? EXIF camera model plus author statement is stronger than title/subject; file-editing software does not automatically imply synthetic pixels.

**Schema decision:** Existing fields `recording_device`, `recording_device_evidence`, `processing_type` already cover the distinction. No new parameter justified in this pass. A genuine closed loop can result in NO schema changes.

**Next iteration:** obtain original-image pixels for at least five eligible real photos, record visible framing, hand/phone location, gaze, crop, illumination, and flag uncertainty. Then seek 28 more records and cross-profile sources. Do not claim visual review until performed.

## Audit 005 — live external search → hypothesis test → repository (2026-10-08)
New file pages from independent web search (not previously in R01–R22):
- R23 https://commons.wikimedia.org/wiki/File:Image_selfie.jpg — iPhone 11 Pro Max; f/2.2, 2.71 mm, ISO640, 1/30s. Phone EXIF does not alone prove which side camera was used.
- R24 https://commons.wikimedia.org/wiki/File:Another_mirror_selfie_(50544326273).jpg — Flickr author tjmills1520; author/source record, but camera model not visible in indexed metadata.
- R25 https://commons.wikimedia.org/wiki/File:Another_mirror_selfie_(50510876573).jpg — another Flickr-origin image; EXIF record lacks camera make/model in indexed excerpt.
- R26 https://commons.wikimedia.org/wiki/File:Phone_and_camera_-_window_reflection_selfie_(28510828738).jpg — window reflection (not necessarily flat mirror); provenance Flickr; geometry remains uninspected.
- R27 https://commons.wikimedia.org/wiki/File:Mirror_selfie,_sink,_Jewel_of_the_South,_French_Quarter,_New_Orleans,_Louisiana,_USA.jpg — photographer Cory Doctorow, Pixel 9a, Flickr original. Capture category: mirror.
- R28 https://commons.wikimedia.org/wiki/File:Museum_Selfie.jpg — iPhone 6, ISO800, 1/17s, museum context.
- R29 https://commons.wikimedia.org/wiki/File:Moss_selfie.jpg — iPhone 11, ISO125, 1/87s.
- R30 https://commons.wikimedia.org/wiki/File:Selfie_at_the_Wikimedia_2016_opening.jpg — iPhone 5s, 1/33s.
- R31 https://commons.wikimedia.org/wiki/File:Selfie_Machine.jpg — iPhone 8 Plus, 1/15s; title alone does not prove selfie output.
- R32 https://commons.wikimedia.org/wiki/File:Front_camera.jpg — iPad mini (5th generation) EXIF; title does not establish whether it shows a camera or is produced by one.

New question tested: is any title containing "front camera" or "selfie" enough to include a record in our portrait-output subset? NO. R32 ambiguous, R31 ambiguous; requires pixel-level inspection and/or author testimony. EXIF lens focal length without model-specific camera specs does not by itself establish front/rear.
Counterexamples: R27 explicitly names a mirror reflection; R26 a window reflection. Treat reflective surface as separate from the generic mirror selfie label.

New candidate parameter: `reflective_surface` = mirror | window | other | none | unknown. This is motivated by R26/R27; remains an optional observation, not QC gate.

Checkpoint: **32 unique metadata-audited source file pages** R01–R32; **0 pixel-level reviews**. Milestone 25 metadata references crossed, but the planned 25-*photo* visual checkpoint is NOT completed. Verified independent profiles target still not counted without deduplication.

## Audit 006 — first direct visual review of public images (2026-10-08)
Method: actual image thumbnails returned by external image search were visually inspected, not original full-resolution pixel files. Mark as `thumbnail_visual_review`, not `deep_original_review`. Third-party sites' subject descriptions do not prove authenticity or provenance.

| Review | Image URL | Observed visible properties | Inference limits |
|---|---|---|---|
| V01 | https://miro.medium.com/v2/resize:fit:2400/2*nCtUdzkXStGo8DbLqs5SFg.jpeg | Man centered tightly head-and-shoulders; patterned tile wall fills background; camera approximately face height; shoulders cut at lower frame. | Whether front camera, timer, or another photographer is unknown. |
| V02 | https://d2g8igdw686xgo.cloudfront.net/99652801_1770182420877188_r.jpeg | Bathroom mirror scene: smartphone visibly held beside face; one arm raised, other supports body at counter; door and towel visible; uneven space left/right. | Image provenance and whether cropped/edited unknown. |
| V03 | https://photos2.spareroom.co.uk/images/flatshare/listings/large/90/25/90256678.jpg | Bathroom mirror image; phone held at upper chest/face level; mirror edge and sinks visible; image includes unused room space and lower foreground counter. | Person's motivation, camera mode, and postprocessing unknown. |
| V04 | https://insideadschool.com/assets/images/IMG_8313-Armando-Rosales-1-scaled.jpeg | Gallery mirror image; phone near face; free hand holds dark garment; head near upper third; large background gallery and floor visible. | Device rear camera is visible but EXIF not checked. |
| V05 | https://storage.googleapis.com/sm-core/profile/3e0fe432-d3dd-4de8-8a52-4901e6fcb685.jpeg | Square close portrait; one forearm reaches toward lower-left edge, consistent with handheld selfie; blank wall and wood at edge. | Arm alone does not prove camera ownership; device unseen. |
| V06 | https://www.mylanguageexchange.com/Uploads/HomePics/4737416.png?rand=0.6595728 | Tight mirror portrait; phone occupies right side, covers portion of shoulder; fingers and phone edges visible; face and phone are both sharp. | Screenshot-style resize; EXIF not established. |
| V07 | https://c.superprof.com/i/a/36002963/15498843/600/20250416171644/form-biology-tutor-with-grade-offering-online-lessons-via-whatsapp.jpg | Tight mirror selfie; blue phone close to face; strong bright reflection/glare at lower phone edge; top decorative element partially cut. | Exact source of glare unknown. |
| V08 | https://www.gettyimages.com/ | Photograph shows a person photographing herself in a mirror and another person photographing her with a larger camera; the foreground device and mirror reflections establish two distinct viewpoints. | Illustrative stock photograph; exclude from ordinary-profile frequency estimates. |

### Pattern checks (small, biased sample; not population rates)
- V02/V03/V04/V06/V07: visible phone and hand placement vary while remaining consistent with mirror-camera geometry.
- V01/V05: camera or phone may be invisible in a close portrait; avoid classifying as definite front-camera selfies solely from appearance.
- V03/V04: unoccupied background and partial foreground objects are ordinary compositional possibilities, not mandatory 'imperfections'.
- V08 and previous Nikon Z6 metadata case: the camera that records the image may differ from a phone depicted inside it.

### New operational distinction
`visual_review_level`: metadata_only | thumbnail_visual_review | original_pixel_review.
This prevents thumbnail inspection from being inflated to original-image review. Keep deep-original counter at zero until full original files have been inspected.

## Audit 007 — verified ORIGINAL image inspection (2026-10-08)
For the first time, full-original image links were opened and image pixels directly visually examined. These are 3 distinct original images; metadata-only count unchanged (source overlaps not yet fully deduplicated).

**O01 — GrumpyGroucho, iPhone SE, 960×1280**
Source: https://commons.wikimedia.org/wiki/File:Selfie_of_iPhone_in_Mirror.jpg
Original: https://upload.wikimedia.org/wikipedia/commons/8/83/Selfie_of_iPhone_in_Mirror.jpg
Observed: Vertical dark restroom scene; bright overexposed phone screen held near center at mid-height; only the person's arm and a narrow strip of checkered sleeve enter from left. Door dominates center background; framed picture at right; paper towels and sink edge at lower/right edges. Light is uneven; reflected phone screen clips to white. No face visible. The arm enters from outside frame, not from below the phone.
Metadata: iPhone SE, 1/20 s, ISO 160, f/2.4, 2.15 mm; CC BY-SA 4.0. This is a reflection image recorded by the iPhone, NOT a portrait of the phone's user. Evidence: full original + author + EXIF.
Modeling implication: a mirror selfie may have **no visible face**; subject visibility must not be assumed. Phone-screen brightness and background luminance can diverge dramatically.

**O02 — Trougnouf, Fujifilm X-E2, 4936×3296**
Source: https://commons.wikimedia.org/wiki/File:Shirtless_man_taking_bathroom_mirror_selfie_with_Fujifilm_X-E2_camera_and_XF18-55mm_lens_(DSCF0902).jpg
Original: https://upload.wikimedia.org/wikipedia/commons/8/80/Shirtless_man_taking_bathroom_mirror_selfie_with_Fujifilm_X-E2_camera_and_XF18-55mm_lens_%28DSCF0902%29.jpg
Observed: Landscape frame, face mostly concealed by the large camera/lens in the central foreground. Both hands hold camera; wood-panel room and slanted ceiling dominate; warm bright overhead light, face in deep shadow; head hair is partially clipped at top. The camera body/lens is much sharper/brighter than the dim facial area. There is no phone.
Metadata: Fujifilm X-E2, 18 mm, f/2.8, ISO 800, 1/60 s, darktable processing, CC BY 4.0. This is direct evidence against 'mirror selfie implies phone' and against 'mirror selfie implies portrait orientation'.
Modeling implication: recording device size and hand grip affect face occlusion; lighting on device and face may be highly asymmetric.

**O03 — Pittigrilli, iPhone 5, 3264×2448**
Source: https://commons.wikimedia.org/wiki/File:Man_photographing_himself_in_hotel_bathroom_with_mirrors_all_around_to_generate_illusion.jpg
Original: https://upload.wikimedia.org/wikipedia/commons/a/a6/Man_photographing_himself_in_hotel_bathroom_with_mirrors_all_around_to_generate_illusion.jpg
Observed: Landscape hotel washroom scene with corner mirrors. Large phone-back shape cuts into far right foreground. Left mirror shows man in profile holding phone; center shows his front reflection; smaller recursively repeated people/phone images recede toward center-right. White sink, faucet and wall socket visible below; straight seams and reflections support multi-mirror geometry. Multiple apparent people are repetitions of ONE subject, not a group photo.
Metadata: iPhone 5, 1/20 s, f/2.4, ISO 50; edited colors/contrast per file history; CC BY-SA 4.0.
Modeling implication: a reflective scene may show multiple instances of the same person and device with consistent geometric recursion. Do not reject duplicate human figures automatically, but verify reflection structure.

**Cross-image findings**
1. Device in frame does not necessarily mean a second camera; mirrored output can include the recording device (O01/O02/O03).
2. Mirror selfie framing may be vertical or horizontal, face fully absent or partially obscured, and include multiple reflections.
3. 'Bad photography' must not be defined as arbitrary defects. Observed clipping, shadow and occlusion each have causal explanations.
4. A reflection-consistency check needs a `mirror_count_or_configuration` observation, but this can initially be a note rather than schema expansion.
5. The sources are hand-picked, not random; no frequency estimates.

Next question: can full-original direct-front-camera portraits be contrasted with these three mirror originals without relying on filenames?
