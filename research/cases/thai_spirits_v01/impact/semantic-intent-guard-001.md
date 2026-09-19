# Semantic Intent Guard 001

## Problem

The user intent in this case is Thai spirits / phi (ผี): supernatural beings, spirit beliefs, spirit houses, offerings, and their relationship with Buddhist practice.

The English word "spirits" is ambiguous. It can refer to supernatural spirits or alcoholic beverages.

During the working session, an interface/status description rendered the topic as “Thai alcoholic beverages”. The repository content itself remained correctly scoped to phi and spirit-house practices.

## Requirement

The Content Factory must resolve ambiguous user language before research and production:

USER INTENT → SEMANTIC INTERPRETATION → CONFIRMED TOPIC → RESEARCH

The canonical topic for this case is:

Thai spirits / phi (ผี) — Thai spirit beliefs, spirit houses, offerings, and their relationship with Buddhist practice.

Excluded interpretation:

Thai alcoholic beverages.

## Acceptance criteria

1. A task label must preserve the confirmed semantic sense, not only the ambiguous English keyword.
2. Research queries must use disambiguating terms such as phi, spirit house, spirit beliefs, or Buddhist practice when this meaning is intended.
3. A conflicting interpretation must be surfaced rather than silently propagated.
4. The ambiguity test must be retained as evidence; do not delete the failed or misleading label.
5. No production execution should occur when the semantic topic is unresolved.

## Status

Observed defect in interface/task wording; repository content is correctly scoped.

This is a test requirement, not yet an implemented runtime capability.
