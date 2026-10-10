# AI Character Product Contract

This document defines the product-level contract for the first AI creator character.

It intentionally does not prescribe a specific model, provider, LoRA, router, database, scheduler, or multi-agent architecture. Those choices are validated through real generation and publication scenarios.

## 1. Character Identity

The character must remain recognizably the same person across content.

Stable identity:
- face and key facial features;
- hair and general grooming;
- body type and approximate age range;
- distinctive visual characteristics;
- approved identity reference images.

Allowed variation:
- clothing;
- location and environment;
- lighting;
- camera angle and framing;
- natural facial expression and pose;
- context-appropriate styling.

Identity consistency is evaluated independently from overall image quality.

## 2. Personality and Voice

The character has a stable behavioral identity that should remain recognizable across text, images, and video.

Define:
- personality traits;
- interests and recurring topics;
- communication style;
- typical attitude toward the audience;
- boundaries and behaviors that are out of character.

Personality is context for generation, not a separate technical subsystem.

## 3. Content Style

The initial content direction is natural creator/lifestyle content rather than synthetic advertising or generic AI-model imagery.

Content may vary across:
- everyday life;
- city/travel;
- sport and activities;
- home and social situations;
- other formats proven to fit the character and audience.

The subject, scene, and content concept should be separable so that the same character can appear in different contexts without becoming a different character.

## 4. Visual Continuity and Naturalism

Two visual requirements are evaluated separately:

### Identity continuity
The character remains the same person across generations, scenes, angles, and formats.

### Naturalism
The result should look like believable photography/video of a real person rather than a glossy AI fashion render.

Preferred:
- natural skin and facial detail;
- believable asymmetry;
- natural lighting and exposure;
- plausible environments;
- natural clothing, posture, and body language;
- ordinary photographic imperfections when they occur naturally.

Avoid:
- plastic skin;
- excessive beauty retouching;
- artificial symmetry;
- perfect synthetic bodies or poses;
- excessive HDR, bloom, sharpening, or glossy commercial lighting;
- generic AI-model aesthetics.

Do not add artificial defects solely to make an image appear realistic.

## 5. References

Identity references are reusable character assets, not ordinary scene inputs.

The reference set should become the stable visual anchor for future generations. Additional references may be introduced when they materially improve identity consistency or control.

A successful generation may become a new approved reference only after QC.

The exact number and composition of references are not fixed in advance; this will be determined by real generation tests.

## 6. Production and QC

The minimum production loop is:

Generate
→ Visual QC
→ Accept / Regenerate
→ Approve
→ Publish

A technically successful generation is a candidate, not automatically a publishable asset.

QC should at minimum evaluate:
- identity consistency;
- naturalism;
- anatomy and visual defects;
- scene/content fit;
- continuity with the character;
- platform suitability.

## 7. Platform Strategy

Initial public channel:
- Instagram;
- photos and short videos.

Potential monetization channel:
- Fanvue.

The first objective is not scale. It is proving that one character can repeatedly produce believable, consistent, publishable content.

Platform-specific publishing and monetization rules are external constraints and must be checked against current platform policies before production at scale.

## 8. AI Disclosure and Provenance

The character is an AI-created character.

Where a platform requires AI disclosure, the account and/or content must be clearly identified according to that platform's current rules.

If the character is derived from a real person's face or likeness, the project must have the necessary authorization to use that likeness.

Provenance should be retained for the character's source references and generated assets so that the origin of published media can be established.

## 9. Learning Loop

The production system should learn from real outcomes:

Generation
→ ExperienceRecord
→ Retrieval
→ next Generation

Useful signals include:
- ACCEPT;
- EDIT;
- REGENERATE;
- REJECT;
- publication result;
- audience/engagement outcome when available.

Accepted or edited results can become future examples. Rejected results should not be treated as positive examples.

This learning loop is part of the existing Content Factory direction; it does not require a new learning architecture at this stage.

## 10. Current Boundary

The following are intentionally not fixed by this document:
- image model;
- video model;
- LLM;
- provider routing;
- LoRA/fine-tuning;
- character database;
- scheduler;
- agent framework;
- multi-agent orchestration.

Decision rule:

real scenario → generation → factual result → minimal change → rerun → external verification.

Architecture changes are introduced only when an observed problem requires them.
