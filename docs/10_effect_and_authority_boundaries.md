# 10 — Effect and Authority Boundaries

The system distinguishes information production, review, acceptance, and external effect.

## 1. Four boundaries

```text
INFORMATION PRODUCTION
        ↓
REVIEW
        ↓
ACCEPTANCE
        ↓
EXTERNAL EFFECT
```

These are separate authority boundaries.

## 2. Information production

Examples:

```text
Research produces evidence/claims.
Content Design produces a specification.
Production produces an asset.
Observation produces an observed signal.
```

Completion here does not grant approval.

## 3. Review

Review asks whether a result conforms to a declared basis.

Examples:

```text
Asset conforms to specification.
Claims are supported by evidence.
Publication package contains the required revisions.
```

Review produces a result, not an acceptance decision.

## 4. Acceptance

Acceptance answers:

> Do we accept this exact version for the next externally meaningful state?

Acceptance must identify:

```text
object_id
revision_id
review_result_id
evidence_refs
authority
outcome
reason
```

## 5. External effect

An external effect changes a system outside the current information workspace.

Examples:

```text
publish
send
schedule
replace public version
retire public version
```

An external effect must identify the exact accepted revision on which it is based.

## 6. No implicit authority escalation

The following do not imply the next authority:

```text
completed production ≠ verified
verified ≠ accepted
accepted ≠ published
published ≠ learned
learning ≠ knowledge truth
```

## 7. Failure classes

### Information failure

The produced content or knowledge is incomplete, unsupported, contradictory, or malformed.

### Review failure

The result does not satisfy the declared verification criteria.

### Acceptance failure

The result passed formal checks but was rejected by the decision authority.

### Effect failure

The accepted result could not be externally applied, or the external outcome became ambiguous.

Effect failure must not silently revoke the accepted informational state.

## 8. Ambiguous effect

When an external operation has an unknown outcome:

```text
ACCEPTED
   ↓
EFFECT_ATTEMPTED
   ↓
UNKNOWN_EXTERNAL_OUTCOME
```

The system must not automatically retry an effect that may already have occurred.

A separate reconciliation decision is required.

## 9. Authority inheritance is prohibited

Authority does not flow implicitly from one role to another merely because the same person or agent performs multiple roles.

The same operator may hold several roles, but each transition still requires the authority appropriate to that transition.

## 10. Decision record contract

A decision is structurally complete only when it records:

```text
DECISION_ID
DECISION_TYPE
TARGET_ID
TARGET_REVISION
REVIEW_RESULT_ID
EVIDENCE_REFS
AUTHORITY
OUTCOME
EFFECTS_AUTHORIZED
EFFECTS_NOT_AUTHORIZED
REASON
```

## 11. Editorial application

The canonical editorial sequence is therefore:

```text
produce asset
   ↓
verify exact asset revision
   ↓
accept exact asset revision
   ↓
assemble release from accepted revisions
   ↓
authorize publication
   ↓
publish exact release
   ↓
record external effect
```

A channel adapter that changes semantic content after verification reopens verification rather than bypassing it.
