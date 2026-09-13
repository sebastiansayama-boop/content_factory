# Ontology 06 — Constraints and Validation

These are semantic constraints for the candidate ontology. They are stronger than folder conventions but weaker than a future formal reasoner until expressed in a formal language.

## Identity constraints

OC01. A revision must identify the persistent entity it versions.

OC02. A material semantic change to an accepted revision must not silently preserve the same revision identity.

OC03. An event record is not identical to the event it records.

OC04. A source is not identical to evidence derived from the source.

## Epistemic constraints

OC05. `supports` and `contradicts` require an epistemic target such as a claim or proposition.

OC06. Production output is not itself evidence of factual truth.

OC07. A learning candidate cannot directly become a knowledge revision without an explicit promotion/validation process.

OC08. `invalidates` must mean that the target's prior validity no longer holds or must be withdrawn/reviewed; it is stronger than mere contradiction.

## Revision constraints

OC09. Revision-bound relations such as `verified_against`, `accepted_against`, and publication provenance must preserve the exact revision concerned.

OC10. A later revision must not rewrite the historical meaning of an earlier revision.

## Dependency constraints

OC11. `depends_on` must declare or be inferable as semantic, operational, existential, or provenance dependence where that distinction changes impact behavior.

OC12. `produced_from` does not imply semantic validity of the input.

OC13. `impacts` does not imply `supersedes`.

OC14. `supersedes` does not imply `invalidates`.

## Authority constraints

OC15. Authority is contextual and scoped.

OC16. Agent type, folder ownership, process completion, or previous approval do not by themselves imply authority for a new transition.

OC17. External effects require an explicit authorization relation or decision boundary.

## Event/state separation

OC18. `ObservationEvent` is not `ObservationResult`.

OC19. `DecisionEvent` is not `DecisionOutcome`.

OC20. `VerificationActivity` is not `VerificationResult`.

OC21. `PublicationEvent` is not `PublicationArtifact`.

OC22. Lifecycle state is not automatically an ontology subclass.

## Competency validation

The candidate ontology passes the current phase only when every competency question in `01_competency_questions.md` can be answered by a combination of:

```text
ontology semantics
+ instance data
+ state/dependency/authority models
```

A question that requires folder naming or undocumented convention is evidence of a missing semantic model or an incorrect separation of concerns.

## Formalization gate

Do not create OWL/RDF as a final authority until:

1. the candidate concepts have survived real editorial cases;
2. identity and dependence ambiguities are resolved or explicitly bounded;
3. relation semantics are stable enough to validate;
4. the competency questions have been exercised;
5. an explicit decision chooses whether formal ontology technology is actually needed.
