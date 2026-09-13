# 17 — System-Level Rules

These rules sit above individual folder and process rules.

## A. System boundaries

1. `Content Ecosystem` is broader than `Content Factory`.
2. `Content Factory` is a functional production subsystem, not the whole business system.
3. External world, market, audience and business outcomes remain outside the factory boundary unless explicitly modeled as inputs or effects.
4. Do not solve an ecosystem problem merely by expanding the factory.

## B. Factory architecture

5. The factory has four layers: strategic intent, value flow, factory control, and shared semantic substrate.
6. The seven value-flow systems are Input, Knowledge, Editorial, Production, Quality, Distribution and Learning.
7. Factory Control is a control plane, not a sequential eighth stage.
8. Shared semantic substrate is not a workflow stage.
9. Strategy/portfolio intent supplies direction and demand; Editorial translates it into bounded production intention.

## C. Work and flow

10. The primary unit of flow is a bounded Content Work Item / Work Package, not a file.
11. One work item may produce multiple asset revisions.
12. One release may bundle multiple work-item outputs.
13. Pull work from real demand and available capacity.
14. Limit WIP at constraining stages rather than maximizing local utilization.
15. Route work by required capability, risk, dependencies and constraints.
16. Treat bottleneck identification and management as a continuous factory function.

## D. Knowledge and semantics

17. Keep source, evidence, claim, knowledge, specification, asset and publication semantically distinct.
18. Provenance, dependency and impact are different relations.
19. Identity and revision remain explicit for mutable objects.
20. Structured content should remain channel-neutral where semantics permit.
21. Channel adaptation that changes meaning requires a new bounded revision and appropriate re-verification.
22. Production output is not automatically a source of truth.

## E. Quality and effects

23. Verification is not acceptance.
24. Acceptance is not publication.
25. Publication is not outcome.
26. Release is a coordinated readiness/effect boundary, not simply another asset state.
27. External effects return as observations before interpretation becomes learning.
28. Learning is not automatically truth and does not silently rewrite reusable knowledge.

## F. Control and authority

29. Factory Control manages flow; it does not inherit epistemic authority over content.
30. Automation may perform repeatable bounded operations but does not implicitly inherit consequential authority.
31. Every consequential transition identifies target object, exact revision, evidence basis, authority and scope.
32. Authority is contextual and scoped.

## G. Repository and model

33. `model/` contains the current working model; it is not raw evidence or history.
34. `10_records/` preserves durable history.
35. `ontology/` defines semantic domain concepts and relations; it is not the workflow or state machine.
36. `SPACE_MAP.md` and `docs/16_system_map.md` are navigation maps, not sources of truth about external reality.
37. `archive/` is inert unless explicit reactivation is recorded.
38. Any current model change must be traceable to research, experiment, case failure or explicit decision.

## H. Research and evolution

39. Structural uncertainty is a research question.
40. Before adding a subsystem, capability, primitive, state or ontology class, establish the missing function and its boundary.
41. Use external references and existing repositories before inventing a structural solution.
42. Validate the integrated model against real cases before implementation hardening.

## I. Highest-level case invariant

A material case should be reconstructable as:

```text
STRATEGIC CONTEXT
→ INPUT
→ KNOWLEDGE
→ EDITORIAL DECISION
→ WORK ITEM
→ PRODUCTION
→ VERIFICATION
→ ACCEPTANCE
→ RELEASE
→ EXTERNAL EFFECT
→ OBSERVATION
→ LEARNING
→ KNOWLEDGE / EDITORIAL / STRATEGY UPDATE
```

If a transition or boundary cannot be reconstructed, either the case record or the system model is incomplete.
