# 19 — Operator Navigation Protocol

This protocol defines how an operator or agent navigates `content_factory` before making a decision or changing the repository.

## 1. Start at the correct system level

Do not begin with:

> Which file should I edit?

Begin with:

```text
Is this an ecosystem question?
Is this a Content Factory question?
Is this a repository/model question?
```

Then locate the function involved.

## 2. Entry procedure

Establish:

```text
SYSTEM LEVEL
ACTIVE CASE / WORK ITEM
ACTIVE OBJECTS
CURRENT REVISIONS
KNOWN EVIDENCE
KNOWN DEPENDENCIES
OPEN DECISIONS
CURRENT UNKNOWNS
AVAILABLE CAPABILITIES
AVAILABLE ACTIONS
RECENT CHANGES
CURRENT BOTTLENECKS if known
```

## 3. Classify the request

```text
STRATEGY / ECOSYSTEM
→ intent / audience / portfolio / outcome

INPUT / DEMAND
→ intake / triage / routing

KNOWLEDGE
→ research / evidence / claims / reuse

EDITORIAL
→ objective / priority / decision / specification

PRODUCTION
→ capability / asset / adaptation

QUALITY
→ verification / review / acceptance

DISTRIBUTION
→ release / channel / publication / effect

LEARNING
→ observation / measurement / interpretation / experiment

FACTORY CONTROL
→ WIP / capacity / scheduling / bottleneck / ownership

SEMANTIC / MODEL
→ ontology / identity / revision / dependency / provenance
```

## 4. Establish work item and object identity

For material work, identify both:

```text
WORK ITEM
OBJECT TYPE
OBJECT ID
REVISION
CURRENT STATE
```

A work item is the bounded unit of flow. An asset, decision, knowledge revision or release may be a product of that work item rather than the work item itself.

## 5. Establish epistemic position

Classify relevant statements as:

```text
OBSERVED
SOURCE-BACKED
DERIVED
INTERPRETED
HYPOTHESIZED
DECIDED
UNKNOWN
```

Do not use stronger language than the evidence permits.

## 6. Establish authority

```text
NO AUTHORITY
→ inspect / propose

WORK AUTHORITY
→ transform bounded inputs

REVIEW AUTHORITY
→ assess conformity

ACCEPTANCE AUTHORITY
→ accept exact revision

EFFECT AUTHORITY
→ cause external change

STRATEGIC AUTHORITY
→ change portfolio / objectives / priorities
```

Authority does not come from folder ownership or previous process completion.

## 7. Choose the smallest legitimate transition

Prefer the narrowest operation that answers the actual question.

Do not redesign the factory when an input triage issue is sufficient.
Do not alter ontology when a process rule is sufficient.
Do not add a new subsystem when an existing capability can represent the requirement safely.

## 8. Before changing factory flow

Confirm:

```text
work item exists
objective is known
audience context is known
required knowledge is identified
required capabilities are known
priority is justified
dependencies are known
acceptance criteria exist
```

## 9. Before changing factory control

Confirm:

```text
actual demand exists
current WIP is known
capacity constraint is known or explicitly unknown
routing decision is bounded
ownership is explicit
change targets flow rather than content truth
```

## 10. Before production

Confirm:

```text
editorial decision exists
content specification revision is ready
knowledge basis is identified
unknowns are explicit
required capability is available
```

## 11. Before quality / acceptance

Confirm:

```text
exact asset revision
exact specification revision
verification criteria
knowledge basis
verification result
acceptance authority
```

## 12. Before distribution

Confirm:

```text
exact accepted revision(s)
release composition
channel / target
adaptation status
explicit authorization
blocking invalidations absent or explicitly handled
```

## 13. After external effect

Record:

```text
what was published / delivered
which revision(s)
where
when
whether delivery succeeded
what was observed
```

Do not rewrite the accepted artifact to match the external outcome.

## 14. Learning and ecosystem feedback

Separate:

```text
FACTORY LEARNING
→ knowledge / editorial / production adaptation

ECOSYSTEM LEARNING
→ audience assumptions / product strategy / portfolio / investment
```

Promotion across this boundary requires an explicit decision.

## 15. When something upstream changes

Trace forward:

```text
source / evidence
→ claim
→ knowledge revision
→ editorial decision / specification
→ work item
→ asset revision
→ release
→ publication
→ effect
```

Use `depends_on`, `invalidates`, and `impacts` rather than silent rewriting.

## 16. End-of-task check

```text
Did the intended state actually change?
Is the exact revision identifiable?
Is the work item recoverable?
Are affected dependencies known?
Did authority stop at the intended boundary?
Are unknowns explicit?
Is flow impact understood?
Can another operator reconstruct the path?
```

A file edit without a meaningful system state change is not a completed task.
