# Authored Shot Pack Preparation v0 — What Is Common Across Different Species?

## 1. Identity

- `shot_pack_id`: `SHOT-PACK-2026-09-14-001`
- `work_item_ref`: `WI-2026-09-13-002-r4`
- `production_specification_ref`: `PROD-SPEC-2026-09-14-001`
- `editorial_specification_ref`: `SPEC-2026-09-14-001`
- `claim_graph_ref`: `RG-2026-09-14-001`
- `status`: `PREPARATION_BLOCKED`
- `execution_authorized`: `NO`

## 2. Target

Prepare the authored inputs required by the active Whisper Studio local renderer for a four-shot vertical explanatory video.

The renderer requires one PNG and one WAV per shot. This record defines the authored content plan and provenance boundary; it is not itself an executable local pack.

## 3. Proposed renderer parameters

- `language`: `ru`
- `shots`: `4`
- `duration_seconds`: `25`
- `resolution`: `1080x1920`
- `external_provider_calls`: `NO`

These parameters are proposed for the first production attempt and require execution authorization before rendering.

## 4. Shot plan

### shot_01 — Inherited biological machinery

Narration intent: Different species can look radically different while sharing deep biological machinery inherited from common ancestry. The visual should distinguish shared biological foundations from identical outward form.

Claim bindings: `C1`, `C2`, `C3`.

Visual direction: restrained scientific motion graphic showing a branching evolutionary tree with selected repeated cellular/molecular motifs persisting across branches. Do not label every visible motif as universally identical or imply a complete reconstruction of the ancestral toolkit.

### shot_02 — Recurring problems and qualified constraints

Narration intent: Organisms repeatedly encounter functional and environmental problems. Physical, ecological, developmental and historical factors can constrain or bias accessible evolutionary trajectories, but they do not determine one inevitable outcome.

Claim bindings: `C4`, `C5`.

Visual direction: aquatic locomotion problem represented by flow lines and several independently branching body-plan silhouettes. Emphasize a constrained design landscape without a deterministic `constraint → solution` arrow.

### shot_03 — Convergent locomotion

Narration intent: Large distantly related aquatic vertebrates independently evolved a thunniform body plan, providing a documented example of recurrent phenotypic solutions under recurring functional and physical conditions.

Claim bindings: `C4`, `C5`, `C6`.

Visual direction: comparative scientific silhouettes of tuna-like, shark-like, cetacean-like and ichthyosaur-like large cruising vertebrate forms, presented as independent evolutionary lineages rather than a single ancestry chain. Avoid implying that hydrodynamics alone explains the convergence.

### shot_04 — Camera eyes: convergent organ, mosaic underlying basis

Narration intent: Vertebrate and cephalopod camera eyes are a classic example of organ-level convergence. Their similar function and overall architecture do not mean that every underlying component evolved independently or that the same genetic mechanism produced both eyes. Evidence instead supports a mosaic picture involving conserved/shared genes and molecular systems alongside lineage-specific recruitment, gene duplication, expression changes and other modifications.

Claim bindings: `C6`, `C7`, `C8`, `C9`.

Visual direction: split comparison of vertebrate and cephalopod camera-eye architecture, followed by a restrained component-level diagram with two categories: shared/conserved molecular resources and lineage-specific recruitment/modification. Do not depict a one-to-one identical gene set, complete independence, or identical developmental construction. citeturn0search0turn0search4turn0search5

## 5. Global visual constraints

- scientific explanatory style;
- no sensational evolutionary claims;
- no deterministic arrows such as `constraint → inevitable solution`;
- no phenotype → ancestry inference;
- no claim that convergent phenotype generally implies convergent genes;
- no claim that every component of a convergent phenotype evolved independently;
- preserve distinction between organ/phenotype and component/gene levels;
- preserve the mosaic basis of the camera-eye example;
- no unsupported labels or factual annotations outside `C1–C9`.

## 6. Required files for executable pack

```text
pack.json
scene_01.png + voice_01.wav
scene_02.png + voice_02.wav
scene_03.png + voice_03.wav
scene_04.png + voice_04.wav
```

The active renderer contract requires PNG visual assets and WAV speech assets inside the pack directory.

## 7. Current blocker

The content factory currently has the semantic production plan, but no authored PNG/WAV files have been created in this repository, and no approved speech-generation capability is active in the referenced renderer.

Therefore the pack cannot honestly be marked executable yet.

Do not substitute the Whisper Studio technical demo fixture: the fixture is explicitly renderer-plumbing evidence, not content-quality evidence.

## 8. Next production gate

Create and inspect the four authored visual assets and four corresponding approved WAV narration assets. Then assemble the executable `pack.json`, verify claim provenance and renderer contract, and request explicit execution authorization.

Production remains blocked until those inputs exist.

## 9. Provenance

- Production specification: `06_production/2026-09-14-commonality-convergence-production-specification-v0.md`
- Editorial specification: `05_decision/2026-09-14-commonality-convergence-editorial-specification.md`
- Claim graph: `04_reasoning/2026-09-14-claim-graph-commonality-convergence.md`
- Renderer contract: `sebastiansayama-boop/whisper-studio/docs/one-command-generator.md`
- External evidence checked for this synchronization: Nature Ecology & Evolution 2025; BMC Ecology and Evolution 2011; Molecular Evidence for Convergence and Parallelism 2015. citeturn0search0turn0search4turn0search5
