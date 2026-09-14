# 2026-09-14 — Discovery → Content Demand and Rules Consistency Audit

Status: `SUPPORTED / ARCHITECTURE REVIEW / OPENALEX ADAPTER PROOF ADDED`

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
7. Use a provider-neutral external-source adapter as the first Knowledge Layer seam, and prove it on one real provider before adding more adapters.

## Implemented receiving contract

`contracts/content-demand-v1.json` defines the machine-readable receiving contract.

`src/content_factory/content_demand.py` provides the executable `ContentDemand` boundary. It requires an `AUTHORIZED` decision, evidence references, knowledge basis references and acceptance criteria, and preserves decision/authority references when mapping the demand into the existing `WorkItem` model.

`tests/test_content_demand.py` covers authorized round-trip/mapping and rejection of unauthorized or incomplete demands.

This is an intake contract, not an end-to-end Discovery implementation. No upstream repository is declared its canonical producer.

## External Source Adapter proof

`src/content_factory/external_source.py` now defines the minimal provider-neutral `ExternalSourceAdapter` seam and a read-only `OpenAlexAdapter` implementation. The adapter normalizes OpenAlex works into `Source`, retrieves an evidence representation, and derives a claim that explicitly references that evidence.

`src/content_factory/openalex_demand.py` maps that source/evidence/claim chain into the already-existing `ContentDemand`; it does not introduce a second production primitive.

`tests/test_openalex_adapter.py` exercises the complete local chain with a deterministic OpenAlex-shaped HTTP fixture:

`OpenAlex → Source → Evidence → Claim → ContentDemand`

The fixture proves identifier/provenance propagation and the existing AUTHORIZED intake gate. It does not prove a live network call from the repository because the available GitHub connector cannot execute the test suite.

The external source choice is technically justified: current OpenAlex documentation describes a free REST API over its connected graph of works, authors, sources, institutions and topics, with work records exposing DOI, abstract, open-access, authorship, topic and citation-related fields. citeturn0search0turn0search3

## Open unknowns

- Which active system should own canonical Discovery decisions.
- Whether Discovery needs one normalized repository or can remain federated behind the contract.
- What authority model should approve a Content Demand across repositories.
- Whether the evidence representation needs spans/chunks rather than an excerpt for long-form sources.
- Whether Source identity needs stronger cross-provider resolution (DOI/OpenAlex/other identifiers).
- Which real case should be used as the first live network-backed Discovery → Demand proof.
- Whether the existing WorkItem mapping is sufficient once a real producer case is exercised.

## Verification status

The new adapter, bridge and tests were fetched from `main` after writing and are present. The adapter was inspected against the current `ContentDemand` and `WorkItem` shapes.

The GitHub connector available in this cycle does not execute the repository test suite, so the tests are written but **not independently executed here**. Therefore this change proves contract presence and source-level consistency plus deterministic fixture coverage, not passing CI or live network execution.

## External research reconciliation

- Continuous discovery / opportunity mapping: `SUPPORTS_CURRENT_MODEL`.
- Provenance across transformations: `SUPPORTS_CURRENT_MODEL`.
- OpenAlex as a machine-accessible research graph: `SUPPORTS_ADAPTER_CHOICE`.
- Specific repository ownership of Discovery: `UNCERTAIN`.
- Existing ecosystem implementation of the proposed bridge: `REVEALS_GAP`.

## Next legitimate step

Run the repository test suite/CI and one live OpenAlex-backed bounded case. If that passes, generalize only the provider-neutral seam: add the next source adapter (likely Wikidata or GitHub) without changing the ContentDemand or runtime primitives unless the real case demonstrates a gap.
