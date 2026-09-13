# Content Factory Repository Rules

The repository is a research environment for an editorial knowledge and production system.

## Governing rules

1. Treat `model/` as the current working model, not as raw research or history.
2. Treat `10_records/` as durable history. Do not rewrite history to hide superseded states.
3. Treat `archive/` as inert unless explicit reactivation is recorded.
4. Keep observation, interpretation, decision and effect separate.
5. Keep object identity and revision explicit for mutable information.
6. Never let production silently introduce unsupported factual claims.
7. Never infer authority from folder ownership or process completion.
8. Verification does not imply acceptance; acceptance does not imply publication.
9. Record provenance, dependency and impact as separate relations.
10. Keep unknowns explicit.
11. Use real cases and experiments to challenge the model before adding new primitives, states, or ontology classes.
12. Research external references and inspect relevant repositories before inventing a solution to an unresolved structural question.
13. Do not import Atlas execution machinery (leases, worker recovery, process isolation, token controls) into the editorial model unless a concrete case demonstrates the need.
14. Do not treat the brain analogy as a literal ontology. It is a functional design heuristic.
15. A new top-level folder requires a recurring information type or control boundary that cannot be represented safely by an existing zone.
16. Any current model change must be traceable to evidence, an experiment, a case failure or an explicit decision.
17. The repository is a bounded system interacting with an external world; the world is not part of the repository model.
18. The highest-level loop is `WORLD → OBSERVATION → MODEL → WORK → DECISION → ACTION → CONSEQUENCE → LEARNING → MODEL`.
19. Folders are projections of system functions, not independent departments.
20. Every material case must preserve enough information to reconstruct its path across sensing, modelling, decision, action, verification, effect and learning.
21. Treat ontology as a semantic domain model, not as a workflow, state machine, folder map, or implementation schema.
22. Do not promote a repository term to an ontology class without a semantic job and at least one competency question.
23. Distinguish entity, event/activity, role, state, artifact, description and record when their identity or behavior differs.
24. Do not collapse support, contradiction, derivation, production, dependency, impact, invalidation and supersession into one generic relation.
25. Treat authority as contextual and scoped; do not make it an intrinsic consequence of ontology membership.

## Chat ↔ repository protocol

26. Every material project message starts a protocol cycle defined in `docs/25_chat_repository_operating_protocol.md`.
27. Before a material architectural claim or repository change, inspect the current repository state relevant to the question. Do not rely on remembered repository state when the repository can be inspected.
28. Unresolved structural, architectural, process, organizational, methodological or technology-selection questions require external research before a model change.
29. External research must be reconciled against the current repository model. Every material finding is classified as `SUPPORTS_CURRENT_MODEL`, `CONTRADICTS_CURRENT_MODEL`, `EXTENDS_CURRENT_MODEL`, `REVEALS_GAP`, `NOT_APPLICABLE`, or `UNCERTAIN`.
30. Research findings are evidence, not automatic repository truth. A repository change requires an explicit bridge from evidence to decision.
31. The evidence hierarchy is: verified execution/experiment → repository contracts and machine-readable models → primary/authoritative external sources → repository synthesis → secondary research → analogy/hypothesis → chat intuition.
32. A material repository write requires: understood intent, current-state inspection, relevant research when required, defined purpose, identified target artifact, dependency awareness, and a verification method.
33. Change the smallest sufficient layer. Do not modify implementation for documentation problems, ontology for workflow problems, or create a primitive when an existing primitive is sufficient.
34. Synchronize directly affected human-readable, machine-readable, navigation, governance and evidence artifacts when a material model changes. If synchronization cannot be completed, record the inconsistency and do not report the work as complete.
35. After every material write, fetch and verify the resulting artifact, revision/commit, direct dependencies and research consistency.
36. A successful write operation is not proof that the conceptual change is correct.
37. Do not silently promote hypothesis → fact, research → truth, candidate → verified, observation → knowledge, metric → learning, learning → strategy, production result → acceptance, verification → acceptance, acceptance → publication, or execution capability → authority.
38. No-change is a valid terminal outcome. Do not create repository churn merely to produce a commit.
39. A material cycle ends only at `COMPLETED`, `NO_CHANGE_REQUIRED`, `USER_DECISION_REQUIRED`, `INSUFFICIENT_EVIDENCE`, `RESEARCH_CONFLICT_REQUIRES_RESOLUTION`, `REPOSITORY_WRITE_BLOCKED`, or `EXTERNAL_EFFECT_REQUIRES_AUTHORITY`.
40. The final report must distinguish what changed, what was verified, research consistency, unknowns, revision/commit and the next legitimate step.

## Project operating memory and direction control

41. The repository must preserve not only current architecture but also enough project experience to resume work after a context switch, branch change, completed experiment, failure, or parked direction. The governing model is documented in `docs/28_project_operating_memory.md`.
42. Project navigation must distinguish `PROJECT MAP` from `CURRENT CHECKPOINT`. The map describes available and historical directions; the checkpoint describes the exact current stop.
43. Every material direction must preserve, at minimum: goal, status, current checkpoint, proven state, unproven state, research needed, dependencies, blockers, next legitimate step and return point.
44. The current direction map is `docs/29_project_direction_map.md`; its machine-readable projection is `model/project-direction-map.yaml`. Both must remain synchronized when direction status or checkpoint materially changes.
45. Leaving a direction requires preserving what changed, what was learned, what was disproved, what remains unknown, what should not be repeated, what remains to be done and where to return.
46. Parked and completed directions remain discoverable. They must not be deleted merely because they are not active.
47. Reusable experience must remain distinguishable from evidence, decisions and implementation state. The preferred promotion chain is `observation/experiment → evidence → interpretation → lesson → knowledge candidate → explicit decision`.
48. Real-world mechanisms may be adapted when they solve a demonstrated problem, but the repository must preserve source, mechanism, evidence of use, applicability, limitations and the adaptation decision. External practice is evidence for a design choice, not proof of local correctness.
49. Durable decisions should preserve context, alternatives, chosen option, tradeoffs, evidence, confidence, status and supersession relationships. Historical rationale must not be silently rewritten.
50. Creative experience is valid project knowledge when it affects repeatable work, but it must preserve context, experiment/treatment, observed effect, reusable candidate, uncertainty, examples, evidence and confidence rather than being represented as objective fact by default.
51. Do not create separate top-level `knowledge/`, `mechanisms/`, or `evidence/` folders merely to satisfy these semantic roles. Existing zones must be used unless a recurring information type or control boundary proves that a new top-level boundary is necessary.
52. Both successful and failed experiments may produce learning. Unexpected success must be examined rather than automatically promoted into a reusable rule.
53. Context transfer is a repository concern, not a conversational-memory assumption. If the repository can contain the checkpoint, direction, evidence or return point, it must be inspected rather than reconstructed from chat memory.

## External research basis

These rules are consistent with external practices emphasizing provenance, explicit decision rationale, version-controlled state, learning from experience, and defined governance. W3C PROV models provenance around entities, activities, agents and derivations; ADR practice records individual decisions and rationale; NIST AI RMF emphasizes governance, documentation and differentiated oversight; after-action review practice treats both failures and successes as inputs to organizational learning. These sources support the protocol principles but do not constitute proof that this repository implements them.

See `docs/25_chat_repository_operating_protocol.md` for the mandatory chat/repository protocol.
See `docs/28_project_operating_memory.md` for the project operating-memory model.
See `docs/29_project_direction_map.md` for current navigation and return points.
See `model/project-direction-map.yaml` for the machine-readable direction projection.
See `docs/14_repository_rules.md` for detailed repository rules.
See `docs/23_content_factory_operating_model.md` for the current factory operating model.
See `docs/24_capability_and_engineering_layer.md` for the capability/engineering boundary.
