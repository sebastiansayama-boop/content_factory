# Blind Inference Comparison 001

## Purpose

Test whether an analyst can identify semantic downstream impact from the changed source and actual artifact text without being given the prior dependency annotations or expected impact result.

## Inputs withheld

The prior dependency map, prior impact analysis, impact-test expectation, lineage file, and prior expected result were not used as analysis inputs.

## Independent result

The manual blind adjudication reproduced the intended core classification:

- SCRIPT-001 → REVIEW
- VIDEO-001 → REVIEW
- SHORT-002 → REGENERATE
- SHORT-001 → KEEP
- SHORT-003 → KEEP

TELEGRAM-001 was classified as KEEP because its wording remains compatible with the revised proposition rather than reproducing the superseded v1 wording.

## What this demonstrates

The test fixture contains enough semantic information in the source versions and artifact text to reason about direct content dependence.

It also demonstrates an important distinction:

- graph reachability alone would mark every downstream object as potentially affected;
- semantic inspection can separate direct dependence from mere downstream ancestry.

## What this does not demonstrate

This is not evidence that the Content Factory can currently perform autonomous semantic inference.

No production inference engine was executed here. The result is a manual blind adjudication designed to validate the test protocol and target output schema.

The next implementation test should run an actual analyzer over the same blind fixture and compare its output against a human-adjudicated reference.

## Terminology guard

The topic in this case is **Thai spirits / phi (ผี): spirit beliefs, spirit houses, offerings, and their relationship with Buddhist practice**.

It is not alcoholic spirits. Any interface or task label that resolves “Thai spirits” as “Thai alcoholic beverages” is a semantic interpretation defect and should be recorded as a separate input-understanding test.
