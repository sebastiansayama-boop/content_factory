# 28 — Project Operating Memory

Status: `ADOPTED / OPERATING MODEL`

This document defines how the repository preserves not only the current system model, but also the project experience required to continue work after a context switch, branch change, completed experiment, failure, or return to a parked direction.

## 1. Purpose

The repository must preserve four different things without collapsing them into one:

```text
CURRENT STATE
PROJECT DIRECTION
EVIDENCE / HISTORY
REUSABLE EXPERIENCE
```

The goal is not to create a large documentation system. The goal is to make the project reconstructable and returnable.

## 2. Semantic layers

The operating memory is represented through existing repository zones and documents:

```text
PROJECT MAP
    ↓
CURRENT CHECKPOINT
    ↓
QUESTION / UNKNOWN
    ↓
RESEARCH / EXPERIMENT / IMPLEMENTATION
    ↓
EVIDENCE
    ↓
INTERPRETATION
    ↓
LESSON
    ↓
KNOWLEDGE CANDIDATE
    ↓
VALIDATION / APPLICABILITY
    ↓
REUSABLE KNOWLEDGE
    ↓
RETRIEVAL
    ↓
APPLICATION / DECISION
    ↓
CHANGED WORK / EXECUTION
    ↓
OUTCOME
    ↓
EVALUATION
    ↺ RETAIN / REVISE / SUPERSEDE / REJECT / SCOPE
```

These are semantic roles, not mandatory folders.

Existing repository zones remain authoritative for their respective information types:

- `00_inbox/` — incoming material and classification;
- `01_observation/` — observations and externally grounded signals;
- `02_memory/` — durable reusable information;
- `03_working_context/` — bounded work-item context;
- `04_reasoning/` — evidence, interpretation and reasoning;
- `05_decision/` — explicit decisions and authority;
- `06_production/` — production execution and outputs;
- `07_verification/` — revision-bound verification;
- `08_effects_feedback/` — effects, feedback and external boundaries;
- `09_learning/` — interpretation of experience and promotion candidates;
- `10_records/` — durable history and provenance.

No new top-level `knowledge/`, `mechanisms/`, or `evidence/` folder is required merely to express this model. The existing zones already provide safer semantic boundaries.

## 3. Provenance chain

Material project knowledge should be reconstructable through a provenance chain:

```text
SOURCE / CASE / OBSERVATION
        ↓
RESEARCH OR EXPERIMENT
        ↓
EVIDENCE
        ↓
INTERPRETATION
        ↓
LESSON / LEARNING CANDIDATE
        ↓
VALIDATION / APPLICABILITY
        ↓
KNOWLEDGE
        ↓
RETRIEVAL / APPLICATION
        ↓
DECISION
        ↓
IMPLEMENTATION / PROCESS CHANGE
        ↓
OBSERVED RESULT / EXTERNAL OUTCOME
        ↓
EVALUATION OF KNOWLEDGE
```

The chain is not a claim that every item must have every stage. It is a reconstruction pattern for material conclusions.

Evidence remains distinct from knowledge. Knowledge remains distinct from decision. A decision remains distinct from implementation outcome. Outcome is evidence about knowledge, not automatic proof that knowledge caused the outcome.

## 4. Real-world mechanisms

When designing a structural mechanism, the repository should prefer adaptation of mechanisms demonstrated in real systems over invention from intuition.

The mechanism record should preserve:

```text
problem_it_solves
source
mechanism
how_it_works
evidence_of_use
applicability_to_factory
limitations
adaptation_decision
confidence
```

A real-world mechanism is evidence for a design option, not proof that the same mechanism is correct for Content Factory.

## 5. Decisions

Durable architectural or operating decisions should remain explicit and reconstructable.

A decision record should preserve at least:

```text
decision
context / problem
options considered
chosen option
tradeoffs
supporting evidence
confidence
status
supersession relationship when applicable
```

A changed decision should supersede the earlier decision rather than silently rewriting the historical rationale.

## 6. Experiments and lessons

Experiments are not documentation theatre. They exist to reduce uncertainty or challenge a model.

The preferred learning transition is:

```text
QUESTION
→ HYPOTHESIS
→ EXPERIMENT / OBSERVATION
→ RESULT
→ EVIDENCE
→ INTERPRETATION
→ LESSON
→ KNOWLEDGE CANDIDATE
→ VALIDATION / APPLICABILITY
→ DECISION
```

Both failure and success are eligible for learning. An unexpected success must be examined rather than automatically treated as a proven recipe.

## 7. Creative knowledge

Creative experience is first-class project knowledge when it affects repeatable work, but it must not be represented as objective fact merely because it was successful once.

Creative records should preserve, where applicable:

```text
creative_question
context
reference_or_input
experiment / treatment
observed_effect
successful_pattern_or_failure
reusable_candidate
uncertainty
examples
supporting_evidence
confidence
```

Examples include visual direction, composition, editorial framing, storytelling structure, prompt patterns, rejected approaches and successful production patterns.

The repository therefore preserves creative experience alongside engineering experience without pretending that aesthetic judgments have the same epistemic status as executable test results.

## 8. Learning-loop control boundaries

External research for Program 1 establishes that the following claims must remain distinct:

```text
knowledge validity
      ≠ applicability
      ≠ retrieval
      ≠ actual use
      ≠ decision impact
      ≠ execution impact
      ≠ external outcome
      ≠ causal attribution
```

A retrieved memory is not evidence that it was useful. A changed decision is not evidence that the decision improved the outcome. A positive outcome is not automatic proof that the memory caused it.

Contradictory evidence enters an evaluation path. It does not automatically invalidate prior knowledge. Knowledge may be retained, revised, superseded, rejected, or restricted in scope depending on evidence and context.

Knowledge-management research also identifies the risk of stale knowledge and competency traps. Therefore deliberate challenge, review and unlearning are part of the learning boundary rather than optional documentation features.

Memory admission is a security/control boundary. External content or retrieved material does not become trusted reusable knowledge merely because it is stored.

The Program 1 evidence synthesis is preserved in `10_records/2026-09-13-learning-loop-program-1-research-synthesis.md` and the corresponding model evolution decision in `05_decision/2026-09-13-program-1-learning-loop-model-evolution.md`.

## 9. Project Direction Map

The Project Direction Map is the navigation layer for the whole project. It prevents the active branch of work from becoming the only remembered branch.

Every material direction should be represented with:

```text
Direction
Goal
Status
Current checkpoint
Proven
Unproven
Research needed
Dependencies
Blocked by
Next legitimate step
Return point
```

Directions may be:

```text
ACTIVE
PARKED
COMPLETED
BLOCKED
SUPERSEDED
```

Parking a direction does not delete its context. Completing a direction does not erase its return point.

The current map is maintained in `docs/29_project_direction_map.md` with a machine-readable projection in `model/project-direction-map.yaml`.

## 10. Current checkpoint

The Project Direction Map answers `where can the project go?`.

A checkpoint answers `where exactly did the project stop?`.

A valid checkpoint must preserve:

```text
repository revision
active direction
current objective
last verified state
known unknowns
uncommitted / pending external steps
next legitimate action
return point
```

The checkpoint must never be reconstructed from conversation memory when the repository can contain it.

## 11. Completion and context transfer

Before leaving a material direction, the assistant must preserve:

```text
what changed
what was learned
what was disproved
what remains unknown
what should not be repeated
what remains to be done
where to return
```

A branch of work is not considered safely parked if only its final conclusion survives while the path, evidence and unresolved questions are lost.

## 12. Operating principle

The repository should behave as project operating memory, not merely as source code plus documentation:

```text
PROJECT MAP
     ↓
CURRENT WORK
     ↓
EVIDENCE / EXPERIENCE
     ↓
KNOWLEDGE
     ↓
DECISION
     ↓
WORK
     ↓
OUTCOME
     ↺
PROJECT MAP
```

The repository remains the durable working model. The chat is the reasoning and control interface. External research is evidence that must be reconciled with the repository rather than copied into it as truth.
