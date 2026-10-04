# Publication text variation matrix

## Decision

Content Factory does not use one fixed writing template per publication.

The deterministic layer fixes constraints: language, length, tone, provenance, forbidden constructions, and factual scope. The model chooses the dominant writing mode from the accepted knowledge.

Default: variation: auto.

An explicit variation remains available when the user or a higher-level editorial rule requests it.

## Matrix

| Mode | Use when | Opening | Movement | Ending |
|---|---|---|---|---|
| scene | concrete moment/place/action/object | scene or action | scene → context → development → meaning | meaning of the scene |
| person | historical figure/participant is central | person + concrete action/decision | person → circumstances → consequences → conclusion | changed understanding |
| contrast | expectation differs from evidence | factual contrast | expectation → fact → reason → conclusion | explain the contrast |
| question | material naturally answers a question | substantive question | question → frame → evidence → answer | direct answer |
| object | object/document/technology/artifact is central | concrete object/property | object → context → significance | return to object with new meaning |
| sequence | facts form temporal/causal chain | key node | node → background → turn → consequence | main turn/consequence |
| myth_fact | evidence supports correcting a real misconception | established representation | representation → verification → correction → conclusion | more precise picture |
| zoom_out | one detail explains a wider process | concrete detail | detail → mechanism → context → meaning | return to detail with new meaning |

## Model decision rule

The model selects exactly one dominant mode when variation=auto.

Selection is based on the strongest factual shape of the accepted knowledge, not on a random rotation and not on a fixed publication template.

The model must not select a mode that requires unsupported facts. It may borrow techniques from another mode when this improves naturalness, but the dominant movement should remain coherent.

Repeated publications should therefore be able to differ in opening type, narrative movement, sentence rhythm, information density, use of contrast/question/scene/person/object, and ending strategy.

The model must preserve claim/evidence scope regardless of the selected mode.

## Deterministic boundary

Code enforces provenance, factual scope, length limits when explicitly requested, prohibited constructions, no em dash, and output validity.

The model decides dominant text mode, exact opening, ordering of supported details, sentence rhythm, transitions, emphasis, and ending.

This separation prevents the variation matrix from becoming another rigid template system.
