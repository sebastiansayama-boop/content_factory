# Content Factory Model Dataset v1

Purpose: turn repository evidence into a small, inspectable dataset/evaluation boundary for a future specialized Content Factory model.

This directory is deliberately split into three classes:

- `eval/`: cases used to measure a model against existing repository contracts.
- `training_candidates/`: examples that may become SFT data only after human/data-quality review.
- `rejected/`: repository material that must not be treated as training data.

Repository code, tests, and contracts are evidence of behavior, not automatically examples of good language generation.

## v1 decision

Do not fine-tune yet.

First establish:
1. a deterministic evaluation set;
2. a baseline from an existing model;
3. accepted training examples separated from implementation fixtures;
4. a holdout set not used for training.

This follows current fine-tuning practice: build evals first, start with a small number of high-quality examples, and compare against the base model.

## Dataset schema

Evaluation records use:

`id, task, input, expected, source_refs, tags`

Training candidates will use conversational or prompt/completion format only after acceptance.

Every accepted example must preserve provenance to the repository artifact that establishes the expected behavior.

## v1 scope

Initial scope is not "teach the model everything in the repository". It targets:

- evidence-grounded content planning;
- provenance-preserving editorial transformation;
- publication-rule following;
- content-package planning.

The deterministic runtime remains authoritative for IDs, provenance, lifecycle, validation, approval, and publication.
