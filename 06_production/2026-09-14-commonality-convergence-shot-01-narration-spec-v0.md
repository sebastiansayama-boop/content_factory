# Shot 01 Narration Asset Specification v0 — Inherited Biological Machinery

## Identity

- `narration_spec_id`: `NARR-SPEC-2026-09-14-001`
- `shot_id`: `shot_01`
- `asset_spec_ref`: `ASSET-SPEC-2026-09-14-001`
- `claim_bindings`: `C1`, `C2`, `C3`
- `language`: `ru`
- `status`: `AUTHORING_SPECIFIED`
- `execution_authorized`: `NO`

## Approved narration text

Разные виды могут сильно отличаться внешне, но при этом иметь глубокие биологические механизмы, унаследованные от общего предка.

## Delivery intent

Calm, precise scientific narration. The sentence should be understandable on first hearing and should not sound sensational or deterministic.

The emphasis should fall on:
- `разные виды` — diversity at organism level;
- `сильно отличаться внешне` — visible divergence;
- `глубокие биологические механизмы` — conserved biological machinery;
- `унаследованные от общего предка` — common ancestry as the explanation for this inherited similarity.

## Speech constraints

- Russian language.
- Neutral adult voice.
- Moderate pace.
- Clear articulation of `биологические`, `механизмы`, `унаследованные`, `общего предка`.
- No dramatic pause suggesting certainty beyond the sentence itself.
- No advertising or trailer-style delivery.
- No added words, interpretation, or unscripted claims.

## Semantic constraints

The narration must not be expanded to claim:
- that all biological features are inherited unchanged;
- that all species share identical genes or genomes;
- that the entire ancestral biological toolkit is known;
- that common ancestry is inferred from outward similarity alone.

## Timing target

Target duration: approximately 6–7 seconds at a natural explanatory pace. Exact WAV duration will be measured after generation and must be recorded in the executable pack metadata.

## WAV acceptance criteria

1. Spoken text exactly matches the approved narration, apart from natural pronunciation and punctuation-related pauses.
2. No missing or substituted words.
3. No clipping or obvious recording artifacts.
4. Voice is intelligible without excessive processing.
5. Measured duration is compatible with the shot timeline after the asset is generated.
6. WAV identity can be bound to `shot_01`, this narration specification, and the eventual production execution.

## Current state

The narration text is specified, but `voice_01.wav` has not been generated. No speech-generation capability is currently authorized for this production, so the missing WAV remains a production blocker.
