# 05 — Decision

Bounded choices and authority records.

## Purpose

`05_decision` records consequential choices about an identified object, revision, work item or release. A decision is the bridge from analysis to an authorized next action; it is not merely a conclusion in prose.

## Minimum decision record

```text
decision_id
decided_at
decision_type
subject_ref
subject_revision_ref
evidence_refs
reasoning_ref
options_considered
selected_option
rejected_or_deferred_options
authority_ref
authority_scope
authorized_effects
forbidden_or_unauthorized_effects
conditions
actor_or_decider
```

Not every decision needs every optional field, but significant decisions must expose the object/revision, evidence, authority and permitted effects.

## Decision types

```text
PROCEED
HOLD
REJECT
ACCEPT
REVISE
AUTHORIZE_RELEASE
AUTHORIZE_PUBLICATION
RETIRE
UPDATE
CANCEL
```

The type describes the decision; it does not imply that the corresponding action has already occurred.

## Authority boundary

Authority is contextual and scoped.

```text
verification ≠ acceptance
action capability ≠ action authority
acceptance ≠ publication
publication authorization ≠ evidence of outcome
```

If the decision authorizes an external effect, the scope and target must be explicit.

## Allowed exits

A decision may authorize or reject the next stage:

```text
reasoning → decision → production
reasoning → decision → verification
verification → decision → acceptance / revision
acceptance → decision → release / publication
learning → decision → model or knowledge update
```

No stage may infer authority solely from the fact that the preceding stage completed.

## Invariants

- Exact subject and revision are identified.
- Evidence and reasoning are traceable.
- Authority is explicit and scoped.
- Unauthorized effects remain prohibited even if technically possible.
- Superseded decisions remain in history.

## Completion criterion

A decision is complete when another operator can determine what was decided, for which exact object/revision, on what basis, by whose authority and which effects were or were not authorized.