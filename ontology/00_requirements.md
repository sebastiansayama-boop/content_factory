# Ontology 00 — Requirements and Scope

## Purpose

The ontology defines the semantic domain of `content_factory`: what kinds of things exist, how they are distinguished, and which relations are meaningful between them.

It does **not** define the repository folder structure, object lifecycles, workflow stages, or implementation schema.

Those remain separate concerns:

```text
ONTOLOGY  → what exists and what relations mean
STATE     → condition of a particular object/revision
PROCESS   → how work changes state
SPACE     → where information and work are located
AUTHORITY → who/what may authorize a transition or effect
RECORD    → what happened and how it is recoverable
```

## Scope

The ontology covers the editorial knowledge-production domain from incoming information through knowledge, editorial decisions, production, verification, release/publication and feedback.

It must also represent the agents, roles and external things required to explain authority and effects.

It does not attempt to model the whole physical world or human cognition.

## Ontology competency requirements

The ontology should make it possible to answer, without relying on folder names or workflow conventions:

1. What kinds of things exist in the editorial system?
2. What makes two records instances of the same kind of thing?
3. Which objects are revisions of a persistent identity?
4. Which things are objects, events, activities, roles, states, descriptions or records?
5. What does it mean for evidence to support or contradict a claim?
6. What does it mean for one object to be derived from another?
7. Which dependencies are semantic and which are merely operational?
8. Which exact object/revision was verified, accepted or published?
9. What is a decision event versus a decision result versus a decision record?
10. What is an observation event versus an observed result versus its interpretation?
11. What is a role, and in which context does an agent hold it?
12. How does an external effect relate to the internal object that authorized it?
13. Which relations permit impact propagation when upstream information changes?
14. Which distinctions are necessary to prevent production output from becoming truth by accident?

## Design principles

- Competency questions before class inventory.
- Meaning before implementation.
- Identity before lifecycle.
- Distinguish entity, event, role, state and record.
- Prefer explicit relations over overloaded generic links.
- Preserve provenance and dependency semantics separately.
- Keep authority as a contextual/normative relation, not an implicit property of a folder.
- Reuse established ontology patterns where they clarify meaning.
- Validate the model against real cases before formalizing it further.

## Out of scope for this stage

- OWL serialization as the primary design activity.
- Database tables.
- Folder-to-class mapping.
- A universal ontology of all content or all human cognition.
- Automatic inference of authority from ontology membership.

## Completion criterion

This ontology phase is complete when:

```text
competency questions
→ candidate concepts
→ identity/dependence analysis
→ relation semantics
→ candidate ontology
→ validation criteria
```

are all explicit enough that a formal implementation can be evaluated rather than guessed.
