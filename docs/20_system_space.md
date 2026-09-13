# 20 — System Space

The repository is a bounded model inside a larger Content Ecosystem and Content Factory.

## 1. Nested system model

```text
EXTERNAL WORLD / MARKET
        ↓
CONTENT ECOSYSTEM
        ↓
CONTENT FACTORY
        ↓
REPOSITORY MODEL / CASES / RECORDS
```

The repository should not confuse these boundaries.

## 2. Ecosystem state space

Contains context such as:

```text
strategy
portfolio
objectives
audience context
market signals
product/business context
experience
outcomes
```

## 3. Factory state space

Contains:

```text
work items
inputs
research
knowledge revisions
editorial decisions
specifications
asset revisions
verification results
acceptance decisions
releases
publications
effects
learning candidates
```

## 4. Factory action space

Actions are legitimate only when permitted by current state, dependencies and authority:

```text
capture
classify
research
relate
prioritize
route
reason
draft
produce
verify
accept
release
publish
observe
measure
experiment
learn
update
retire
```

Factory Control chooses or coordinates flow actions; it does not create epistemic truth by itself.

## 5. Semantic coordinates

Every material factory item is navigated through:

```text
SYSTEM LEVEL
OBJECT
REVISION / STATE
EVIDENCE
DEPENDENCIES
AUTHORITY
TIME
```

## 6. Realities to keep separate

```text
OBSERVED REALITY
what was observed externally

REPRESENTED REALITY
what the current knowledge/model says

INTENDED FUTURE
what strategy/decisions propose

COMMITTED HISTORY
what records say happened

UNKNOWN SPACE
what cannot currently be established
```

## 7. Factory control coordinates

For flow management, add:

```text
DEMAND
PRIORITY
QUEUE / WIP
CAPACITY
ROUTE
OWNER
SERVICE EXPECTATION
BOTTLENECK
```

These coordinates describe the state of the work system, not the truth of content.

## 8. Available transition calculation

Conceptually:

```text
NEXT ACTIONS
= f(
  current state,
  work item objective,
  evidence,
  dependencies,
  authority,
  capability,
  capacity,
  constraints
)
```

A file's existence is not evidence that its corresponding action is available.

## 9. Cross-boundary transitions

```text
ECOSYSTEM → FACTORY
strategy / audience / demand becomes bounded content work

FACTORY → EXPERIENCE
accepted release becomes an external delivery

EXPERIENCE → ECOSYSTEM
response/outcome becomes market, audience or business signal

FACTORY → REPOSITORY
state, evidence, decisions and history become inspectable records
```

## 10. System integrity

A material case is navigable when an operator can answer:

```text
What strategic or external context created the demand?
What work item entered?
What was known?
What did the factory decide?
What capability processed it?
What constrained the flow?
What exact revision was verified and accepted?
What release occurred?
What external effect occurred?
What was observed afterward?
What changed in factory or ecosystem state?
```

If these answers cannot be recovered, the problem is a failure of state representation or system boundary definition, not merely documentation quality.
