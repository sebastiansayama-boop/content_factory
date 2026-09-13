# 07 — Verification

Validation and error detection against exact revisions.

## Purpose

`07_verification` determines whether a specific revision conforms to defined requirements. It produces findings and evidence for a decision; it does not itself accept or publish the revision.

## Minimum verification record

```text
verification_id
subject_ref
subject_revision_id
verification_type
criteria_refs
input_evidence_refs
checks_performed
findings
failures
warnings
verdict
verifier_or_executor
verified_at
verification_revision
```

The verification record must identify the exact revision checked. Re-running verification against a later revision is a new verification event.

## Verification types

```text
FACTUAL
SEMANTIC
SPECIFICATION
FORMAT
RENDER
TECHNICAL
POLICY
DEPENDENCY
```

Multiple checks may be attached to one verification activity.

## Verdict

Use an explicit result such as:

```text
PASS
FAIL
PASS_WITH_WARNINGS
INCONCLUSIVE
NOT_RUN
```

`INCONCLUSIVE` means the available evidence cannot establish conformity. It must not be silently converted into pass.

## Boundary

```text
production → verification → decision
```

Verification reports whether criteria were met. Acceptance is a separate authority decision. Publication is a separate effect.

## Failure handling

A failed verification should identify:

- exact subject/revision;
- failed criterion;
- observed evidence;
- severity or impact where meaningful;
- required correction or next decision;
- whether re-verification is required.

## Invariants

- Verification is revision-bound.
- Criteria are explicit or traceable.
- Findings are distinguishable from conclusions about future action.
- Verification does not grant acceptance or publication authority.
- Previous verification results remain historical evidence even when superseded by a new verification.

## Completion criterion

A verification record is complete when another operator can determine exactly what revision was checked, against which criteria, with what findings and what verdict.