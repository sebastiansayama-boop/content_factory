# Claim Graph — Commonality, Convergence and Constraints

Reasoning ID: RG-2026-09-14-001
Work item ID: WI-2026-09-13-002
Revision basis: WI-2026-09-13-002-r3
Status: SYNTHESIS
Date: 2026-09-14

## Question

Which minimal claims can support the story about similarities across species without collapsing common ancestry, convergence, physical constraint, ecological constraint, developmental architecture or molecular reuse into one mechanism?

## Epistemic statuses

- `SUPPORTED` — current evidence directly supports the bounded claim.
- `QUALIFIED` — the core observation is supported, but the claim requires an explicit boundary or causal qualification.
- `UNKNOWN` — current evidence in this work item is insufficient to support the claim.

## Minimal claim graph

```text
C1 Shared ancestry explains many similarities
        |
        +--> C2 Extant cellular life retains deeply conserved biological machinery
        |
        +--> C3 Inherited architecture supplies an available biological toolkit
                                      |
C4 Recurring functional/environmental problems create recurring selection pressures
        |
        +--> C5 Physical, ecological and developmental constraints filter viable trajectories
                                      |
                                      +--> C6 Similar problems can produce recurrent phenotypic solutions
                                                              |
                                                              +--> C7 Recurrent phenotype does not imply identical genetic/developmental mechanism

C3 + C5 + accessible variation
        |
        +--> C8 Independent complex structures can reuse ancient components

C6 + C7 + C8
        |
        +--> C9 Similarity must be classified at the level being compared

C6/C7/C8
        |
        +--> C10 Evolution has a globally small, fixed universal solution space [UNKNOWN]
```

## Claims

### C1 — Common ancestry explains many shared biological features

Status: `SUPPORTED`

Claim: Similarities shared across distantly related species can be explained by inheritance from common ancestry, although the exact ancestral state may require model-dependent reconstruction.

Evidence refs: initial common-ancestry evidence recorded in WI-2026-09-13-002-r3.

Boundary: Do not infer that every shared trait or sequence is homologous solely from superficial similarity.

### C2 — Deep biological machinery can be conserved across extant cellular life

Status: `SUPPORTED`

Claim: Major components of cellular information processing and energy metabolism are deeply conserved across cellular life and are consistent with inheritance from ancient common ancestry.

Evidence refs: initial universal-cellular-foundations evidence recorded in WI-2026-09-13-002-r3.

Boundary: The work item has not yet synthesized a complete universal-cellular inventory or reconstructed every component to LUCA.

### C3 — Ancestry supplies an inherited biological toolkit

Status: `SUPPORTED`

Claim: Evolution does not begin from an empty design space; lineages inherit molecular, developmental and structural components that affect which subsequent modifications are accessible.

Evidence refs: WI-2026-09-13-002-r3, Finding 4 and Finding 8.

Boundary: The existence of an inherited toolkit does not imply that a particular later phenotype was predetermined.

### C4 — Recurring functional/environmental problems create recurring selection pressures

Status: `SUPPORTED`

Claim: Organisms repeatedly encounter functional requirements and environmental conditions that impose selection pressures on viable phenotypes.

Evidence refs: locomotion and visual-system convergence evidence in WI-2026-09-13-002-r3.

Boundary: Similar selection pressures do not guarantee convergence; contingency, variation, development and historical context remain relevant.

### C5 — Constraints filter viable evolutionary trajectories

Status: `QUALIFIED`

Claim: Physical laws, ecological relationships and genetic/developmental architecture can restrict or bias the set of viable or accessible evolutionary trajectories.

Evidence refs: WI-2026-09-13-002-r3, Findings 1–4 and 7.

Qualification: The relative contribution of each constraint is trait- and lineage-dependent. Restricted observed trait space does not identify one universal causal mechanism.

### C6 — Similar problems can produce recurrent phenotypic solutions

Status: `SUPPORTED`

Claim: Under recurring functional problems and constraints, similar phenotypic solutions can evolve independently in different lineages.

Evidence refs: thunniform locomotor convergence and vertebrate/cephalopod camera-eye convergence in WI-2026-09-13-002-r3.

Qualification: "Can" and "elevated probability" are appropriate. "Will" or "must" is not supported.

### C7 — Phenotypic convergence does not imply identical underlying mechanisms

Status: `SUPPORTED`

Claim: Independently recurring phenotypes may be produced through different genetic, developmental or anatomical routes.

Evidence refs: WI-2026-09-13-002-r3, Finding 5 and visual-system evidence.

Boundary: Molecular convergence can also recur independently, so the converse claim that genetic differences necessarily imply different adaptive mechanisms is invalid.

### C8 — Independent complex structures can reuse ancient biological components

Status: `SUPPORTED`

Claim: A phenotype can evolve independently at the organ or system level while incorporating homologous genes, regulatory machinery or other ancient components.

Evidence refs: WI-2026-09-13-002-r3, Finding 8.

Qualification: Component homology does not by itself establish homology of the whole phenotype.

### C9 — Similarity must be classified at the level being compared

Status: `SUPPORTED`

Claim: Homology, phenotypic convergence and component reuse can coexist at different analytical levels; therefore similarity should be explained at the level of organ, anatomy, development, gene, protein, function or other relevant unit rather than assigned one global label.

Derivation: C1 + C3 + C6 + C7 + C8.

Evidence class: `SUPPORTED AS BOUNDED SYNTHESIS`.

This is a reasoning conclusion, not a direct single-source observation.

### C10 — Evolution has a globally small, fixed universal solution space

Status: `UNKNOWN`

Claim under test: Biological evolution is confined to a small, universal and largely predetermined set of solutions.

Current evidence: insufficient.

Reason: The reviewed cases support restricted/biaised trajectories and recurrent solutions, but they also show multiple implementations, historical contingency and different genetic/developmental routes. These observations do not establish a universal fixed solution set.

## Evidence-to-claim mapping

| Evidence pattern | Claims supported | Status | Interpretation boundary |
|---|---|---|---|
| Deeply conserved cellular machinery | C1, C2, C3 | SUPPORTED | Exact ancestral reconstruction remains model-dependent |
| Tuna/shark/whale/ichthyosaur locomotor convergence | C4, C5, C6 | SUPPORTED | Strong case for physical constraint; not a universal rule |
| Quantitative hydromechanical analysis | C5, C6 | SUPPORTED | Supports mechanism, not inevitability |
| 9,963-bird trait/niche analysis | C4, C5, C6 | QUALIFIED | Trait-space recurrence does not isolate one causal factor |
| Restricted mammal/bird strategy space | C5 | QUALIFIED | Restricted occupancy is not a single-mechanism explanation |
| Genetic/developmental constraint synthesis | C3, C5, C7 | SUPPORTED | Strength varies by trait |
| Vertebrate/cephalopod camera eyes | C4, C5, C6, C7 | SUPPORTED | Same broad function, different architecture |
| Ancient visual-development components | C3, C8, C9 | SUPPORTED | Component reuse does not make the whole organ homologous |

## Story spine that survives the evidence boundary

```text
Life inherits a biological toolkit.
        ↓
Organisms repeatedly face functional and environmental problems.
        ↓
Physics, ecology, development and inherited architecture filter what is viable or accessible.
        ↓
Some solutions therefore recur independently.
        ↓
But recurrence does not mean identical construction: different lineages can reach similar outcomes by different routes while reusing ancient components.
        ↓
Therefore biological similarity has to be explained at the correct level rather than treated as one phenomenon.
```

## Claims that must not be promoted

1. `Constraints force the same evolutionary solution.` — NOT SUPPORTED.
2. `Similar phenotype means common ancestry.` — NOT SUPPORTED.
3. `Independent phenotype means every underlying component evolved independently.` — NOT SUPPORTED.
4. `Convergent phenotype implies convergent genes.` — NOT SUPPORTED as a general rule.
5. `Evolution searches a globally small fixed set of designs.` — UNKNOWN.
6. `Physics is the sole explanation for convergence.` — NOT SUPPORTED.

## Research closure condition

The current research question can be closed at the bounded synthesis level if the final content only claims:

`inherited toolkit + recurring problems + constraints + accessible variation → some probability of recurrent solutions`

and explicitly distinguishes this from a universal law of evolutionary design.

The remaining unresolved question is not whether convergence exists. It is how far this explanatory model generalizes across additional biological domains and how quantitatively the relative contributions of constraint, variation, development, ecology and historical contingency can be estimated.

## Conclusion

The two stress tests—locomotion and vision—support the same bounded explanatory structure. The claim graph therefore provides a sufficient intermediate representation for editorial work without promoting the broader universal-solution-space hypothesis.

Confidence: moderate-to-high for C1, C2, C6, C7 and C8; moderate for the multi-factorial formulation of C5; insufficient for C10.

Next legitimate step: use this graph as the epistemic boundary for the content story and only reopen broad biological research if an editorial claim exposes a specific unsupported edge.
