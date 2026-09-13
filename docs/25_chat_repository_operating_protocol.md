# 25 — Chat ↔ Repository Operating Protocol

Status: `MANDATORY / GOVERNING PROTOCOL`

This document defines the mandatory interaction protocol between the ChatGPT conversation and the `content_factory` repository. It governs research, repository inspection, model changes, writes, verification and completion reporting.

The protocol applies to every material interaction concerning the repository, its architecture, ontology, processes, operating model, research conclusions or implementation direction.

## 1. Core rule

The chat is not the source of truth for the repository.

The repository is the durable working model. External research is the evidence layer. The chat is the control and reasoning interface that connects them.

```text
USER MESSAGE
    ↓
INTENT CLASSIFICATION
    ↓
REPOSITORY SYNC
    ↓
EVIDENCE / RESEARCH CHECK
    ↓
ANALYSIS
    ↓
DECISION
    ↓
OPTIONAL REPOSITORY CHANGE
    ↓
REPOSITORY VERIFICATION
    ↓
RESEARCH ↔ REPOSITORY CONSISTENCY CHECK
    ↓
COMPLETION REPORT
```

No material repository change is considered complete before the final consistency check.

## 2. Process start: message receipt

Every user message concerning this project begins a new interaction cycle.

The first task is to classify the message into one or more intents:

```text
QUESTION
RESEARCH REQUEST
REPOSITORY INSPECTION
MODEL REVIEW
MODEL CHANGE
DOCUMENTATION CHANGE
IMPLEMENTATION REQUEST
CHECKPOINT / MEMORY REQUEST
STATUS / VERIFICATION REQUEST
NO-CHANGE DISCUSSION
```

If the message is ambiguous, ambiguity must be preserved rather than silently converted into a repository change.

A conversational statement is not an authorization to modify the repository unless the requested action is reasonably explicit.

## 3. Repository sync is mandatory

Before making a material architectural claim or repository change, inspect the current repository state relevant to the question.

Minimum inspection includes:

```text
current README / entry point
current governing rules
current relevant model files
current relevant docs
current machine-readable maps
current status / checkpoint when available
```

The inspection scope expands when dependencies indicate that adjacent models may be affected.

Never rely on remembered repository state when the current repository can be inspected.

Never assume that the last known commit is still current.

## 4. Research gate

External research is mandatory for unresolved structural, architectural, process, organizational, methodological or technology-selection questions.

The minimum research sequence is:

```text
QUESTION
→ identify relevant disciplines / patterns
→ search primary or authoritative sources
→ inspect multiple relevant sources
→ compare findings with current repository model
→ identify agreement / contradiction / gap
→ decide whether the repository model should change
```

Research is not mandatory for purely mechanical operations whose semantics are already established and whose execution does not introduce a new model claim, such as formatting a previously approved document without changing its meaning.

When research is performed, sources must be traceable in the resulting research record or document.

## 5. Research ↔ repository reconciliation

Research must never be copied directly into the repository as truth.

For each material external finding, classify it as:

```text
SUPPORTS_CURRENT_MODEL
CONTRADICTS_CURRENT_MODEL
EXTENDS_CURRENT_MODEL
REVEALS_GAP
NOT_APPLICABLE
UNCERTAIN
```

A repository change requires an explicit bridge from evidence to model decision.

The bridge should answer:

```text
What did the source establish?
What existing repository concept does it affect?
Does it change a boundary, state, relation, process, authority or capability?
What remains unproven?
What repository artifact must change, if any?
```

## 6. Evidence hierarchy

Use the following order when resolving conflicts:

```text
1. Direct executable behavior / verified experiment
2. Current repository contracts and machine-readable models
3. Primary / authoritative external sources
4. Repository architectural synthesis
5. Secondary research / industry practice
6. Analogy / hypothesis
7. Chat intuition
```

A higher-level source must not override direct repository evidence without explicitly identifying why the repository behavior is itself defective or out of scope.

External best practice is not proof that the repository already implements the corresponding property.

## 7. Change classification

Every proposed repository change must be classified before writing:

```text
DOCUMENTATION
MODEL
ONTOLOGY
PROCESS
CONTRACT
IMPLEMENTATION
RECORD / HISTORY
ARCHIVE
```

The smallest sufficient layer must be changed.

Do not modify implementation to solve a documentation problem.

Do not modify ontology to solve a workflow problem.

Do not create a new primitive when an existing primitive can express the requirement without loss of meaning.

## 8. No silent model promotion

The following transitions are forbidden without explicit evidence and a recorded decision:

```text
hypothesis → fact
research finding → repository truth
candidate model → verified model
observation → knowledge
metric → learning
learning → strategy
production result → accepted content
verification → acceptance
acceptance → publication
execution capability → authority
```

The status of a model must remain explicit (`candidate`, `supported`, `verified`, `superseded`, etc., according to the applicable model).

## 9. Repository write gate

A write is permitted only when all of the following are true:

```text
1. The requested change is understood.
2. Current repository state has been inspected.
3. Relevant external research has been checked when the question is structural or unresolved.
4. The change has a defined purpose.
5. The target artifact is identified.
6. The change does not silently invalidate another current model.
7. A verification method exists.
```

If any condition is missing, do not write; identify the missing condition instead.

## 10. Atomicity of conceptual changes

A material model change must update all directly affected representations in the same interaction whenever technically possible.

Typical synchronization set:

```text
governing rules
+ human-readable model
+ machine-readable model
+ README / navigation
+ research record or evidence reference
```

Do not leave a machine-readable map describing one architecture while the governing human-readable document describes another.

If complete synchronization cannot be performed, the repository must explicitly record the inconsistency and the work must not be reported as complete.

## 11. External research record

Material research that affects the repository must be reproducible enough to identify:

```text
research question
sources consulted
key findings
source date / currency when material
agreement with repository
contradictions / unresolved issues
decision taken
repository artifacts affected
```

The research record is evidence, not authority by itself.

## 12. Change execution

When a change is authorized and all gates pass:

```text
READ CURRENT FILE
→ PREPARE COMPLETE NEW CONTENT
→ WRITE TARGET
→ UPDATE DEPENDENT ARTIFACTS
→ VERIFY WRITTEN CONTENT
→ VERIFY COMMIT / revision identity
```

Do not perform destructive replacement of unrelated content.

Do not rewrite history merely to make the model appear cleaner.

Do not claim a write occurred until the repository confirms it.

## 13. Post-write verification

After every material write:

```text
WRITE RESULT
→ FETCH RESULTING ARTIFACT
→ CONFIRM CONTENT
→ CONFIRM REVISION / COMMIT
→ CHECK DIRECT DEPENDENCIES
→ CHECK GOVERNING RULES
→ CHECK RESEARCH CONSISTENCY
```

A successful API write is not sufficient evidence that the conceptual change is correct.

## 14. Research ↔ repository consistency gate

Before closing a material cycle, explicitly compare the changed repository model against the external evidence used to justify it.

The gate must determine:

```text
SUPPORTED
PARTIALLY SUPPORTED
CONTRADICTED
UNRESOLVED
```

If contradicted, the change must be revised or rejected unless a documented scope distinction explains the contradiction.

If unresolved, the repository must preserve the uncertainty.

## 15. Completion criteria

A material repository task is complete only when all applicable conditions hold:

```text
[ ] user intent classified
[ ] current repository state inspected
[ ] relevant external research completed
[ ] evidence reconciled with repository
[ ] change scope decided
[ ] required artifacts updated
[ ] writes confirmed
[ ] dependent artifacts checked
[ ] research ↔ repository consistency checked
[ ] unresolved issues recorded
[ ] final revision / commit identified
```

"I wrote the file" is not a completion criterion.

## 16. Final response contract

The completion response must distinguish:

```text
DONE
WHAT CHANGED
WHAT WAS VERIFIED
RESEARCH CONSISTENCY
WHAT REMAINS UNKNOWN
REVISION / COMMIT
NEXT LEGITIMATE STEP
```

Never report an inference as a verified repository fact.

Never report a research recommendation as an implementation fact.

Never report a repository write as complete without repository evidence.

## 17. No-change cycle

If analysis concludes that the repository should not change, that is a valid terminal outcome.

The cycle ends with:

```text
NO CHANGE
+ reason
+ evidence
+ repository state confirmed
+ unresolved question, if any
```

Research should not be converted into repository churn merely to produce a visible commit.

## 18. Stop conditions

The interaction cycle stops when one of these conditions is reached:

```text
COMPLETED
NO_CHANGE_REQUIRED
USER_DECISION_REQUIRED
INSUFFICIENT_EVIDENCE
RESEARCH_CONFLICT_REQUIRES_RESOLUTION
REPOSITORY_WRITE_BLOCKED
EXTERNAL_EFFECT_REQUIRES_AUTHORITY
```

The assistant must not continue into a consequential next step merely because it is technically possible.

## 19. Strict prohibitions

```text
NO repository change from memory alone.
NO architecture change without repository inspection.
NO unresolved structural change without external research.
NO silent promotion of research to truth.
NO silent promotion of candidates to verified state.
NO claiming completion from an unverified write.
NO hidden repository work reported only as reasoning.
NO mixing current state with historical evidence.
NO using folders as proof of authority.
NO treating a provider/tool as a capability definition.
NO treating execution ability as authorization.
NO treating publication as proof of outcome.
```

## 20. Governing loop

The mandatory chat/repository loop is therefore:

```text
MESSAGE
  ↓
CLASSIFY
  ↓
SYNC REPOSITORY
  ↓
RESEARCH WHEN REQUIRED
  ↓
RECONCILE EVIDENCE
  ↓
DECIDE
  ↓
CHANGE OR EXPLICITLY NO-CHANGE
  ↓
VERIFY
  ↓
RECONCILE AGAIN
  ↓
REPORT
  ↓
STOP
```

This protocol governs future repository interactions unless the user explicitly replaces it with a newer governing protocol recorded in the repository.
