# Research Record — Project Operating Memory and Direction Control

Date: 2026-09-13
Status: `RECONCILED / SUPPORTS_ADOPTION_WITH_SCOPE`

## Research question

How should Content Factory preserve project direction, current checkpoints, research, evidence, reusable knowledge, decisions, experiments and creative experience without collapsing them into one undifferentiated memory system?

## External sources consulted

1. ADR GitHub organization — Architectural Decision Records: https://adr.github.io/
2. ADR practices: https://adr.github.io/ad-practices/
3. W3C Provenance Working Group publications / PROV-DM: https://www.w3.org/groups/wg/prov/publications/
4. NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
5. NIST AI RMF Core / governance guidance: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
6. Harvard Business Review — A Better Approach to After-Action Reviews: https://hbr.org/2023/01/a-better-approach-to-after-action-reviews
7. Harvard Business Review — Strategies for Learning from Failure: https://hbr.org/2011/04/strategies-for-learning-from-failure

## Key findings

### ADR / decision records

A durable decision record is useful for preserving one significant decision, its rationale, alternatives/tradeoffs and consequences. A decision log is different from a general knowledge base.

Repository classification: `EXTENDS_CURRENT_MODEL`.

Adaptation: use explicit durable decision records where rationale matters; do not turn every note or implementation detail into an ADR.

### Provenance

W3C PROV separates entities, activities and agents and provides relations for generation, usage and derivation. This supports treating provenance as a relation overlay rather than as one generic knowledge field.

Repository classification: `SUPPORTS_CURRENT_MODEL`.

Adaptation: preserve source → activity/experiment → evidence → interpretation → knowledge/decision relationships where material.

### Governance and documentation

NIST AI RMF treats governance as cross-cutting and emphasizes documentation, differentiated roles, human oversight and continuous lifecycle management.

Repository classification: `SUPPORTS_CURRENT_MODEL` and `EXTENDS_CURRENT_MODEL`.

Adaptation: preserve explicit governance boundaries and checkpoints; do not infer authority from documentation or role names.

### Learning from experience

After-action review practice is explicitly aimed at learning from both failures and successes. This supports a formal learning transition instead of treating metrics or successful outputs as automatic knowledge.

Repository classification: `SUPPORTS_CURRENT_MODEL`.

Adaptation: use `observation/experiment → evidence → interpretation → lesson → knowledge candidate → decision` as the preferred learning transition.

## Reconciliation with current repository

The current repository already separates observation, memory, reasoning, decision, production, verification, effects, learning and durable records. Therefore the research does not justify a new top-level knowledge architecture.

Instead, the repository gains a navigation/control layer across existing zones:

```text
PROJECT MAP
→ CURRENT CHECKPOINT
→ QUESTION
→ RESEARCH / EXPERIMENT / IMPLEMENTATION
→ EVIDENCE
→ INTERPRETATION
→ LESSON
→ KNOWLEDGE
→ DECISION
→ WORK / OUTCOME
→ PROJECT MAP UPDATE
```

This is a projection across existing semantic zones, not a replacement for them.

## Design decision

Adopt:

- `docs/28_project_operating_memory.md` as the semantic operating-memory model;
- `docs/29_project_direction_map.md` as the human-readable navigation and return-point map;
- `model/project-direction-map.yaml` as its machine-readable projection;
- `RULES.md` and `docs/25_chat_repository_operating_protocol.md` as the governing enforcement layer;
- existing `02_memory/` and `09_learning/` zones for reusable knowledge and learning, including creative experience and mechanism knowledge.

Do not add separate top-level `knowledge/`, `mechanisms/`, or `evidence/` folders at this stage.

## What remains unproven

- Whether the direction map remains usable under many simultaneous branches.
- Which parts should later become machine-enforced by CI or schemas.
- Which mechanism records are recurring enough to justify additional structured tooling.
- Which creative learning patterns survive repeated controlled experiments.

## Decision boundary

This research changes repository operating memory and navigation, not the Content Factory execution architecture or ontology. It does not establish production readiness or any external-effect capability.
