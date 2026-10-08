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
