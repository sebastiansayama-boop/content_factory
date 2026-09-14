# 2026-09-14 — Discovery → Content Demand and Rules Consistency Audit

Status: `SUPPORTED / ARCHITECTURE REVIEW`

## Question

After scanning the ten-project ecosystem, determine whether the previously identified capability ownership matrix still reflects the current repositories, whether a Discovery → Content Demand bridge exists, and whether Content Factory governing rules or navigation artifacts have become stale.

## Evidence inspected

Current `content_factory` state at commit `c21be3d2b445b17bd940a9c7971aae67cbd35ffa`, including:

- `RULES.md`
- `docs/14_repository_rules.md`
- `docs/23_content_factory_operating_model.md`
- `docs/24_capability_and_engineering_layer.md`
- `docs/25_chat_repository_operating_protocol.md`
- `docs/29_project_direction_map.md`
- `model/content-factory-map.yaml`

Adjacent repositories inspected for current ownership:

- `ai-creative-os/README.md`
- `whisper-studio/README.md`
- `ai-research-radar/README.md`

External research was also checked for current discovery practice and provenance requirements.

## Findings

### 1. The earlier capability matrix contains one material stale assignment

`ai-creative-os` is archived as of 2026-08-02 and explicitly has no active production path. It must not be treated as an active Discovery owner. Its historical research remains useful evidence but not a current capability provider.

Classification: `CONTRADICTS_PREVIOUS_MATRIX`

### 2. The active discovery surface is fragmented and bounded

`whisper-studio` is an active local-first renderer, but its current route does not implement brief-to-video generation, publishing or analytics. It contains historical research material but its active product contract is rendering, not a general Discovery system.

`ai-research-radar` is currently `PAUSED`. Its retained scope is local research-radar intake, scoring and human review. Its review outcomes explicitly do not trigger product decisions, builds or roadmap changes.

Therefore neither repository currently proves ownership of a canonical cross-project Discovery decision system.

Classification: `REVEALS_GAP`

### 3. The missing architecture is a bridge, not a new content primitive

The Content Factory already models `CONTENT DEMAND` upstream of the factory and `WORK ITEM` as the operational unit. The missing boundary is the normalized transition:

`Discovery evidence → interpreted opportunity/problem → explicit decision → Content Demand`

This should remain outside the factory's production lifecycle. Content Factory should consume an authorized Content Demand; it should not silently infer demand from research, metrics or observations.

Classification: `EXTENDS_CURRENT_MODEL`

### 4. Current external discovery practice supports a continuous, evidence-backed decision boundary

Current 2026 discovery guidance consistently emphasizes connecting outcomes to customer opportunities, candidate solutions and assumption tests, while keeping customer evidence continuously refreshed. This supports an explicit decision layer rather than a one-time persona/CJM documentation phase.

The evidence supports the mechanism, but does not prove that any particular repository in this ecosystem implements it.

Classification: `SUPPORTS_CURRENT_MODEL`

### 5. Provenance remains a cross-boundary requirement

Current provenance practice emphasizes preserving origin and transformation information across systems. This supports carrying evidence references and decision provenance into Content Demand rather than passing an untraceable brief string.

Classification: `SUPPORTS_CURRENT_MODEL`

## Rules audit

The governing rules remain substantively useful, but one description is stale:

- `RULES.md` describes the repository as a "research environment". The repository now contains an executable durable runtime, provider boundary, product workspace and control-plane implementation. The repository is better described as a research-and-development environment for an executable editorial production system.

The following rules remain valid and should be retained:

- evidence before model;
- explicit identity/revision;
- separation of verification, acceptance and publication;
- explicit authority boundaries;
- research before unresolved structural changes;
- smallest sufficient layer;
- no silent promotion of evidence or authority;
- post-write verification;
- explicit project operating memory.

The protocol itself is not obsolete, but it has become more important to distinguish governance rules from project-state assertions. Project-state assertions belong in model/navigation artifacts and should not be frozen into governing rules.

## Decision

1. Do not create a new Discovery repository.
2. Do not reactivate `ai-creative-os` as an active owner.
3. Do not make `whisper-studio` or `ai-research-radar` the canonical owner of the Discovery → Demand boundary without further evidence.
4. Define the Discovery → Content Demand boundary as an explicit cross-system contract owned at the receiving boundary by Content Factory, while preserving discovery evidence and decision authority in their source systems.
5. Treat the producer side of the contract as unresolved until an active system demonstrates the required decision lifecycle.
6. Correct stale repository-state language and navigation statuses without changing unrelated execution architecture.

## Candidate bridge contract

A `ContentDemand` consumed by Content Factory should carry at minimum:

```text
demand_id
revision_id
strategic_intent_ref
opportunity_or_problem_ref
audience_context_ref
requested_outcome
content_job_or_product_intent
knowledge_basis_refs
evidence_refs
decision_ref
decision_status
authority_ref
constraints
acceptance_criteria
release_requirements
success_signals
```

The contract is a candidate consumer boundary, not proof that an upstream producer currently emits all fields.

## Open unknowns

- Which active system should own canonical Discovery decisions.
- Whether Discovery needs one normalized repository or can remain federated behind the contract.
- What authority model should approve a Content Demand across repositories.
- Which real case should be used as the first end-to-end Discovery → Demand proof.

## External research reconciliation

- Continuous discovery / opportunity mapping: `SUPPORTS_CURRENT_MODEL`.
- Provenance across transformations: `SUPPORTS_CURRENT_MODEL`.
- Specific repository ownership of Discovery: `UNCERTAIN`.
- Existing ecosystem implementation of the proposed bridge: `REVEALS_GAP`.

## Next legitimate step

Implement and test the smallest `ContentDemand` contract at the Content Factory intake boundary using one real bounded case. Do not build a general Discovery platform before that case demonstrates the need.
