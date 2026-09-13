# 20 — System Space

The repository is not only a workflow. It is a bounded space of possible information states and authorized transitions.

## 1. System-level abstraction

```text
WORLD
  ↓
PERCEPTION
  ↓
REPRESENTATION
  ↓
MODEL
  ↓
POSSIBILITIES
  ↓
DECISION
  ↓
ACTION
  ↓
CONSEQUENCE
  ↓
OBSERVATION
  ↓
MODEL UPDATE
```

A state describes where the system is.

A transition describes what can happen from that state.

A decision determines which transition is authorized.

## 2. The space is four-dimensional

Every important state can be located by four coordinates:

```text
INFORMATION
What exists or is known?

STATE
What lifecycle condition is it in?

DEPENDENCY
What other things must remain valid?

AUTHORITY
What may legally happen next?
```

A fifth coordinate is useful for navigation:

```text
TIME
What is historical, current, proposed, superseded or unknown?
```

## 3. The system has a state space and an action space

### State space

Contains:

- observations;
- evidence;
- claims;
- knowledge revisions;
- active contexts;
- decisions;
- specifications;
- assets;
- verification results;
- releases;
- publications;
- learning candidates;
- current model;
- historical records.

### Action space

Contains only actions that are legitimate from the current state and authority:

```text
observe
classify
research
relate
reason
propose
approve
reject
hold
produce
verify
accept
publish
retire
learn
update
archive
```

The repository must never infer an available action from the existence of a file alone.

## 4. The current model is a map, not the territory

`model/` describes the current best working model of the system.

It is not the world, the complete evidence base, or the complete history.

Therefore:

```text
WORLD ≠ MODEL
MODEL ≠ MEMORY
MEMORY ≠ HISTORY
HISTORY ≠ AUTHORITY
```

A model change is itself an event that must be explainable by evidence, experiment, case failure or explicit decision.

## 5. The repository contains multiple realities

At any moment the repository may contain:

```text
OBSERVED REALITY
what was actually observed

REPRESENTED REALITY
what the current knowledge model says

INTENDED FUTURE
what decisions propose to do

COMMITTED HISTORY
what the records say happened

UNKNOWN SPACE
what cannot currently be established
```

Confusing these realities is a primary source of system error.

## 6. Decision-making in the space

When asked to perform work, first locate:

```text
CURRENT STATE
TARGET OBJECT
TARGET REVISION
KNOWN EVIDENCE
DEPENDENCIES
AUTHORITY
POSSIBLE NEXT TRANSITIONS
```

Then choose the smallest valid transition.

The default decision function is:

```text
DECIDE = f(state, evidence, dependencies, authority, objective, constraints)
```

It is not:

```text
DECIDE = f(request text alone)
```

## 7. Constraint field

Constraints are part of the state space.

Examples:

```text
unknown factual claim
missing evidence
blocked dependency
expired decision
unaccepted revision
publication already occurred
explicit user boundary
repository scope boundary
```

A constraint can remove transitions from the action space without changing the underlying information.

## 8. Opportunity field

The system should also identify available legitimate transitions, not only blockers.

For a given state:

```text
AVAILABLE
BLOCKED
REQUIRES RESEARCH
REQUIRES DECISION
REQUIRES ACCEPTANCE
REQUIRES EXTERNAL AUTHORITY
UNKNOWN
```

This makes the map operational: it tells the operator not only where the system is, but what can happen next.

## 9. Local map versus global map

A case has a local space:

```text
CASE
 ├── objects
 ├── revisions
 ├── evidence
 ├── dependencies
 ├── decisions
 ├── effects
 └── observations
```

The repository has a global space containing many cases, shared knowledge and the current model.

A local case may change shared memory only through explicit promotion.

## 10. Navigation principle

The operator should move through the repository by semantic coordinates, not filenames:

```text
space
→ object
→ state
→ evidence
→ dependency
→ authority
→ next transition
→ record
```

The file path is chosen after these coordinates are known.

## 11. System integrity condition

The space is considered navigable when an operator can answer, for a meaningful case:

```text
Where are we?
What do we know?
What do we not know?
What versions are current?
What depends on what?
What decisions exist?
What authority exists?
What can happen next?
What already happened?
How do we know?
```

If these answers cannot be recovered, the problem is not merely documentation. It is a failure of system state representation.
