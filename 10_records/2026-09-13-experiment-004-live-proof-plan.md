# Experiment-004 — Live GitHub proof plan

Status: `EXECUTING`

The replacement proof branch exists only to obtain a fresh GitHub Actions execution against the corrected adapter revision after PR #28 was superseded.

## Expected observable chain

```text
Issue #27
  ↓
experiment/004-github-semantic-adapter-proof
  ↓
Pull Request
  ↓
GitHub Actions pytest
  ↓
head revision + CI result + review observation
  ↓
FactoryChangeVerification
```

## Acceptance boundary

A passing workflow proves repository change mechanics and test evidence only. It does not grant Factory semantic acceptance, release authority, publication authority, or external outcome.

## Evidence to record after CI

- replacement pull request number;
- exact head SHA;
- workflow run ID and conclusion;
- test result;
- review state observed;
- adapter interpretation;
- explicit unknowns.
