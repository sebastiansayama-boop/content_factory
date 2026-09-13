# 04 — Decision Points

Information flow и decision flow разделены.

## D1 — Candidate admission

```text
SIGNAL / QUESTION
       ↓
CANDIDATE
       ↓
[ investigate? ]
```

Possible outcomes:

- PROCEED
- HOLD
- REJECT

## D2 — Research sufficiency

```text
RESEARCH
   ↓
KNOWLEDGE
   ↓
[ sufficient for decision? ]
```

Possible outcomes:

- SUFFICIENT
- RESEARCH_MORE
- INCONCLUSIVE

## D3 — Editorial selection

```text
KNOWLEDGE
   ↓
[ produce? ]
```

Possible outcomes:

- PROCEED
- HOLD
- REJECT
- UPDATE_EXISTING

## D4 — Verification

```text
ASSET
   ↓
[ conforms to knowledge + specification? ]
```

Possible outcomes:

- ACCEPT
- REVISE
- RESEARCH_NEEDED
- REJECT

## D5 — Publication

```text
APPROVED ASSET
      ↓
[ publish? ]
```

Possible outcomes:

- PUBLISH
- HOLD
- CANCEL

## D6 — Post-publication change

```text
OBSERVATION / NEW EVIDENCE
          ↓
[ affects existing knowledge or publication? ]
```

Possible outcomes:

- NO_ACTION
- UPDATE_KNOWLEDGE
- REVIEW_PUBLICATION
- REPUBLISH
- RETIRE

## Decision boundary rule

Процесс, который производит информацию, не должен автоматически обладать правом принять решение о следующем значимом состоянии.

Это правило будет пересматриваться только при наличии конкретного контрпримера.
