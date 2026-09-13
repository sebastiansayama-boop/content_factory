# Learning / Memory Loop Research — Content Factory

Date: 2026-09-13
Research status: COMPLETE
Decision: EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE
Confidence: HIGH on semantic boundary; MEDIUM on future promotion criteria

## 1. Global question

How can Content Factory convert accumulated observations, experiments and external outcomes into reusable knowledge that affects future work without silently converting a record, interpretation or one-off success into truth or authority?

## 2. Decomposition

### Q1 — Semantic layers
What is the difference between record, observation, evidence, interpretation, learning, knowledge, memory and decision?

### Q2 — Promotion
What mechanism moves a learning candidate into reusable memory/knowledge?

### Q3 — Epistemic control
What prevents one observation, successful output, metric or model inference from becoming a reusable rule?

### Q4 — Provenance
How is the complete path from source/experiment to reusable knowledge preserved?

### Q5 — Invalidation
How are contradiction, staleness, supersession and invalidation represented without rewriting history?

### Q6 — Operational use
How does accepted knowledge become an input to a later work item, decision or verification criterion?

### Q7 — Feedback closure
How can the factory demonstrate that knowledge actually changed a later decision or outcome rather than merely existing in the repository?

### Q8 — Implementation boundary
Which mechanisms are justified now, and which remain unproven until a real production case exists?

## 3. Source map

### Repository sources

1. `RULES.md`
2. `docs/28_project_operating_memory.md`
3. `docs/29_project_direction_map.md`
4. `09_learning/README.md`
5. `02_memory/README.md`
6. `10_records/README.md`
7. Recent external-system research records Q13–Q15

### External sources

1. W3C PROV model and provenance concepts: provenance distinguishes entities, activities, agents and derivations; provenance identifies how an item was produced but does not itself establish truth or authority.
2. NIST Baldrige knowledge-management/organizational-learning guidance: evidence gathered from multiple sources is used for data-driven decision making and continuous improvement. citeturn0search14
3. Martin Fowler, Event Sourcing: durable event history can preserve how current state arose and can support reconstruction of prior states. citeturn0search1
4. IBM Data Lineage / Provenance: lineage tracks origin, transformations and downstream use; provenance preserves historical context and supports auditability, trust and impact analysis. citeturn0search0turn0search2
5. IBM governance/catalog practice: reusable governed information needs discoverability, stewardship, lineage and explicit governance rather than simply accumulating records. citeturn0search3turn0search5
6. Atlas `07_MEMORY_KNOWLEDGE_AND_LEARNING_MODEL.md`: separate control/evidence/context lanes, source lineage, contradiction preservation, revision/supersession, bounded context packets, lesson candidates, policy adoption, retention and regression testing. The Atlas document is explicitly `SPECIFICATION_CANDIDATE / THEORY_ONLY`, so it is a design reference rather than implementation proof. fileciteturn304file0L1-L2

## 4. Five-level semantic reconstruction

### Level 0 — History
`10_records` is the durable historical reconstruction layer. It stores events, decisions, revisions, experiments, effects, provenance and supersession. It is not the current model and does not itself create knowledge. `RULES.md` explicitly separates history from current state and prohibits silently promoting observation to knowledge. fileciteturn295file0L2-L2 fileciteturn298file0L2-L2

### Level 1 — Observation / evidence
An observation records what was actually observed. Evidence is the support that allows an interpretation or claim to be evaluated. The distinction matters because the same observation can support multiple interpretations. Current rules require observation, interpretation, decision and effect to remain separate. fileciteturn298file0L2-L2

### Level 2 — Learning
`09_learning` is explicitly the interpretation/promotion-candidate layer. Its minimum record contains observation and experiment references, question/trigger, interpretation, evidence, alternative explanations, uncertainty, status, proposed change and impact scope. Its transition is `question → experiment/observation → result → evidence → interpretation → lesson/learning candidate → explicit decision → knowledge/process/model update`. A learning candidate cannot silently mutate `model/`. fileciteturn293file0L2-L2

### Level 3 — Reusable memory / knowledge
`02_memory` is intended for durable reusable information, not chronological history. A reusable item requires identity, type, scope, content, status, source/evidence/provenance, revision, known unknowns and supersession links. Entry into memory requires an explicit promotion step supported by evidence or explicit decision. fileciteturn294file0L2-L2

### Level 4 — Future work
The operating-memory model defines the intended chain `PROJECT MAP → CURRENT CHECKPOINT → QUESTION → RESEARCH/EXPERIMENT → EVIDENCE → INTERPRETATION → LESSON → REUSABLE KNOWLEDGE → DECISION → CHANGED WORK/OUTCOME → PROJECT MAP UPDATE`. The model therefore already contains the semantic route from experience to future behavior. fileciteturn301file0L2-L2

### Level 5 — Closed learning loop
A real learning loop exists only when an accepted learning/knowledge item is subsequently retrieved or referenced by a later work item, affects a decision/specification/verification criterion, and the later outcome is observed. Repository presence alone is not proof of learning. This is consistent with the repository's own distinction between knowledge, decision and implementation outcome, and with lineage/event-sourcing practice where history supports reconstruction but does not by itself prove the usefulness of a projection. fileciteturn301file0L2-L2 citeturn0search1turn0search0

## 5. Current repository inspection

### `10_records`
Active. Q13, Q14 and Q15 are durable research records with explicit question decomposition, evidence, inference boundaries, decisions, repository impact and derived questions. Q15 explicitly concludes `EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE`, demonstrating that research can terminate without implementation churn. 

### `09_learning`
Semantically specified but currently contains only `README.md`. No concrete learning records were found in the zone. Therefore the promotion mechanism is described but not demonstrated as a recurring repository process. Directory inspection confirms the README is the only current file. fileciteturn299file0L2-L10

### `02_memory`
Semantically specified but currently contains only `README.md`. No accepted reusable memory items were found. The promotion rule exists as documentation, but no concrete promotion artifact is currently present. Directory inspection confirms the README is the only current file. fileciteturn300file0L2-L10

### `10_records → 09_learning → 02_memory`
The semantic chain is documented, but there is currently no demonstrated artifact chain proving that a historical research/experiment record has been converted into a learning record, explicitly decided, promoted into reusable memory, retrieved later, and used to change a subsequent work item.

### Project direction
The Project Direction Map currently marks Learning Loop as `PARKED / NOT STARTED` because no real external production feedback loop has yet been demonstrated. Its stated next legitimate step is to capture `observation → interpretation → learning candidate → explicit decision` after the first real external effect. fileciteturn302file0L2-L2

## 6. Mechanism comparison

### Mechanism A — Append-only history
Already present conceptually through `10_records`. It preserves reconstruction and provenance but is not learning by itself.

### Mechanism B — Learning candidate
Already specified in `09_learning`. It creates an explicit epistemic boundary between evidence and reusable knowledge.

### Mechanism C — Explicit promotion decision
Already required by the model. It prevents `learning → knowledge` from being automatic.

### Mechanism D — Versioned reusable memory
Already specified in `02_memory`, including provenance, revision, supersession and known unknowns.

### Mechanism E — Retrieval into future work
Semantically allowed by `02_memory`, but not yet demonstrated in a concrete work item.

### Mechanism F — Outcome attribution
Required to close the loop, but not yet demonstrated for a real production learning case.

### Mechanism G — Invalidation / supersession
Specified. History remains, reusable state changes through revision/supersession rather than destructive rewriting.

### Mechanism H — Measurement of learning quality
Not yet operationally demonstrated. Atlas research provides candidate measures such as retrieval quality, stale-memory rate, retention and regression tests, but these are not yet justified as Content Factory primitives. Atlas itself labels the memory/learning model theory-only. fileciteturn304file0L1-L2

## 7. Critical distinction

The current repository has a **learning model**, not yet a **learning mechanism**.

More precisely:

```text
HISTORY                = implemented as durable research/record artifacts
LEARNING SEMANTICS     = specified
PROMOTION RULE         = specified
MEMORY SCHEMA          = specified
MEMORY CONTENT         = not yet demonstrated
RETRIEVAL              = not yet demonstrated
FUTURE DECISION USE    = not yet demonstrated
CLOSED LEARNING LOOP   = not yet demonstrated
```

This explains the earlier observation that knowledge accumulation exists in `10_records`, while experience/learning is not yet accumulating as a separate operational layer.

## 8. What external research changes

### SUPPORTS_CURRENT_MODEL
- Provenance should preserve origin and transformation history rather than only current values. citeturn0search0turn0search2
- Historical event records and current projections should remain distinguishable. citeturn0search1
- Continuous improvement depends on using evidence in decision and knowledge-management processes, not merely collecting records. citeturn0search14

### EXTENDS_CURRENT_MODEL
- Reusable knowledge needs not only provenance but also discoverability/use lineage: it should be possible to establish where a reusable item was later consumed and what decision/work it influenced. This follows from data-lineage practice and is a candidate extension, not yet a new Content Factory primitive. citeturn0search0turn0search3
- A closed learning loop needs an observable downstream use/outcome boundary; otherwise the repository can demonstrate storage and promotion but not learning effectiveness.

### REVEALS_GAP
- No concrete learning records exist in `09_learning`.
- No concrete accepted reusable memory records exist in `02_memory`.
- No verified promotion chain exists from a real observation/experiment to reusable memory.
- No verified downstream consumption chain exists from memory to a later decision/work item.
- No measured retention/regression mechanism exists in Content Factory.

### NOT_APPLICABLE / UNJUSTIFIED_NOW
- Vector database, knowledge graph, automatic embedding retrieval, online model training and autonomous prompt/policy mutation are not justified by the current evidence.
- Atlas's richer memory machinery is useful as a comparison boundary but is not proof that Content Factory needs those mechanisms. fileciteturn304file0L1-L2

## 9. Minimal complete semantic loop

The smallest loop that would actually prove learning is not merely:

`observation → learning record → memory`.

It is:

```text
1. OBSERVE
2. PRESERVE EVIDENCE
3. INTERPRET
4. FORM LEARNING CANDIDATE
5. MAKE EXPLICIT PROMOTION DECISION
6. CREATE VERSIONED REUSABLE KNOWLEDGE/MEMORY
7. RETRIEVE IT FOR A LATER WORK ITEM
8. SHOW THAT IT AFFECTED A DECISION / SPECIFICATION / VERIFICATION
9. OBSERVE THE RESULT
10. RECORD WHETHER THE KNOWLEDGE HELPED, FAILED, OR REQUIRED REVISION
```

Steps 1–6 are mostly represented semantically by the current repository. Steps 7–10 are not yet demonstrated.

## 10. Candidate promotion gate

Candidate only; not yet a repository primitive:

```text
PROMOTE_TO_REUSABLE_KNOWLEDGE iff
    source/evidence is reconstructable
AND scope is explicit
AND competing explanations are considered
AND uncertainty is explicit
AND contradiction status is known
AND a reusable proposition is actually identifiable
AND an explicit decision authorizes promotion
AND revision/provenance links are created
```

For a transferable operational rule, an additional test should normally be required:

```text
candidate pattern
→ counterexample / adjacent-scope test
→ retention / repeat test
→ explicit decision
```

This is consistent with Atlas's candidate controls against single-episode generalization, negative transfer and unobserved retention, but those controls remain theory-only in Atlas. fileciteturn304file0L1-L2

## 11. Invalidation model

The research supports retaining at least four distinct situations:

```text
SUPERSEDED   = replaced by a newer accepted revision
CONTRADICTED = material evidence conflicts with the claim
STALE        = no longer current for the declared scope/time
REJECTED     = promotion/learning proposition was not accepted
```

These must not be collapsed into one `inactive` flag because they imply different future reasoning behavior. Historical evidence remains discoverable while current retrieval excludes or qualifies the obsolete item.

## 12. Answer to the original structural question

Content Factory does not currently lack a conceptual learning architecture. It lacks **demonstrated execution of the learning loop**.

The deepest missing boundary is:

```text
REUSABLE KNOWLEDGE
        ↓
FUTURE WORK CONSUMPTION
        ↓
DECISION / SPECIFICATION / VERIFICATION CHANGE
        ↓
OBSERVED OUTCOME
        ↓
LEARNING ABOUT THE KNOWLEDGE ITSELF
```

This is the boundary that must be tested before adding storage technology, retrieval infrastructure, new ontology classes or automatic learning machinery.

## 13. Decision

`EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE`

No repository model or implementation change is justified yet.

The next legitimate research/experiment is a bounded, fully reconstructable learning case that can be executed without requiring a real external effect if a safe internal case is available. If such a case cannot demonstrate downstream use, the first real external-effect case should become the learning-loop proof.

## 14. Derived questions

Q19 — Can one existing Content Factory research result be converted into a real `09_learning` record without inventing evidence?

Q20 — Can that learning candidate be explicitly promoted into one `02_memory` item while preserving provenance and revision identity?

Q21 — Can a later bounded work item retrieve and cite that memory item so that its decision demonstrably changes?

Q22 — What is the smallest observable outcome that can falsify or strengthen the promoted knowledge?

Q23 — Should downstream consumption be represented as a relation in existing records, or does a concrete case demonstrate the need for a new recurring artifact type?

Q24 — What evidence threshold is required before a reusable creative/editorial pattern is promoted beyond a context-bound candidate?

## 15. Repository impact

- Research record added only.
- No production code changed.
- No ontology changed.
- No new top-level folder created.
- No memory item fabricated from research.
- No learning item fabricated without a real observation/experiment.
- No automatic promotion mechanism introduced.

## 16. Verification

The research record was created in `10_records/`, consistent with the repository's historical/provenance boundary. The directly relevant README files, operating-memory model, direction map, current research record and Atlas comparison specification were inspected before this conclusion. The result remains `EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE` until a concrete learning case demonstrates the missing downstream loop.
