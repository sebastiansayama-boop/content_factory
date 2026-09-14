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

### shot_01 — Inherited toolkit

Narration intent: Different species can look radically different while sharing deep biological machinery inherited from common ancestry.

Claim bindings: `C1`, `C2`, `C3`.

Visual direction: restrained scientific motion graphic showing a branching evolutionary tree with repeated cellular/molecular motifs persisting across branches; no claim that all visible structures are identical.

### shot_02 — Recurring problems and constraints

Narration intent: Organisms repeatedly face functional and environmental problems, while physics, ecology, development and inherited architecture can constrain accessible evolutionary trajectories.

Claim bindings: `C4`, `C5`.

Visual direction: aquatic locomotion problem represented by flow lines and several independently branching body-plan silhouettes; emphasize a constrained design landscape without depicting one inevitable solution.

### shot_03 — Convergent locomotion

Narration intent: Large distantly related aquatic vertebrates independently evolved a thunniform body plan, illustrating recurrent phenotypic solutions under recurring functional and physical conditions.

Claim bindings: `C4`, `C5`, `C6`.

Visual direction: comparative scientific silhouettes of tuna-like, shark-like and other large cruising vertebrate forms, presented as independent lineages rather than a single ancestry chain.

### shot_04 — Camera eyes and component reuse

Narration intent: Vertebrate and cephalopod camera eyes show organ-level convergence, while similarity at the organ level does not mean every underlying component evolved independently; ancient biological components can be reused.

Claim bindings: `C6`, `C7`, `C8`, `C9`.

Visual direction: split comparison of vertebrate and cephalopod camera-eye architecture, followed by a restrained component/reuse diagram. Explicitly avoid implying identical developmental construction or universal genetic convergence.

## 5. Global visual constraints

- scientific explanatory style;
- no sensational evolutionary claims;
- no deterministic arrows such as `constraint → inevitable solution`;
- no phenotype → ancestry inference;
- no claim that convergent phenotype generally implies convergent genes;
- preserve distinction between organ/phenotype and component/gene levels;
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
