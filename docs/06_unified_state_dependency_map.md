# 06 — Unified State and Dependency Map

This document synthesizes the current `content_factory` model with nine existing repositories:

- `thai-mythology-content-generator`
- `ai-creative-os`
- `whisper-studio`
- `ai-research-radar`
- `telegram_bot`
- `controlled-agent-executor`
- `atlas-records`
- `atlas-workspace`
- `-atlas-agent`

The purpose is not to copy implementation details. It is to determine which state, dependency, evidence, and decision patterns appear reusable across systems and which are specific to execution or production.

## 1. Current Content Factory model

The existing model defines four flows:

```text
SIGNAL FLOW
WORLD → SIGNAL → QUESTION → CANDIDATE

KNOWLEDGE FLOW
SOURCE → EVIDENCE → CLAIM → CONTEXT/RELATIONS → KNOWLEDGE

VALUE FLOW
KNOWLEDGE → EDITORIAL DECISION → CONTENT SPEC → ASSET → PUBLICATION

LEARNING FLOW
PUBLICATION → OBSERVATION → LEARNING → KNOWLEDGE / DISCOVERY / DECISION
```

The current model already separates information flow from decision flow and defines ownership at state boundaries.

The synthesis adds four dimensions that are currently implicit:

```text
IDENTITY
VERSION / STATE
DEPENDENCY
EFFECT BOUNDARY
```

## 2. Unified state model

The combined model is:

```text
INPUT / SIGNAL
      ↓
IDENTITY
      ↓
BOUNDED WORK ITEM
      ↓
VERSIONED INFORMATION STATE
      ↓
OPERATION
      ↓
OBSERVED RESULT
      ↓
REVIEW
      ↓
DECISION
      ↓
EXTERNAL EFFECT
```

History and current state are separate views of the same evolution:

```text
APPEND-ONLY HISTORY
        ↓
CURRENT / DERIVED STATE
        ↓
DECISION RECORD
```

A decision must remain bound to the exact object/version/evidence it concerns.

## 3. Unified editorial dependency graph

The editorial graph should be understood as a dependency graph rather than only a sequence:

```text
SOURCE
  ↓
EVIDENCE
  ↓
CLAIM
  ↓
KNOWLEDGE REVISION
  ↓
EDITORIAL DECISION
  ↓
CONTENT SPECIFICATION REVISION
  ↓
ASSET REVISION
  ↓
VERIFICATION
  ↓
RELEASE / PUBLICATION UNIT
  ↓
PUBLICATION
  ↓
OBSERVATION
  ↓
LEARNING / NEW EVIDENCE
  ↺
```

A concrete trace can therefore be:

```text
Publication P7
  → Asset A12 revision 3
  → Content Specification CS4 revision 2
  → Editorial Decision D9
  → Knowledge K8 revision 5
  → Claim C17
  → Evidence E17
  → Source S03
```

This is stronger than provenance alone because it can also express impact when an upstream dependency changes.

## 4. Three different relations that must not be collapsed

### Provenance

Answers:

```text
Where did this come from?
```

Example:

```text
SLIDE 4 → CLAIM C17 → EVIDENCE E17 → SOURCE S03
```

### Dependency

Answers:

```text
What depends on this?
```

Example:

```text
CLAIM C17
  ↓
KNOWLEDGE K8
  ↓
SPEC CS4
  ↓
ASSET A12
  ↓
PUBLICATION P7
```

### Invalidation / impact

Answers:

```text
What must be reconsidered if this changes?
```

Example:

```text
SOURCE S03 becomes unreliable
        ↓
EVIDENCE E17 affected
        ↓
CLAIM C17 affected
        ↓
KNOWLEDGE K8 affected
        ↓
ASSET A12 requires review
        ↓
PUBLICATION P7 requires review
```

These relations are currently only implicit in `content_factory` and should be treated as separate concepts.

## 5. Repository pattern matrix

| Pattern | Source repositories | Status in Content Factory | Classification |
|---|---|---|---|
| Current state separated from historical material | Thai Mythology, AI Creative OS, Whisper Studio, Radar, Workspace | Partly explicit via `working model`; history not yet formally separated | Universal repository pattern |
| Explicit exclusions / non-dependencies | Thai Mythology, AI Creative OS, Telegram Bot, Whisper Studio, Workspace | Not explicit | Universal boundary pattern |
| Stable identity for work item | Controlled Executor, Atlas Agent | Not yet explicit | Universal control pattern |
| Durable state before later effects | Controlled Executor | Not yet explicit | Universal for stateful workflows |
| Exact version bound to review/acceptance | Controlled Executor, Atlas Agent, Atlas Records | Missing | Universal for mutable information |
| Append-only history | Radar, Atlas Records, Atlas Agent | Conceptually implied, not modelled | Universal history pattern |
| Derived latest state separate from history | Radar | Missing | Universal state projection pattern |
| Review separate from acceptance | Controlled Executor, Whisper Studio, Atlas Agent, Atlas Records | Decision gates exist, but boundary is compressed | Universal governance pattern |
| Decision bound to exact evidence | Atlas Records, Controlled Executor | Traceability exists but binding is incomplete | Universal evidence pattern |
| External effect separated from internal decision | Atlas Agent, Controlled Executor | Publication exists, but effect authorization is underdefined | Universal effect boundary |
| Re-observation of result instead of trusting completion | Controlled Executor | Not modelled | Execution-specific but useful for production verification |
| Leases / reclaim / cancellation | Controlled Executor | Not relevant to editorial semantics yet | Execution-specific |
| Multi-asset release / batch publish | Sanity-style external reference, not from nine repos | Not present | Production-specific candidate |
| Renderer/technical result vs human/product acceptance | Whisper Studio | Missing explicit distinction | Editorial/production pattern |
| Historical snapshot ≠ current compatibility | Atlas Workspace | Missing explicit epistemic rule | Universal research/reproducibility pattern |
| Human review outcome stored append-only | Radar, Atlas Records | Learning exists, review outcome not explicit enough | Universal governance pattern |
| Runtime independence between repositories | All nine, especially archived projects | Partly represented outside Content Factory | Universal dependency-management pattern |

## 6. Patterns classified as universal

The following patterns recur independently of whether the repository is an execution engine, research system, content system, or archived prototype.

### U1 — Current state is not history

A historical file, snapshot, result, or phase must not silently become the current state.

Required distinction:

```text
HISTORY
CURRENT STATE
```

### U2 — Identity is separate from content

A result should be identifiable independent of its textual representation.

```text
ASSET_ID
VERSION
CONTENT
```

### U3 — Version is part of meaning

Acceptance, verification, or publication of mutable information must target an exact revision.

```text
ACCEPT(asset_id, revision_id)
```

not merely:

```text
ACCEPT(asset_id)
```

### U4 — Decision is not information

A process may produce evidence or a result without acquiring authority to approve the next state.

### U5 — Review is not acceptance

Passing a check, completing a task, or producing a result does not imply human or product acceptance.

### U6 — Evidence and decision must remain linked

A durable decision must preserve the evidence and exact state on which it was made.

### U7 — External effect is a separate boundary

Saving, generating, accepting, and publishing are different operations and must not collapse into one state transition.

### U8 — Dependencies must be explicit

A repository, document, claim, source, or artifact should not become a dependency merely because it exists or was historically related.

### U9 — Historical material must not silently reactivate

Old code, old process, old provider assumptions, and old decisions require explicit reactivation.

### U10 — Unknown is a legitimate state

A missing fact or unresolved dependency should remain explicitly unknown rather than being filled by inference.

## 7. Patterns classified as editorial-general

These are likely to apply to a broad content/knowledge production system, but they are not universal to every software workflow.

### E1 — Knowledge is a reusable layer

Claims/evidence may support multiple editorial decisions and multiple assets.

### E2 — Asset is a projection, not source of truth

Production renders selected knowledge for a specific audience, objective, and channel.

### E3 — Content specification is a contract

Production should consume a bounded specification rather than reconstructing intent from raw knowledge.

### E4 — Research sufficiency is decision-relative

"Sufficient research" only has meaning relative to the decision the research must enable.

### E5 — Observation and interpretation should be separated

Observed performance, correction, or new evidence should not automatically become learning or knowledge.

### E6 — Editorial release may contain multiple dependent assets

A publication unit may represent a coherent set of related outputs rather than one asset.

## 8. Patterns classified as execution-specific

These come primarily from `controlled-agent-executor` and parts of Atlas.

### X1 — Lease / heartbeat / reclaim

Useful when work is delegated to a worker that can disappear or become ambiguous.

Not a fundamental editorial primitive.

### X2 — Exact process argument vectors

Important for safe command execution. Not inherently required by the knowledge model.

### X3 — Detached worktree isolation

Execution isolation mechanism, not an editorial state concept.

### X4 — Crash recovery of operating-system work

Necessary for bounded execution but downstream of the content model.

### X5 — Re-observation of physical effects

Critical when a worker can mutate a filesystem or external system. Less fundamental for pure information transformation.

## 9. Patterns classified as production-specific

### P1 — Channel adaptation

May modify representation for a concrete channel and therefore may require re-verification if semantics change.

### P2 — Publication authorization

Relevant once the system can make an external publishing effect.

### P3 — Release / batch publication

Relevant when several assets form one externally visible editorial unit.

### P4 — Render validation

Checks layout, media, timing, dimensions, encoding, etc. These are production-specific validation dimensions.

## 10. State model proposed by the synthesis

The minimum conceptual state machine should be extended to distinguish creation, observation, review, acceptance and effect:

```text
DISCOVERY
   ↓
CANDIDATE
   ↓
RESEARCH REQUIREMENT
   ↓
RESEARCH
   ↓
KNOWLEDGE REVISION
   ↓
EDITORIAL DECISION
   ↓
CONTENT SPEC REVISION
   ↓
ASSET REVISION
   ↓
VERIFICATION RESULT
   ↓
REVIEW / ACCEPTANCE
   ↓
RELEASE CANDIDATE
   ↓
PUBLICATION EFFECT
   ↓
OBSERVATION
   ↓
LEARNING / NEW EVIDENCE
   ↺
```

Important distinction:

```text
VERIFICATION RESULT
        ≠
ACCEPTANCE
        ≠
PUBLICATION
```

And:

```text
KNOWLEDGE REVISION
        ≠
KNOWLEDGE TRUTH FOREVER
```

## 11. Required dependency semantics

For every significant derivative object, the conceptual model should eventually support:

```text
produced_from
depends_on
verified_against
accepted_against
published_as
supersedes
invalidates
impacts
```

The system does not yet need a database schema. These are semantic relations to test against real cases first.

## 12. Minimum decision record

A durable decision should conceptually answer:

```text
DECISION_ID
DECISION_TYPE
TARGET_ID
TARGET_REVISION
EVIDENCE_IDS
ACTOR / AUTHORITY
TIMESTAMP
OUTCOME
EFFECTS_AUTHORIZED
EFFECTS_NOT_AUTHORIZED
```

This pattern is derived primarily from Atlas Records and the Atlas execution controls, but generalized here to information and editorial decisions.

## 13. What is specifically Atlas and should not be imported wholesale

The following should remain outside the core Content Factory model until a real editorial case demonstrates the need:

```text
leases
heartbeats
reclaim
operating-system process control
detached Git worktrees
exact shell argument vectors
executor crash recovery
provider credential boundaries
agent token telemetry
worker attribution
```

They are controls for bounded execution, not primitives of editorial knowledge.

## 14. What Content Factory adds back to Atlas-style control ideas

The editorial model contributes several concepts that are not naturally present in a task executor:

```text
claim
source
evidence
unknown
context / relation
research sufficiency
editorial intent
channel-specific projection
observation
learning
```

Therefore the two domains should not be collapsed into one architecture.

## 15. Synthesis

The nine repositories converge on a common control principle:

```text
IDENTITY
  ↓
EXACT VERSION / STATE
  ↓
BOUND INPUTS
  ↓
OPERATION
  ↓
OBSERVED RESULT
  ↓
REVIEW
  ↓
DECISION
  ↓
EXPLICIT EFFECT
```

`content_factory` adds the information semantics around that control loop:

```text
SOURCE → EVIDENCE → CLAIM → KNOWLEDGE → EDITORIAL INTENT → ASSET → PUBLICATION
```

The current hypothesis is therefore:

```text
CONTENT FACTORY
=
EDITORIAL INFORMATION MODEL
+
VERSION / DEPENDENCY MODEL
+
DECISION / AUTHORITY MODEL
+
PRODUCTION EFFECT MODEL
```

This is a research conclusion, not an implementation specification.

## 16. Current gaps to test next

The synthesis does not resolve these questions:

1. What is the minimum version identity required for knowledge and derivative assets?
2. How exactly does an upstream claim invalidation propagate?
3. Is `review` always distinct from `acceptance`, or can some editorial cases safely collapse them?
4. What is the correct boundary between `Learning` and `Knowledge`?
5. When does channel adaptation require re-verification?
6. What is the minimum unit of a publication release?
7. Which dependencies are semantic and which are merely operational?

These questions should be resolved by cases and experiments before introducing schemas or runtime code.
