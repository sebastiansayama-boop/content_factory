# Content Factory Repository Rules

The repository is a research environment for an editorial knowledge and production system.

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
11. Use real cases and experiments to challenge the model before adding new primitives or states.
12. Research external references and inspect relevant repositories before inventing a solution to an unresolved structural question.
13. Do not import Atlas execution machinery (leases, worker recovery, process isolation, token controls) into the editorial model unless a concrete case demonstrates the need.
14. Do not treat the brain analogy as a literal ontology. It is a functional design heuristic.
15. A new top-level folder requires a recurring information type or control boundary that cannot be represented safely by an existing zone.
16. Any current model change must be traceable to evidence, an experiment, a case failure or an explicit decision.

See `docs/14_repository_rules.md` for the expanded rule set and `model/repository-map.md` for the functional map.
