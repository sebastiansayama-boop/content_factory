# Shot 01 Authored Asset Specification v0 — Inherited Biological Machinery

## Identity

- `asset_spec_id`: `ASSET-SPEC-2026-09-14-001`
- `shot_pack_ref`: `SHOT-PACK-2026-09-14-001`
- `shot_id`: `shot_01`
- `work_item_ref`: `WI-2026-09-13-002-r4`
- `claim_bindings`: `C1`, `C2`, `C3`
- `status`: `AUTHORING_SPECIFIED`
- `execution_authorized`: `NO`

## Purpose

Establish the exact semantic and visual boundary for the first production asset before image generation. The asset must communicate inherited biological commonality without implying that all species share an identical genome, identical anatomy, or a complete known reconstruction of the ancestral state.

## Narration

Different species can look radically different while sharing deep biological machinery inherited from common ancestry.

## Visual concept

A restrained scientific vertical motion-graphic composition. A central abstract biological motif represents a conserved cellular foundation. From this center, several evolutionary branches diverge into visibly different organism silhouettes. Along the branches, selected small molecular/cellular motifs recur, showing continuity of biological machinery while the organism-level forms become increasingly different.

The image should communicate two simultaneous facts: descent can preserve deep biological machinery, while evolutionary divergence can produce substantial differences in outward form.

## Composition

- Vertical 9:16 frame.
- Central biological motif positioned slightly below the upper third.
- Four to five branching evolutionary paths spread downward and outward.
- Each branch terminates in a deliberately different simplified organism silhouette.
- Repeated molecular/cellular motifs appear at corresponding points on multiple branches.
- No text labels are required inside the image.
- Leave clean negative space for subtitles if the renderer overlays them.

## Visual hierarchy

1. shared biological motif;
2. branching ancestry structure;
3. repeated conserved motifs;
4. divergent organism forms.

The hierarchy must make the inheritance relationship legible without making the visual look like a literal reconstructed phylogenetic tree of specific taxa.

## Style

Scientific editorial motion-graphic aesthetic; clean vector-like forms; restrained detail; neutral academic presentation; high legibility at 1080x1920; no photorealistic organisms; no decorative sci-fi effects.

## Image prompt

Create a restrained scientific editorial vertical infographic about inherited biological machinery. Show an abstract central cellular/molecular motif connected to several branching evolutionary paths. Along different branches, repeat a small set of generic cellular and molecular motifs to represent deeply conserved biological machinery, while each branch develops into a visibly different simplified organism silhouette. The visual should communicate common ancestry and conservation at a deep biological level, not identical organisms or identical genomes. Use clean vector-like scientific forms, precise spacing, subtle depth, strong hierarchy, generous negative space for subtitles, 9:16 composition, academically neutral presentation.

## Negative prompt

No DNA double-helix as the sole symbol of all inheritance. No claim of identical genomes. No literal depiction of LUCA. No labeled species genealogy. No statement that every visible molecule is universal. No humanoid AI, robots, brains, futuristic holograms, glowing sci-fi interfaces, fantasy evolution imagery, sensational Darwinian imagery, or photorealistic collage.

## Claim-safety checks

- Must support `C1`: common ancestry explains shared biological features.
- Must support `C2`: some deep biological machinery can be conserved across extant cellular life.
- Must support `C3`: ancestry can supply an inherited biological toolkit.
- Must not imply that all shared features have the same evolutionary depth.
- Must not imply that the ancestral toolkit is completely reconstructed or fully known.
- Must not imply that visible organism similarity is evidence of common ancestry by itself.

## Acceptance criteria

1. A reviewer can identify a shared biological foundation and divergent organism-level forms without reading explanatory text.
2. Repeated motifs appear as selected conserved components, not as a claim that every component is universal.
3. No specific unsupported taxa, dates, genes, or molecular identities are introduced.
4. The visual remains consistent with `C1–C3` and does not introduce claims outside the approved claim graph.
5. Asset can be generated as a single PNG suitable for the active Whisper Studio local-pack contract.

## Asset identity

Planned file: `scene_01.png`

Planned role: visual input for `shot_01` in `SHOT-PACK-2026-09-14-001`.

Current state: specification complete; PNG not yet generated because image-generation capability is temporarily unavailable.
