# Decision — Program 1 Learning Loop model evolution

Date: 2026-09-13
Decision ID: `DEC-2026-09-13-003`
Status: `ADOPTED / BOUNDED MODEL EVOLUTION`

## Context

Program 1 research tested the learning mechanism across epistemology, promotion, retrieval, decision impact, validation, contradiction, lifecycle, attribution, transfer, automation, architecture, governance, measurement, external effect and meta-learning.

External scientific and real-world evidence supports several distinctions that are not explicit enough in the prior Content Factory learning representation. In particular, retrieval is not equivalent to use; use is not equivalent to decision impact; decision impact is not equivalent to outcome improvement; contradiction is not equivalent to invalidation; and stored knowledge can become stale or create competency traps.

## Evidence

Primary external evidence is recorded in `10_records/2026-09-13-learning-loop-program-1-research-synthesis.md`, including peer-reviewed meta-analyses, experimental belief-updating research, external-validity reviews, NIST evaluation guidance, and recent agent-memory security/benchmark research.

## Decision

Evolve the current learning model to explicitly represent the following semantic sequence:

`learning candidate → validation/applicability → reusable knowledge → retrieval → application/decision → execution → external outcome → evaluation → retain/revise/supersede/reject`.

The model must preserve these as distinct claims:

- validity of knowledge;
- applicability to the current context;
- retrieval;
- actual use;
- decision impact;
- execution impact;
- external outcome;
- outcome evidence about the knowledge;
- lifecycle revision.

Contradictory evidence must enter an evaluation/revision path rather than automatically invalidating prior knowledge.

Memory admission is treated as a security/control boundary. External or retrieved content does not gain authority merely by being stored.

## Explicit non-decisions

This decision does not authorize:

- automatic promotion;
- automatic authority from memory;
- vector database adoption;
- knowledge graph adoption;
- separate memory service;
- automatic retry policy;
- self-modifying promotion/retrieval policy;
- production external effects.

Those require separate evidence and decisions.

## Rationale

The evidence is sufficient for a semantic model evolution because multiple independent sources converge on the distinctions above. It is not sufficient to claim that the resulting Content Factory mechanism is empirically effective in production.

## Verification

Verify that:

1. the machine-readable model exposes the new learning distinctions;
2. the human-readable operating-memory model describes the same boundaries;
3. the direction map records the new proven/unproven boundary;
4. the research record and decision are immutable history;
5. no implementation mechanism is introduced solely from this research.

## Remaining proof boundary

The next unresolved empirical boundary is:

`memory-informed decision → changed execution → real external outcome → evaluation of memory → memory revision`.

A real external case is required before claiming L7–L10 maturity.
