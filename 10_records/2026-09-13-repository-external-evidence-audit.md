# Repository Audit — External Evidence Reconciliation

Date: 2026-09-13
Status: `COMPLETED / DOCUMENTATION AUDIT`
Scope: current `main` branch, learning-loop model, project direction state, runtime/provider claims, external evidence basis.

## Audit rule

Repository state proves what the project contains or has executed. External sources support external principles or documented practices; they do not prove local effectiveness. No external source reviewed here justifies automatic promotion, automatic authority, self-modifying learning policy, or production readiness.

## External sources checked

1. W3C PROV-O is a Recommendation defining a provenance ontology for representing provenance information and its relationships. It supports provenance modelling; it does not establish that a particular local provenance implementation is effective. https://www.w3.org/TR/prov-o/
2. W3C PROV overview identifies provenance, reproducibility, versioning and derivation as core concerns. This supports the repository's separation of provenance and revision semantics, not their local correctness. https://www.w3.org/TR/prov-overview/
3. NIST AI RMF 1.0 defines Govern, Map, Measure and Manage functions and calls for continuous lifecycle risk management, measurement, documentation and continual improvement. NIST currently states that AI RMF 1.0 is being revised, so it is a current reference framework, not a final immutable standard. https://www.nist.gov/itl/ai-risk-management-framework
4. NIST AI RMF Measure guidance supports documenting what cannot or will not be measured and evaluating validity, reliability and context-specific limits. https://airc.nist.gov/airmf-resources/playbook/measure/
5. NIST SP 800-160 supports traceability, objective evidence, validation/verification and lifecycle engineering for trustworthy systems. It is systems-engineering guidance, not empirical proof of Content Factory effectiveness. https://csrc.nist.gov/pubs/sp/800/160/v1/r1/final
6. GRADE provides a structured approach to certainty of evidence and strength of recommendations. It is principally a health-care evidence methodology and therefore supports the general epistemic distinction between evidence certainty and recommendation strength, not a Content Factory-specific scoring scheme. https://www.gradeworkinggroup.org/
7. OpenAI's current model documentation confirms GPT-5.6 Luna (`gpt-5.6-luna`) and availability through the Responses API. This confirms the repository's named default model/provider boundary; it does not prove that the repository has successfully executed a real provider call. https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4

## Reconciliation results

### SUPPORTS_CURRENT_MODEL

- Provenance, revision and derivation should remain explicit rather than collapsed into generic metadata.
- Measurement and governance should distinguish what is measured from what cannot be established.
- Validity, reliability and generalizability are distinct evaluation concerns.
- Lifecycle traceability and objective evidence are appropriate engineering controls.
- `gpt-5.6-luna` is a current OpenAI model identifier and the Responses API is an appropriate provider boundary.

### EXTENDS_CURRENT_MODEL

- External guidance strengthens the repository requirement to record measurement limitations explicitly.
- NIST AI RMF's current revision status should be preserved as source metadata when citing AI RMF guidance.

### CONTRADICTS_CURRENT_MODEL

No substantive external contradiction was found in the audited claims.

### REVEALS_GAP

- External sources do not prove Content Factory production effectiveness.
- The repository still lacks a completed real OpenAI execution proof on the current execution environment.
- The repository still lacks a completed real external-effect proof.
- Learning-loop claims beyond project-demonstrated Q19–Q21 behavior remain empirical hypotheses.

## Repository consistency findings

1. `docs/29_project_direction_map.md` correctly records Learning Loop as `ACTIVE RESEARCH / EXTERNAL PROOF PENDING`.
2. `model/content-factory-map.yaml` correctly records Phase 7 as `research_complete_real_external_proof_pending` and now separates externally supported claims from project-demonstrated claims.
3. `model/project-direction-map.yaml` was stale at audit time: Learning Loop was marked `PARKED`. Corrected to `ACTIVE` in version 3.
4. `README.md` was stale at audit time: its final phase list marked Learning Loop `NOT STARTED`. Corrected to `ACTIVE RESEARCH / EXTERNAL PROOF PENDING`.
5. `10_records/2026-09-13-experiment-001-status.md` correctly remains at `EXECUTION GATE`; no external-effect result has been established.

## Corrections applied

- `model/project-direction-map.yaml` → version 3; Learning Loop synchronized to `ACTIVE`.
- `docs/29_project_direction_map.md` → synchronized current navigation state and external/project evidence labels.
- `model/content-factory-map.yaml` → version 12; `externally_supported_scope` and `project_demonstrated_scope` are now distinct.
- `README.md` → current phase status synchronized.

Commits:
- Audit record: `45a1241ee8b97599f01f2b2a8975c81185886c6e`
- Direction model: `ca54870834bcc6b738272da2620c27a79977e974`
- Direction map: `88e5cb0e7aa9635125a63d9673159aff15cafdc7`
- README: `919eb1b7c8570fe3eaac3a3aa48f85efa76bede0`
- Factory model epistemic labels: `ccdedae6ec749df17e4f9ed3f15160b5c92d960a`

## Proven project state after audit

- Phase 1 bounded durable runtime: project-demonstrated and test-backed.
- Phase 2 provider boundary: implementation and mapping tests exist; real provider execution remains unproven in the current environment.
- Phase 3 real external effect: not proven on `main`.
- Q19–Q21 learning path: project-demonstrated bounded learning/promotion/memory-consumption/decision-change loop.
- Real external outcome evaluating memory: not proven.
- Automatic promotion, automatic authority, self-modifying learning policy and production readiness: not authorized/proven.

## Audit conclusion

The substantive model is consistent with the external evidence reviewed. The main defect found was repository-state synchronization, not a need for new architecture. The repository is now synchronized at the audited boundaries. The next empirical boundary remains: memory-informed decision -> changed execution -> real external outcome -> evaluation -> memory revision.
