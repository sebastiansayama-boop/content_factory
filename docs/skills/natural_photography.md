# Skill: natural photographic generation

Status: experimental skill; not an automated production gate.
Trigger: an AI character photo feels overly synthetic, glossy or staged, or a realistic everyday image is requested.
Goal: produce a plausible photo while preserving character identity.

## Inputs
- Approved identity reference(s), if any; otherwise label identity as candidate.
- Action and setting; time/weather; plausible light sources and room surfaces.
- Camera position/distance, framing and intended capture device.
- Clothing, interaction with objects, and permitted scene variation.

## Procedure
1. Define one ordinary action and why a camera would be present. Do not default to a beauty portrait.
2. Describe the scene geometry and one or more plausible light sources, including bounce/fill when relevant.
3. Define camera position and framing; select phone/other camera only if useful. Avoid invented exact EXIF values.
4. Keep stable identity characteristics explicit; vary pose, expression, clothing and location naturally.
5. Generate **one independent photograph** per test. Collages may serve as moodboards but do not validate independent image consistency.
6. Inspect identity, light/shadow coherence, perspective, exposure, material detail, anatomy/object contact, and behavioral naturalism independently.
7. Record actual failures and the changed variable; revise minimally and rerun. Approve a reference only after human QC.

## QC decision
- Identity: same recognizable face/body? **Not proven** until independently reviewed across images.
- Physical plausibility: coherent light, shadows, reflections, perspective and materials?
- Capture plausibility: credible focus, exposure, processing and framing?
- Behavioral plausibility: action and gaze make sense?
- Technical: anatomy, fingers, objects, backgrounds?
Record each as pass/fail/uncertain with evidence, not a single aesthetic score.

## Observations from Luca exploratory outputs (2026-10-08)
- Generated moodboards and a three-panel everyday-scenes image.
- Subject often remained unusually photogenic and camera-aware even in mundane settings.
- Collage output did **not** establish independent multi-image identity consistency.
- Hypothesis to test: more explicit physical scene/camera constraints and independent single-frame generation reduce perceived synthetic polish. Not yet verified.

## Future considerations (not implementation requests)
- Versioned identity reference set after approval.
- Reusable scene/camera/light templates if multiple real tests justify them.
- Automated visual QC only after manual examples and observed failure modes exist.
- Provider comparisons or fine-tuning only if controlled generation tests reveal a repeatable limitation.

Related: [photography principles](../knowledge/photography.md), [character visual identity](../character/visual_identity.md).
