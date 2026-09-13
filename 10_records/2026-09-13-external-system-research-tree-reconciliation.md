# Research Record — External-System Research Tree Reconciliation

Date: 2026-09-13
Status: `RECONCILED / ADOPTED_AS_RESEARCH_STRUCTURE`

## Question

Should the external-world research program begin from provider/GitHub mechanics, or from a generic model of crossing the factory boundary into externally owned state?

## Evidence reviewed

- `docs/10_effect_and_authority_boundaries.md` — existing separation of production, acceptance, publication and external effect.
- `RULES.md` — explicit repository/external-world boundary, provenance requirements, unknown handling, research-before-model-change, and post-write verification requirements.
- Existing research record `2026-09-13-project-operating-memory-research.md` — demonstrates that research conclusions are recorded with sources, classification, adaptation, unresolved questions and decision boundary.
- GitHub research already performed in the preceding cycle — demonstrated that GitHub exposes distinct mechanisms for repository objects, commits, refs, authentication/permissions and Actions, but these are implementation evidence for one external system rather than the generic model.

## Finding

The provider-first/GitHub-first framing is too low-level for the global research question. The correct abstraction begins with the external world and recursively decomposes through external systems, interaction semantics, action structure, authority, effect, observation, state/time, uncertainty, reliability, security, provenance, factory integration boundary and generic capabilities. GitHub is a concrete instantiation at the end of this tree.

## Decision

`ADOPT`

Adopt `docs/32_external_system_research_tree.md` as the authoritative research hierarchy and update the seed research program so the initial questions start at the generic boundary rather than GitHub API operations.

## Repository impact

- Added `docs/32_external_system_research_tree.md`.
- Updated `docs/31_research_program_100_questions.md` to make the 100 questions a seed corpus governed by the tree and to define five-level minimum decomposition, contextual source selection, inference boundaries, and post-write verification.
- Preserved the earlier numbered question corpus; no historical research record was rewritten.

## Fixation audit

A research conclusion is considered durably fixed only when the repository contains:

1. the question/decomposition path;
2. sources actually consulted;
3. evidence and contradictions/negative evidence;
4. observed result and inference boundary;
5. conclusion and confidence;
6. explicit decision;
7. repository impact;
8. verification after the write;
9. derived questions/return point.

The new tree contains the structural rule and record requirements. The existing operating-memory research record demonstrates the same conclusion-fixation pattern for the prior research cycle. This record closes the reconciliation between those practices and the new external-system research structure.

## Not proven

This write does not prove that Content Factory can perform external effects. It proves only that the repository now has an explicit research structure for investigating that capability.

## Next legitimate research step

Open Q0–Q4 from the generic tree, decompose each material branch to at least five levels, select context-appropriate sources, and record evidence before introducing or changing external-effect implementation primitives.
