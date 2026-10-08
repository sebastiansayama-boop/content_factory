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
