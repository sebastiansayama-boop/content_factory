# 13 — Repository Structure and Functional Map

The repository is organized by information function and control boundary, using the brain analogy as a heuristic. The structure is not an anatomical model.

## Top-level map

```text
content_factory/
│
├── 00_inbox/             ← incoming sensory field
├── 01_observation/       ← raw observed signals
├── 02_memory/            ← durable evidence, knowledge and relations
├── 03_working_context/   ← active task context / working memory
├── 04_reasoning/         ← research synthesis and explicit reasoning
├── 05_decision/          ← decisions, authority and commitments
├── 06_production/        ← transformation into concrete assets
├── 07_verification/      ← error detection, validation and revision requests
├── 08_effects_feedback/  ← publication effects and external observations
├── 09_learning/          ← interpreted learning and model updates
├── 10_records/           ← append-only durable history and provenance
│
├── model/                ← current system model
├── docs/                 ← explanatory and synthesis documents
├── templates/            ← reusable case/decision structures
└── archive/              ← explicitly superseded material
```

## 00_inbox — incoming field

Purpose: receive unclassified material before the system decides what it is.

Contains:
- imported notes;
- raw external material;
- unsorted questions;
- newly discovered references;
- case inputs waiting for classification.

Rules:
- no claim is authoritative merely because it entered `00_inbox/`;
- do not perform editorial synthesis here;
- every item eventually gets classified into observation, source, question, case input or discarded material.

Analogy: sensory stream before attention and interpretation.

## 01_observation — observed signals

Purpose: preserve what was actually observed before interpretation.

Contains:
- signals;
- measurements;
- corrections;
- new-source notifications;
- operational observations;
- audience observations.

Rules:
- observation must describe what happened, not why;
- interpretation belongs in `09_learning/` or an explicit research record;
- raw observation should remain recoverable.

Analogy: salience/sensory detection layer.

## 02_memory — durable knowledge

Purpose: preserve reusable information independent of a single publication.

Suggested internal areas:

```text
02_memory/
├── sources/
├── evidence/
├── claims/
├── knowledge/
└── relations/
```

Contains:
- source records;
- evidence extracts;
- claims;
- unknowns;
- knowledge revisions;
- relations between claims, sources and evidence.

Rules:
- never silently overwrite a prior knowledge revision;
- evidence and claims must retain provenance;
- unknowns remain explicit;
- knowledge may be reused by multiple editorial decisions.

Analogy: durable episodic/semantic memory. The analogy is functional; human memory is not a single storage area. citeturn842770search0turn842770search3

## 03_working_context — active working memory

Purpose: hold temporary context needed to perform one bounded task.

Contains:
- current research brief;
- active question set;
- selected evidence;
- current constraints;
- audience/context requirements;
- acceptance criteria;
- temporary working notes.

Rules:
- working context is disposable and task-bound;
- do not use it as a source of durable truth;
- when a working observation becomes durable knowledge, promote it through an explicit transition.

Analogy: working memory and active executive context. Frontoparietal executive systems are associated with working memory and cognitive control. citeturn842770search1turn842770search11

## 04_reasoning — synthesis and model formation

Purpose: convert bounded evidence into explicit interpretations, comparisons and hypotheses.

Contains:
- research syntheses;
- contradiction analysis;
- comparative analysis;
- hypotheses;
- reasoning traces that are worth preserving;
- case analysis.

Rules:
- clearly separate evidence from interpretation;
- hypotheses are not automatically knowledge;
- reasoning cannot silently change the current model;
- model changes require a decision record.

Analogy: executive integration rather than a single anatomical module.

## 05_decision — authority and selection

Purpose: record choices that change what the system is allowed or expected to do next.

Contains:
- editorial decisions;
- acceptance decisions;
- publication authorization;
- holds/rejections;
- decisions to update or retire existing material;
- durable decision records.

Rules:
- every significant decision targets an exact object/revision;
- evidence supporting the decision is recorded;
- authorization scope is explicit;
- "reviewed" does not mean "accepted";
- acceptance does not mean publication.

Analogy: executive control and action-selection function. Prefrontal systems interact with basal ganglia and thalamus in goal-directed action selection and updating. citeturn842770search7

## 06_production — action / transformation

Purpose: transform approved knowledge and a bounded specification into a concrete asset.

Contains:
- content specifications;
- production briefs;
- asset revisions;
- generated or authored outputs;
- channel representations.

Rules:
- production consumes approved inputs;
- production is not authorized to invent unsupported facts;
- material changes create new revisions;
- production result is not automatically accepted.

Analogy: action system. The analogy is to function, not anatomy.

## 07_verification — error monitoring and correction

Purpose: detect divergence between intended state and produced result.

Contains:
- verification runs;
- factual checks;
- semantic checks;
- specification conformity checks;
- format/render checks;
- revision requests.

Rules:
- verification references exact revisions;
- failures do not silently mutate the asset;
- verification result is distinct from acceptance;
- channel adaptation that changes semantics can trigger re-verification.

Analogy: error monitoring and sensorimotor error correction. Cerebellar and basal-ganglia systems participate in motor learning and prediction/error-related processes, but this analogy should not be read as mapping verification to one brain structure. citeturn842770search15

## 08_effects_feedback — interaction with the external world

Purpose: separate internal acceptance from external effect and preserve what happened afterward.

Contains:
- release records;
- publication records;
- channel delivery results;
- external effect records;
- incoming corrections and audience responses.

Rules:
- an external effect must be explicit;
- publication identifies the exact accepted revision/release;
- publication success does not imply content truth;
- delivery result and observation are separate records.

Analogy: action → environment → sensory feedback loop.

## 09_learning — adaptation

Purpose: interpret observations and determine whether they justify changing future behavior or knowledge.

Contains:
- interpretations;
- learning candidates;
- accepted learning;
- rejected learning;
- proposed model changes;
- experiments motivated by observations.

Rules:
- observation comes before interpretation;
- learning remains a hypothesis until explicitly accepted for reuse;
- learning does not automatically become knowledge truth;
- a proposed model change needs evidence and a decision.

Analogy: plasticity and strategy updating. PFC research emphasizes interaction between immediate goal-directed behavior and longer-timescale learning. citeturn842770search10

## 10_records — durable history

Purpose: preserve what happened, independent of current interpretation.

Contains:
- decision records;
- revision history;
- provenance records;
- case timelines;
- superseded model snapshots;
- experiment outcomes.

Rules:
- append-only conceptually;
- never rewrite history to make the current model look cleaner;
- current state is a projection over history;
- records must identify exact object/revision when relevant.

Analogy: autobiographical/episodic record, with an important distinction: repository records are intentionally explicit and inspectable.

## model — current internal model

Contains only the currently adopted working model:

```text
model/
├── state-machine.yaml
├── information-flow.md
└── repository-map.md
```

Rules:
- a file in `model/` must represent current working assumptions, not raw research;
- changes require a decision or a clearly documented synthesis;
- superseded versions move to history/archive rather than being silently rewritten without record.

Analogy: current internal operating model rather than long-term storage.

## docs — explanation

Purpose: explain the model, research synthesis and conceptual relationships.

`docs/` is not a dumping ground for raw evidence or cases.

## templates — operating interfaces

Purpose: define repeatable structures for cases, decisions, experiments and research records.

Templates are contracts for capture, not records themselves.

## archive — inactive material

Purpose: preserve explicitly superseded or inactive material without allowing it to masquerade as current truth.

Rules:
- historical material remains inspectable;
- archived material has no authority merely because it exists;
- reactivation requires an explicit decision.

## Functional connections

```text
00_inbox
   ↓ classification
01_observation
   ↓ selection / evidence extraction
02_memory ←→ 04_reasoning
   ↑                ↓
   │             hypotheses
   │                ↓
03_working_context → 05_decision
                       ↓
                  06_production
                       ↓
                  07_verification
                       ↓
                  05_decision
                       ↓
              08_effects_feedback
                       ↓
                 01_observation
                       ↓
                  09_learning
                   ↙       ↘
             02_memory    04_reasoning

10_records observes the whole system.
model/ describes the current system.
docs/ explains it.
templates/ standardizes capture.
archive/ preserves superseded states.
```

The key rule is that no folder is an isolated department. The repository models interacting functions and controlled transitions.
