# 08 — Transition Matrix

The transition matrix defines which state changes are allowed, what must be known before the transition, and what authority is required.

The machine-readable object lifecycles in `model/state-machine.yaml` are the canonical state vocabulary. This document may describe a cross-object operation as one business step, but must not collapse distinct object lifecycles into one state.

A transition is:

```text
FROM STATE
  + INPUTS
  + EVIDENCE
  + AUTHORITY
  → OPERATION
  → TO STATE
```

## 1. Intake

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| SIGNAL | frame question | QUESTION | signal reference | Discovery |
| QUESTION | formulate candidate | CANDIDATE | rationale | Discovery |
| CANDIDATE | admit | ADMITTED | decision rationale | Candidate authority |
| CANDIDATE | hold | HELD | reason | Discovery |
| CANDIDATE | reject | REJECTED | reason | Candidate authority |

Admission closes the candidate lifecycle at `ADMITTED`. If research is required, admission also creates or activates a separate research object at `RESEARCH_REQUIREMENT`; that is a cross-object relation, not a candidate state transition.

## 2. Research

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| RESEARCH_REQUIREMENT | begin research | RESEARCH_ACTIVE | research brief | Research |
| RESEARCH_ACTIVE | establish knowledge sufficiency | SUFFICIENT | sources/evidence and required claims addressed | Research |
| RESEARCH_ACTIVE | declare inconclusive | INCONCLUSIVE | unresolved questions | Research |
| RESEARCH_ACTIVE | continue research | RESEARCH_ACTIVE | explicit gap | Research |
| SUFFICIENT | material evidence changes | AFFECTED | new/changed evidence | Research |
| AFFECTED | reopen | RESEARCH_ACTIVE | impact assessment | Research |
| SUFFICIENT | close | CLOSED | closure rationale | Research |

`SUFFICIENT` means sufficient for a specific editorial decision, not globally true or complete.

## 3. Editorial

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| PENDING | proceed | PROCEED | audience/strategy rationale | Editorial |
| PENDING | hold | HOLD | reason | Editorial |
| PENDING | reject | REJECT | reason | Editorial |
| PENDING | update existing | UPDATE_EXISTING | existing publication reference | Editorial |
| PROCEED | replace decision | SUPERSEDED | replacement decision | Editorial |

## 4. Content design

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| DRAFT | satisfy contract | READY | selected claims, format, criteria | Content Design |
| READY | material upstream change | AFFECTED | affected dependency | Content Design |
| AFFECTED | revise | DRAFT | revision rationale | Content Design |
| READY | create new revision | SUPERSEDED | replacement revision | Content Design |

## 5. Production

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| DRAFT | submit | READY_FOR_VERIFICATION | specification + bound knowledge revision | Production |
| READY_FOR_VERIFICATION | fail verification | REVISION_REQUIRED | verification feedback | Verification |
| REVISION_REQUIRED | revise | DRAFT | defect classification | Production |
| READY_FOR_VERIFICATION | accept exact revision | ACCEPTED | exact verification binding | Acceptance authority |
| READY_FOR_VERIFICATION | reject exact revision | REJECTED | rejection reason | Acceptance authority |

Production does not own factual truth of the source knowledge.

## 6. Verification and acceptance

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| PENDING | pass | PASSED | verification result | Verification |
| PENDING | fail | FAILED | failed checks | Verification |
| PASSED | newer revision verified | SUPERSEDED | newer verification | Verification |
| FAILED | newer revision verified | SUPERSEDED | newer verification | Verification |

`PASSED` is a verification result. `ACCEPTED` is an acceptance decision on an exact revision. They are intentionally distinct object lifecycles.

## 7. Release and publication

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| DRAFT | assemble release | READY | exact accepted revisions | Publication |
| READY | hold | HELD | explicit reason | Publication |
| READY | publish | PUBLISHED | exact release identity + publication receipt | Publication |
| HELD | publish | PUBLISHED | still-valid accepted revision | Publication |
| PUBLISHED | retire | RETIRED | retirement rationale | Publication |
| PUBLISHED | replace with new release | SUPERSEDED | replacement release | Publication |

A publication record must identify the exact accepted asset revisions that produced the external effect.

## 8. Observation and learning

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| RECORDED | interpret | INTERPRETED | observation set + method | Learning |
| INTERPRETED | close | CLOSED | closure rationale | Learning |
| CANDIDATE | accept for reuse | ACCEPTED | decision rationale | Editorial Learning |
| CANDIDATE | reject | REJECTED | rejection rationale | Editorial Learning |
| ACCEPTED | replace learning | SUPERSEDED | replacement learning | Editorial Learning |

Observation and learning are separate lifecycles. A publication becoming externally observable creates an observation object; it does not directly mutate knowledge.

## 9. Evidence

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| OBSERVED | assess relevance | RELEVANT | relevance assessment | Research |
| RELEVANT | source change | AFFECTED | changed source | Research |
| AFFECTED | invalidate | INVALID | invalidation rationale | Research |
| RELEVANT | replace evidence | SUPERSEDED | replacement evidence | Research |

## 10. Forbidden implicit transitions

The following shortcuts are not allowed in the conceptual model:

```text
PRODUCTION → ACCEPTED

VERIFIED → PUBLISHED

OBSERVED → KNOWLEDGE

LEARNING_CANDIDATE → KNOWLEDGE

HISTORICAL_FILE → CURRENT_STATE

NEW_EVIDENCE → RETIRE_PUBLICATION
```

Each requires an explicit intermediate decision or review appropriate to the case.

## 11. Revision rule

A material change to a previously accepted or published object creates a new revision.

```text
ACCEPTED revision 2
        ↓ material change
DRAFT revision 3
```

The system must not rewrite revision 2 into revision 3 in place.

## 12. Runtime boundary clarification

The runtime's `FactoryState` is a bounded orchestration lifecycle and is not a replacement for the object-specific state machines above. It currently models ambiguous execution/publication exceptions as `FAILED`; an `UNKNOWN` outcome state is not implemented. Therefore the repository must not claim ambiguous external outcome recovery as a proven runtime mechanism until that mechanism is explicitly implemented and tested.

## 13. Transition completeness test

A proposed transition is not part of the model until it can answer:

```text
What exact object changes?
Which revision changes?
What inputs are bound?
What evidence supports the transition?
Who has authority?
What state becomes current?
What external effect, if any, occurred?
Can the previous state be reconstructed?
```
