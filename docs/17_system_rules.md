# 17 — System-Level Rules

These rules sit above individual folder rules. They define how the repository behaves as one system.

## A. Boundary rules

1. The repository is a model of an information-producing system, not the external world.
2. External facts, observations, and outcomes must enter through an explicit observation boundary.
3. Internal interpretation must never be presented as direct observation.
4. An external effect is not complete merely because the system intended or prepared it.

## B. State rules

5. Every material mutable object has an identity and revision.
6. Every object has its own lifecycle; do not create one global lifecycle for unrelated objects.
7. Current state is a projection over history, not a replacement for history.
8. Material changes create a new revision rather than rewriting accepted or published history.
9. State is explicit; never infer it from filenames, folder location, timestamps or prose tone.

## C. Knowledge rules

10. Evidence, interpretation, decision and effect are separate information classes.
11. Unknown is a valid state and must remain explicit.
12. A claim is not stronger than its supporting evidence.
13. A production artifact is not a source of truth merely because it is polished.
14. Learning is a candidate for adaptation, not automatically a new fact.
15. Model changes require an explicit reason: research, experiment, case failure or decision.

## D. Control rules

16. Processes produce information; authority decides state transitions.
17. Review is not acceptance.
18. Acceptance is not publication.
19. Publication is not outcome.
20. Authority does not propagate implicitly from one transition to the next.
21. Every significant decision identifies target object, exact revision, evidence, authority and authorization scope.

## E. Feedback rules

22. Consequences return as observations before becoming learning.
23. Learning may update memory, reasoning or future questions, but promotion is explicit.
24. Upstream changes must be able to mark downstream dependencies as affected.
25. Dependency, provenance and impact are distinct relations.

## F. Repository rules

26. `model/` contains the current working model only.
27. `10_records/` preserves durable history and provenance.
28. `archive/` is inert unless explicitly reactivated.
29. `docs/` explains and synthesizes; it is not a dumping ground for raw case material.
30. `templates/` defines capture contracts; templates are not evidence.
31. A new top-level folder requires a recurring information function or control boundary that cannot be represented safely by an existing zone.

## G. Brain analogy rule

32. Use the brain only as a functional analogy: sensing, salience, memory, working context, control, action, error monitoring and learning.
33. Do not map a folder to a literal brain structure.
34. When biological analogy conflicts with information-flow evidence, preserve the information-flow model.

## H. Research rule

35. Structural uncertainty is a research question.
36. Before inventing a new primitive, state or folder, inspect external references and relevant existing repositories.
37. A rule becomes stable only after surviving real cases or repeated supporting evidence.

## I. Highest-level invariant

For every material case, the repository should make it possible to reconstruct:

```text
WORLD INPUT
→ OBSERVATION
→ INTERNAL MODEL
→ WORKING CONTEXT
→ REASONING
→ DECISION
→ ACTION
→ VERIFICATION
→ EXTERNAL EFFECT
→ CONSEQUENCE
→ LEARNING
→ MODEL UPDATE
```

If a material transition cannot be reconstructed, either the case record or the system model is incomplete.
