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
