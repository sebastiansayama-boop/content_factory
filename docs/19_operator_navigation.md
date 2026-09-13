# 19 — Operator Navigation Protocol

This document defines how an operator or agent should navigate `content_factory` before making a decision or changing the repository.

## 1. The repository is a navigable state space

Do not begin with the question:

> Which file should I edit?

Begin with:

> What situation are we in, what exists, what is known, what is uncertain, what authority exists, and which transitions are legitimate?

The correct file or folder is a consequence of that answer.

## 2. Entry procedure

Before meaningful work, establish:

```text
SYSTEM STATE
ACTIVE CASE
ACTIVE OBJECTS
CURRENT REVISIONS
KNOWN EVIDENCE
KNOWN DEPENDENCIES
OPEN DECISIONS
CURRENT UNKNOWNS
AVAILABLE ACTIONS
RECENT CHANGES
```

Read the smallest set of repository material needed to establish those facts. Do not reread the entire repository by default.

## 3. Locate the question

Classify the request first.

```text
FACTUAL QUESTION
→ observation / research / memory

STRUCTURAL QUESTION
→ reasoning + model comparison

PROCESS QUESTION
→ processes / transition matrix

AUTHORITY QUESTION
→ decision / rules

PRODUCTION QUESTION
→ specification / production

QUALITY QUESTION
→ verification

CHANGE-IMPACT QUESTION
→ dependency / provenance / records

POST-EFFECT QUESTION
→ effects / observation / learning

REPOSITORY-MODEL QUESTION
→ model + records + recent decisions
```

## 4. Establish object and revision

Never make a significant decision about an unnamed or unversioned mutable object.

Minimum locator:

```text
OBJECT TYPE
OBJECT ID
REVISION
CURRENT STATE
```

If any component is unknown, the next operation should normally be identification, not modification.

## 5. Establish epistemic position

Determine whether the relevant statement is:

```text
OBSERVED
SOURCE-BACKED
DERIVED
INTERPRETED
HYPOTHESIZED
DECIDED
UNKNOWN
```

Do not use a stronger category than the evidence supports.

## 6. Establish authority

Determine what can legitimately happen next.

```text
NO AUTHORITY
→ may inspect or propose

WORK AUTHORITY
→ may transform bounded inputs

REVIEW AUTHORITY
→ may assess conformity

ACCEPTANCE AUTHORITY
→ may accept exact revision

EFFECT AUTHORITY
→ may cause external change
```

Do not infer authority from file ownership, folder location, previous approvals or process completion.

## 7. Choose the smallest legitimate transition

Prefer the narrowest transition that answers the actual question.

Examples:

```text
Need evidence?
→ research only

Need to compare interpretations?
→ reasoning only

Need to choose whether to proceed?
→ decision

Need a concrete artifact?
→ production

Need to know whether it conforms?
→ verification

Need to change the external world?
→ explicit effect transition
```

Avoid broad restructuring when a local evidence-gathering or model update is sufficient.

## 8. Use the space map as a routing table

```text
00_inbox
  → unclassified input

01_observation
  → observed facts/events/signals

02_memory
  → reusable source/evidence/claim/knowledge

03_working_context
  → temporary task state

04_reasoning
  → interpretation, comparison, hypothesis

05_decision
  → authority-bearing choice

06_production
  → concrete representation

07_verification
  → conformity/error assessment

08_effects_feedback
  → external effects and immediate consequences

09_learning
  → interpretation of consequences and adaptation proposals

10_records
  → durable history

model/
  → current system belief

docs/
  → explanation and synthesis

templates/
  → capture contracts

archive/
  → inactive historical material
```

## 9. Before changing `model/`

Do not update the current model merely because an idea is plausible.

Require at least one traceable basis:

```text
external research finding
experiment result
real-case failure or repeated ambiguity
explicit decision
```

For structural changes, prefer multiple independent observations when available.

## 10. Before creating a new folder or object type

Ask:

```text
Is the information recurring?
Does it have a distinct lifecycle?
Does it have a different authority boundary?
Would storing it in an existing zone erase an important distinction?
```

If not, do not create a new top-level zone.

## 11. Before production

Confirm:

```text
editorial decision exists
knowledge revision is identified
specification revision is ready
unknowns are explicit
factual claims have an evidence path
```

## 12. Before verification

Confirm that the verification target is exact:

```text
asset revision
specification revision
knowledge revision
verification criteria
```

A verification result belongs to the exact target it checked.

## 13. Before acceptance

Confirm:

```text
verification result exists
verification target matches the candidate revision
evidence binding is recoverable
acceptance authority is explicit
scope of acceptance is explicit
```

## 14. Before external effect

Confirm:

```text
exact accepted revision or release
external target
explicit publication/effect authorization
no unresolved blocking invalidation
```

## 15. After external effect

Record separately:

```text
what was sent/published
which exact revision
where
when
whether delivery succeeded
what was observed afterward
```

Do not rewrite the accepted artifact to match what happened externally.

## 16. When something upstream changes

Trace forward through dependencies:

```text
changed source/evidence
→ affected claim
→ affected knowledge revision
→ affected decision/spec
→ affected asset/release
→ affected publication
```

Use explicit `depends_on`, `invalidates`, and `impacts` relations.

Do not automatically rewrite downstream outputs. Mark them for review first.

## 17. When uncertain

Prefer explicit unknown over invented certainty.

If the question is structural and unresolved:

```text
RESEARCH
→ COMPARE
→ EXPERIMENT / CASE
→ DECISION
→ MODEL UPDATE
```

## 18. End-of-task check

Before declaring a meaningful task complete, verify:

```text
Did the intended state actually change?
Is the exact revision identifiable?
Is the reason for the change recorded?
Are affected dependencies known?
Did authority stop at the intended boundary?
Are unknowns still explicit?
Can another operator recover the path?
```

A proposed edit without a state change is not a completed system change.
