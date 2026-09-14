# 2026-09-14 — Discovery → Content Demand and Rules Consistency Audit

Status: `SUPPORTED / ARCHITECTURE REVIEW / INTAKE CONTRACT IMPLEMENTED`

## Question

After scanning the ten-project ecosystem, determine whether the previously identified capability ownership matrix still reflects the current repositories, whether a Discovery → Content Demand bridge exists, and whether Content Factory governing rules or navigation artifacts have become stale.

## Findings

The earlier capability matrix contained one material stale assignment: `ai-creative-os` is archived and must not be treated as an active Discovery owner. `whisper-studio` is an active local-first renderer rather than a general Discovery system, and `ai-research-radar` is paused with review outcomes that do not trigger product decisions. No currently inspected active repository proves canonical ownership of the upstream Discovery decision lifecycle.

The missing architecture is therefore the normalized transition:

`Discovery evidence → interpreted opportunity/problem → explicit decision → Content Demand`

This remains outside the factory production lifecycle. Content Factory consumes an authorized Content Demand and must not silently infer demand from research, metrics, observations or candidate opportunities.

Current external discovery practice supports a continuous, evidence-backed decision boundary rather than treating persona/CJM documentation as the end of Discovery. Provenance practice supports carrying evidence and decision references across the system boundary. These findings support the mechanism but do not prove local implementation.

## Rules audit

The governing rules remain substantively useful. One stale project-description sentence was corrected in `RULES.md`: the repository is now described as a research-and-development environment for an executable editorial knowledge and production system.

The evidence-before-model rule, identity/revision requirements, separation of verification/acceptance/publication, authority boundaries, research gate, smallest sufficient layer, no-silent-promotion rules, post-write verification and project operating memory remain valid.

Project-state assertions should remain in model/navigation artifacts rather than becoming frozen governing rules.

## Decision

1. Do not create a new Discovery repository.
2. Do not reactivate `ai-creative-os` as an active owner.
3. Do not make `whisper-studio` or `ai-research-radar` the canonical owner of the Discovery → Demand boundary without further evidence.
4. Define the Discovery → Content Demand boundary as an explicit receiving-side contract in Content Factory while preserving discovery evidence and decision authority in source systems.
5. Keep producer ownership unresolved until an active system demonstrates the required decision lifecycle.
6. Change no unrelated execution architecture.

## Implemented receiving contract

`contracts/content-demand-v1.json` defines the machine-readable receiving contract.

`src/content_factory/content_demand.py` provides the executable `ContentDemand` boundary. It requires an `AUTHORIZED` decision, evidence references, knowledge basis references and acceptance criteria, and preserves decision/authority references when mapping the demand into the existing `WorkItem` model.

`tests/test_content_demand.py` covers authorized round-trip/mapping and rejection of unauthorized or incomplete demands.

This is an intake contract, not an end-to-end Discovery implementation. No upstream repository is declared its canonical producer.

## Open unknowns

- Which active system should own canonical Discovery decisions.
- Whether Discovery needs one normalized repository or can remain federated behind the contract.
- What authority model should approve a Content Demand across repositories.
- Which real case should be used as the first end-to-end Discovery → Demand proof.
- Whether the existing WorkItem mapping is sufficient once a real producer case is exercised.

## Verification status

The new contract, executable boundary and tests were fetched from `main` after writing and are present. The executable boundary was inspected against the current `WorkItem` runtime shape.

The GitHub connector available in this cycle does not execute the repository test suite, so the tests are written but **not independently executed here**. Therefore this change proves contract presence and source-level consistency, not CI/test execution.

## External research reconciliation

- Continuous discovery / opportunity mapping: `SUPPORTS_CURRENT_MODEL`.
- Provenance across transformations: `SUPPORTS_CURRENT_MODEL`.
- Specific repository ownership of Discovery: `UNCERTAIN`.
- Existing ecosystem implementation of the proposed bridge: `REVEALS_GAP`.

## Next legitimate step

Run one real bounded Discovery → Content Demand case through the receiving contract. Use that case to determine whether the contract is sufficient and whether an active upstream system can legitimately produce it. Do not create a general Discovery platform before that proof.
