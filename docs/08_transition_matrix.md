# 08 — Transition Matrix

The transition matrix defines which state changes are allowed, what must be known before the transition, and what authority is required.

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
| CANDIDATE | admit | RESEARCH_REQUIREMENT | decision rationale | Candidate authority |
| CANDIDATE | hold | CANDIDATE/HOLD | reason | Discovery |
| CANDIDATE | reject | REJECTED | reason | Candidate authority |

## 2. Research

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| RESEARCH_REQUIREMENT | begin research | RESEARCH_ACTIVE | research brief | Research |
| RESEARCH_ACTIVE | add findings | KNOWLEDGE_DRAFT | sources/evidence | Research |
| KNOWLEDGE_DRAFT | assess sufficiency | KNOWLEDGE_SUFFICIENT | required claims addressed | Research |
| KNOWLEDGE_DRAFT | continue research | RESEARCH_ACTIVE | explicit gap | Research |
| KNOWLEDGE_DRAFT | declare inconclusive | KNOWLEDGE_INCONCLUSIVE | unresolved questions | Research |
| KNOWLEDGE_SUFFICIENT | material evidence changes | KNOWLEDGE_AFFECTED | new/changed evidence | Research |

`KNOWLEDGE_SUFFICIENT` means sufficient for a specific editorial decision, not globally true or complete.

## 3. Editorial

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| KNOWLEDGE_SUFFICIENT | evaluate opportunity | EDITORIAL_PENDING | knowledge revision + context | Editorial |
| EDITORIAL_PENDING | proceed | EDITORIAL_PROCEED | audience/strategy rationale | Editorial |
| EDITORIAL_PENDING | hold | EDITORIAL_HOLD | reason | Editorial |
| EDITORIAL_PENDING | reject | EDITORIAL_REJECT | reason | Editorial |
| EDITORIAL_PENDING | update existing | EDITORIAL_UPDATE | existing publication reference | Editorial |
| KNOWLEDGE_AFFECTED | review decision | EDITORIAL_PENDING | impact assessment | Editorial |

## 4. Content design

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| EDITORIAL_PROCEED | create production contract | SPEC_DRAFT | exact decision + knowledge revision | Content Design |
| SPEC_DRAFT | satisfy contract | SPEC_READY | selected claims, format, criteria | Content Design |
| SPEC_READY | material upstream change | SPEC_DRAFT | affected dependency | Content Design |

## 5. Production

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| SPEC_READY | produce | ASSET_DRAFT | specification + bound knowledge revision | Production |
| ASSET_DRAFT | finish | ASSET_READY_FOR_VERIFICATION | asset revision | Production |
| ASSET_READY_FOR_VERIFICATION | revise | ASSET_REVISION_REQUIRED | verification feedback | Production |
| ASSET_REVISION_REQUIRED | resubmit | ASSET_READY_FOR_VERIFICATION | new asset revision | Production |

Production does not own factual truth of the source knowledge.

## 6. Verification and acceptance

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| ASSET_READY_FOR_VERIFICATION | inspect | VERIFICATION_PENDING | asset revision + spec revision + knowledge revision | Verification |
| VERIFICATION_PENDING | pass | VERIFIED | verification result | Verification |
| VERIFICATION_PENDING | fail | VERIFICATION_FAILED | failed checks | Verification |
| VERIFICATION_FAILED | revise | ASSET_REVISION_REQUIRED | defect classification | Production |
| VERIFIED | accept | ACCEPTED | exact verification + evidence binding | Acceptance authority |
| VERIFIED | reject | REJECTED | rejection reason | Acceptance authority |
| VERIFIED | request research | RESEARCH_ACTIVE | unresolved knowledge issue | Editorial / Research authority |

`VERIFIED` is a verification result. `ACCEPTED` is an acceptance decision. They are intentionally distinct.

## 7. Release and publication

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| ACCEPTED | assemble release | RELEASE_CANDIDATE | exact accepted revisions | Publication authority |
| RELEASE_CANDIDATE | hold | PUBLICATION_HELD | explicit reason | Publication authority |
| RELEASE_CANDIDATE | publish | PUBLISHED | exact release identity + publication receipt | Publication authority |
| PUBLICATION_HELD | publish | PUBLISHED | still-valid accepted revision | Publication authority |
| PUBLISHED | retire | RETIRED | retirement rationale | Publication authority |

A publication record must identify the exact accepted asset revisions that produced the external effect.

## 8. Observation and learning

| From | Operation | To | Required evidence | Authority |
|---|---|---|---|---|
| PUBLISHED | collect signal | OBSERVED | timestamp + observation source | Observation |
| OBSERVED | interpret | INTERPRETED | observation set + method | Learning |
| INTERPRETED | propose | LEARNING_CANDIDATE | explicit interpretation | Learning |
| LEARNING_CANDIDATE | accept for reuse | LEARNING_ACCEPTED | decision rationale | Editorial / Learning |
| OBSERVED | identify new source | NEW_EVIDENCE | source/evidence reference | Observation / Research |
| NEW_EVIDENCE | assess impact | KNOWLEDGE_UPDATE_REQUIRED | dependency impact | Research |
| KNOWLEDGE_UPDATE_REQUIRED | update | KNOWLEDGE_AFFECTED | changed evidence/claim | Research |

## 9. Forbidden implicit transitions

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

## 10. Revision rule

A material change to a previously accepted or published object creates a new revision.

```text
ACCEPTED revision 2
        ↓ material change
DRAFT revision 3
```

The system must not rewrite revision 2 into revision 3 in place.

## 11. Transition completeness test

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
