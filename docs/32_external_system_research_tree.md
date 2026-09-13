# Content Factory — External-System Research Tree

## Purpose

This is the current research tree for understanding how Content Factory crosses the boundary of its own information space and interacts with the external world.

It replaces a provider- or GitHub-first framing with a general model. GitHub is a concrete instantiation to be studied only after the generic boundary is understood.

The tree is cumulative and adaptive. Each node may generate child questions. A global question is not closed merely because one implementation works.

## Research depth rule

Every material global question must be decomposed to at least five levels before investigation is considered sufficiently scoped. Additional levels are required when evidence exposes unresolved mechanisms, contradictions, or meaningful boundary conditions.

Research proceeds as:

`Question → Decomposition → Source Map → Evidence → Cross-source comparison → Mechanism reconstruction → Verification → Contradiction analysis → Conclusion → Decision → Derived questions`

## Evidence classes

Use sources according to the question, not by a fixed priority list:

- authoritative protocol/API/specification sources;
- implementation and source-code evidence;
- security and authorization documentation;
- reliability and failure-mode documentation;
- operational evidence and observed system behavior;
- comparative implementations;
- controlled experiments;
- negative evidence and counterexamples.

External sources support a design choice but do not prove local implementation correctness. Local execution/experiment evidence remains the strongest evidence for claims about this repository.

## Tree

### L0 — External world

**Q0. What must Content Factory be able to do to interact with reality outside its own information space?**

This is the root question. The repository boundary is internal; external systems own external state and can independently reject, delay, transform, or accept operations.

### L1 — External systems

**Q1. What is an external system?**

1.1 What state does it own?
1.2 Who defines its mutation rules?
1.3 Which boundary separates its state from factory state?
1.4 Who can independently confirm a state change?
1.5 What makes the system external rather than merely another factory component?

### L2 — External-system classes

**Q2. What classes of external systems must the factory distinguish?**

2.1 Source systems: where information is obtained.
2.2 Execution systems: where operations are performed.
2.3 Publication systems: where artifacts become externally available.
2.4 Transaction systems: where durable business/financial state changes occur.
2.5 Control systems: where permissions, policy, automation, or governance constrain behavior.
2.6 Observation systems: where post-action state or consequences can be independently observed.

Each class must be tested for semantic differences rather than assumed to require a separate implementation primitive.

### L3 — Interaction semantics

**Q3. What kinds of interaction can occur across the boundary?**

3.1 observe
3.2 query
3.3 retrieve
3.4 prepare
3.5 authorize
3.6 execute
3.7 mutate
3.8 publish
3.9 trigger
3.10 observe-after-effect
3.11 reconcile
3.12 recover
3.13 learn

For each interaction ask whether it changes external state, merely reads it, or establishes evidence about a state change.

### L4 — External action

**Q4. What is the generic structure of an external action?**

4.1 intent
4.2 target
4.3 authority
4.4 preconditions
4.5 exact input/revision
4.6 execution request
4.7 external processing
4.8 external effect
4.9 observation
4.10 verification
4.11 consequence

The central boundary is:

`API/request accepted ≠ operation completed ≠ external state changed ≠ desired consequence occurred`.

### L5 — Authority and execution

**Q5. What makes an external operation authorized and attributable?**

5.1 identity
5.2 authority
5.3 scope
5.4 duration
5.5 conditions
5.6 delegation
5.7 revocation
5.8 escalation
5.9 operation identity
5.10 audit evidence

Authority must be contextual and scoped. Capability to call an integration is not itself proof of authority to perform every operation exposed by it.

### L6 — Effect, observation, verification

**Q6. How can the factory distinguish execution from actual external effect?**

6.1 What evidence proves the request was sent?
6.2 What evidence proves the external system accepted it?
6.3 What evidence proves the external resource/state changed?
6.4 What evidence identifies the resulting external object/state?
6.5 What independent observation can confirm the resulting state?
6.6 What evidence is sufficient for each operation class?
6.7 What evidence proves the desired business consequence rather than merely a technical mutation?

### L7 — External state and time

**Q7. How should external state and temporal ordering be modeled?**

7.1 internal state
7.2 external state
7.3 desired state
7.4 observed state
7.5 verified state
7.6 divergence
7.7 staleness
7.8 state before action
7.9 action interval
7.10 state after action
7.11 later consequence

A later observation may invalidate an earlier assumption without changing the historical fact that an operation was attempted.

### L8 — Uncertainty

**Q8. How should uncertain external outcomes be represented?**

8.1 not sent
8.2 rejected
8.3 accepted/executed
8.4 effect confirmed
8.5 observation unavailable
8.6 request outcome unknown
8.7 effect outcome unknown
8.8 consequence unknown
8.9 retry prohibited pending reconciliation
8.10 reconciliation required

`UNKNOWN` is not interchangeable with `FAILED`. The correct boundary must be demonstrated per integration class and operation type.

### L9 — Reliability and recovery

**Q9. What mechanisms are required to operate safely when external systems fail or become ambiguous?**

9.1 retry
9.2 idempotency
9.3 deduplication
9.4 concurrency control
9.5 partial completion
9.6 crash recovery
9.7 orphan detection
9.8 external reconciliation
9.9 compensation where possible
9.10 safe terminal states

Recovery must never fabricate an external result merely because an internal execution record exists.

### L10 — Security and blast radius

**Q10. How should authority and failure impact be contained?**

10.1 least privilege
10.2 credential isolation
10.3 authority isolation
10.4 target isolation
10.5 operation isolation
10.6 tenant isolation
10.7 secret non-propagation
10.8 auditability
10.9 compromise containment
10.10 blast-radius limits
10.11 destructive/irreversible operation boundaries

### L11 — Provenance

**Q11. How can a complete causal/provenance chain be reconstructed?**

11.1 question
11.2 research/evidence
11.3 interpretation
11.4 decision
11.5 WorkItem
11.6 exact output/revision
11.7 authorization
11.8 execution identity
11.9 external identity/effect
11.10 observation
11.11 verification
11.12 consequence
11.13 learning
11.14 derived question

### L12 — Factory integration boundary

**Q12. Where should external-system semantics live?**

12.1 generic external-system contract
12.2 transport
12.3 authentication
12.4 authorization
12.5 protocol
12.6 adapter/connector
12.7 capability semantics
12.8 publisher/effect semantics
12.9 observer semantics
12.10 reconciliation/recovery semantics

The goal is to prevent the factory core from becoming a collection of special cases for individual providers.

### L13 — Generic capability model

**Q13. What is the maximum useful generic capability surface for external systems?**

13.1 read
13.2 inspect
13.3 plan
13.4 authorize
13.5 execute
13.6 observe
13.7 verify
13.8 reconcile
13.9 recover
13.10 learn

Each capability must be justified by a concrete semantic job and evidence that the distinction matters.

### L14 — Concrete system instantiation: GitHub

**Q14. How does one concrete external system instantiate the generic model?**

14.1 GitHub as information source
14.2 GitHub as execution target
14.3 GitHub as publication/coordination system
14.4 GitHub Actions as automation/execution system
14.5 GitHub as observation source
14.6 GitHub governance constraints
14.7 GitHub identity and permissions
14.8 GitHub external object identities
14.9 GitHub state observation
14.10 GitHub-specific failure/recovery behavior

GitHub research begins only after the generic questions above establish what must be proven.

## Proof target

The generic external-system capability is not considered proven until a concrete case can reconstruct:

`Factory intent → authorized execution → external operation → external state changed → independent observation → verification → durable provenance → recovery/reconciliation behavior`

The first concrete target is GitHub, but GitHub evidence must be classified as an instantiation of the generic model rather than silently becoming the model itself.

## Research record requirement

Every material branch must produce a durable record containing at minimum:

- question and decomposition path;
- source map and sources actually consulted;
- evidence collected;
- source reliability/authority assessment;
- contradictions and negative evidence;
- experiment/verification method where applicable;
- observed result;
- inference boundary;
- conclusion and confidence;
- explicit decision or `NO_CHANGE_REQUIRED`;
- repository impact;
- derived questions.

No research conclusion becomes repository truth merely because it is written down. Promotion requires an explicit bridge from evidence to decision and a post-write verification of the resulting repository state.
