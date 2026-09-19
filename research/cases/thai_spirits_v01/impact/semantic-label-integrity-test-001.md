# Semantic Label Integrity Test 001

## Purpose

Prevent ambiguous user language from becoming executable operation metadata before semantic resolution.

## Case

User input:

> что-нибудь про отношение тайцев к духам

Resolved canonical meaning:

- domain: Thailand
- concept: phi
- script: ผี
- meaning: Thai spirit beliefs, spirit houses, offerings, and their relationship with Buddhist practice
- excluded interpretation: alcoholic beverages

## Invariant

Internal operation names, task types, workflow identifiers, progress labels, and other executable metadata MUST be generated from the resolved canonical meaning, not directly from ambiguous user text.

Required flow:

USER INPUT
→ SEMANTIC INTERPRETATION
→ CANONICAL MEANING
→ OPERATION METADATA

Forbidden flow:

USER INPUT
→ OPERATION METADATA

## Acceptance test

For this canonical case:

1. Generate operation metadata only from the canonical meaning.
2. Assert that metadata refers to phi/spirit beliefs, not alcoholic beverages.
3. If metadata contains terms equivalent to alcoholic beverages (for example: алкоголь, спиртные напитки, alcoholic beverages), classify the result as `SEMANTIC_DRIFT`.
4. `SEMANTIC_DRIFT` blocks execution until semantic interpretation is corrected.
5. Preserve the failed label as evidence; do not silently rewrite it and erase the failure.

## Observed defect

The conversation produced internal/progress wording equivalent to:

> Исследование влияния тайских спиртных напитков

This wording was not found in the Content Factory repository. It is therefore recorded as an observed interface/operation-label defect, not as a repository implementation defect.

## Scope

This test establishes the contract and fixture. It does not claim that the current Content Factory runtime already enforces the guard.

## Next production step

Proceed with the Thai phi case only after the canonical topic is locked:

`Thai Phi (ผี) — Spirit Beliefs & Spirit Houses`

The research phase is considered sufficient for the first production experiment. Further research should be triggered by a concrete factual gap discovered during production or verification.
