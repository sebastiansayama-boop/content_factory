# Ontology 01 — Competency Questions

These questions are the acceptance tests for the conceptual model. If the ontology cannot answer them from its own semantics, the model is incomplete or underspecified.

## Existence and identity

CQ01. What kind of thing is `Knowledge K8`?

CQ02. How do we know that two `KnowledgeRevision` records belong to the same `Knowledge` identity?

CQ03. What makes `Asset A12 revision 3` different from `Asset A12 revision 4`?

CQ04. Is a revision an independent entity, a state description, or both at different modeling levels?

## Evidence and knowledge

CQ05. Which evidence supports claim `C17`?

CQ06. Which evidence contradicts `C17`?

CQ07. Which source gave rise to evidence `E17`?

CQ08. Which claims are included in a particular knowledge revision?

CQ09. If evidence `E17` becomes invalid, which knowledge revisions may be affected?

CQ10. Can a production artifact introduce a new claim without passing through the knowledge/verification boundary?

## Decisions

CQ11. What happened when an editorial decision was made?

CQ12. What was the resulting decision outcome?

CQ13. What record proves the decision?

CQ14. Which agent played the decision-making role in that context?

CQ15. Which exact revision was the decision about?

## Production and verification

CQ16. Which content specification constrained asset revision `A12-r3`?

CQ17. Which knowledge revision was part of the semantic basis for that asset?

CQ18. What verification activity checked `A12-r3`?

CQ19. What verification result was produced?

CQ20. Which exact revision was accepted, by which authority, and against which verification result?

## Release and publication

CQ21. Which release contains a particular asset revision?

CQ22. Which accepted state was published externally?

CQ23. Is `Publication P7` an artifact, an event, an external state, or a record of an external event?

CQ24. Which channel and external target were involved in a publication effect?

## Feedback and learning

CQ25. What was actually observed after publication?

CQ26. What interpretation was derived from that observation?

CQ27. Which learning candidate was produced from the observation?

CQ28. What evidence is required before a learning candidate may affect reusable knowledge?

## Dependency and impact

CQ29. What does `depends_on` mean for this pair of objects?

CQ30. How is `depends_on` different from `produced_from`?

CQ31. How is `supports` different from `depends_on`?

CQ32. How is `invalidates` different from `supersedes`?

CQ33. What downstream objects are semantically impacted by a changed knowledge revision?

## Authority

CQ34. What agent has authority to accept this exact asset revision?

CQ35. Is authority intrinsic to the agent, or does the agent hold a role within a decision context?

CQ36. Does completing a production activity create acceptance authority? The intended answer must be no unless explicitly modeled otherwise.

## Unknowns and boundaries

CQ37. Can the ontology represent an unresolved fact without promoting an inference to a claim?

CQ38. Can it distinguish an observed event from an interpretation of that event?

CQ39. Can it represent a proposed future action without treating that action as an external effect?

CQ40. Can it represent historical truth without confusing it with the current model?

## Validation rule

Every proposed top-level class or relation should justify at least one competency question. A term with no semantic job is a candidate for removal, not automatic promotion into the ontology.
