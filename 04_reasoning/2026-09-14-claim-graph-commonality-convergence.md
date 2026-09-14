# Claim Graph — Commonality, Convergence and Constraints

Reasoning ID: RG-2026-09-14-001
Work item ID: WI-2026-09-13-002
Revision basis: WI-2026-09-13-002-r4
External evidence review: 2026-09-14
Status: SYNTHESIS

## Question

Which minimal claims can support the story about similarities across species without collapsing common ancestry, convergence, physical constraint, ecological constraint, developmental architecture or molecular reuse into one mechanism?

## Epistemic statuses

- `SUPPORTED` — current external evidence directly supports the bounded claim.
- `QUALIFIED` — the core observation is supported, but the claim requires an explicit causal or scope boundary.
- `UNKNOWN` — current evidence is insufficient to support the claim.

## Updated claim graph

```text
C1 Shared ancestry explains many similarities
        |
        +--> C2 Many core cellular systems are deeply conserved
        |
        +--> C3 Lineages inherit molecular/developmental/structural components
                                      |
C4 Recurring functional/environmental problems create selection pressures
        |
        +--> C5 Physical, ecological and developmental constraints can restrict or bias trajectories
                                      |
                                      +--> C6 Similar problems can sometimes produce recurrent phenotypic solutions
                                                              |
                                                              +--> C7 Phenotypic convergence does not imply identical genetic/developmental mechanisms

C3 + C5 + available variation
        |
        +--> C8 Independently evolved phenotypes can incorporate ancient or shared biological components

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

Claim: Similarities shared across distantly related species can be explained by inheritance from common ancestry, although the exact ancestral state may require phylogenetic or model-dependent reconstruction.

Boundary: Superficial similarity alone does not establish homology.

External evidence basis: broad comparative-evolutionary framework; this claim is not used to classify every similarity as homologous.

### C2 — Many core cellular systems are deeply conserved

Status: `SUPPORTED`

Claim: Major components of cellular information processing and other core cellular systems are deeply conserved across diverse cellular life and are consistent with inheritance from ancient common ancestry.

Boundary: This does not constitute a complete inventory of LUCA or prove that every conserved component was already present in exactly its modern form in LUCA.

External evidence basis: comparative genomics / LUCA literature; exact ancestral reconstruction remains model-dependent.

### C3 — Lineages inherit an available biological toolkit

Status: `SUPPORTED`

Claim: Evolution does not begin from an empty design space; lineages inherit molecular, developmental and structural components that can affect which later modifications are accessible.

Boundary: An inherited component does not imply that a particular later phenotype was predetermined.

### C4 — Recurring functional/environmental problems create selection pressures

Status: `SUPPORTED`

Claim: Organisms repeatedly encounter functional requirements and environmental conditions that can impose recurring selection pressures.

Boundary: Similar pressures do not guarantee the same evolutionary outcome; variation, development, ecology and history remain relevant.

External evidence basis: thunniform locomotor convergence and comparative visual-system evidence.

### C5 — Constraints can restrict or bias evolutionary trajectories

Status: `QUALIFIED`

Claim: Physical laws, ecological relationships and genetic/developmental architecture can restrict or bias the set of viable or accessible evolutionary trajectories.

Qualification: The relative contribution of each constraint is trait- and lineage-dependent. A restricted observed trait space does not by itself identify one universal causal mechanism.

External evidence basis: Motani 2002 models physical/hydrodynamic constraints in thunniform swimming; Donley et al. 2004 links hydromechanical demands to selection on locomotor design. These are strong examples of constraint contributing to convergence, not evidence that physics universally determines morphology.

### C6 — Similar problems can produce recurrent phenotypic solutions

Status: `SUPPORTED`

Claim: Under recurring functional problems and relevant constraints, similar phenotypic solutions can evolve independently in different lineages.

Qualification: Use `can`, `may`, or similarly bounded language. Do not state that the same problem necessarily produces the same solution.

External evidence basis: thunniform body-plan convergence across tunas, lamnid sharks, whales and ichthyosaurs; vertebrate/cephalopod camera-eye similarity.

### C7 — Phenotypic convergence does not imply identical underlying mechanisms

Status: `SUPPORTED`

Claim: Independently recurring phenotypes may be produced through different genetic, developmental or anatomical routes.

Boundary: The converse is also important: genetic convergence can occur in multiple forms, so different-looking implementations do not justify a blanket claim of completely unrelated molecular mechanisms.

External evidence basis: 2026 Nature Reviews Genetics review identifies multiple forms of genetic convergence; cephalopod-eye studies show a mixture of shared genes, lineage-specific changes and gene recruitment.

### C8 — Independently evolved phenotypes can incorporate ancient or shared biological components

Status: `SUPPORTED`

Claim: A phenotype can evolve independently at the organ or system level while incorporating ancient or shared genes, regulatory machinery or other biological components.

Qualification: Component-level homology/reuse does not by itself establish homology of the whole phenotype. In the camera-eye case, the evidence supports a mosaic rather than a simple "all independent" or "all inherited" explanation.

External evidence basis: vertebrate/cephalopod eye studies identify conserved developmental genes and shared expression alongside lineage-specific recruitment and structural differences.

### C9 — Similarity must be classified at the level being compared

Status: `SUPPORTED AS BOUNDED SYNTHESIS`

Claim: Homology, phenotypic convergence, parallelism and component reuse can coexist at different analytical levels; therefore similarity should be explained at the level of organ, anatomy, development, gene, protein, function or other relevant unit rather than assigned one global label.

Derivation: C1 + C3 + C6 + C7 + C8.

Boundary: This is a synthesis conclusion, not a claim that every level can always be cleanly classified with current evidence.

### C10 — Evolution has a globally small, fixed universal solution space

Status: `UNKNOWN`

Claim under test: Biological evolution is confined to a small, universal and largely predetermined set of solutions.

Current evidence: insufficient.

Reason: The reviewed cases support recurrent solutions under particular conditions but also show different implementations, component reuse, lineage-specific recruitment and historical/developmental dependence. They do not establish a universal fixed solution set.

## Evidence-to-claim mapping

| External evidence | Claims supported | Status | Boundary |
|---|---|---|---|
| Deep conservation of core cellular systems / LUCA research | C1, C2, C3 | SUPPORTED | Does not reconstruct every LUCA component or exact ancestral state |
| Motani 2002 thunniform convergence | C4, C5, C6 | SUPPORTED | Strong physical-constraint example; not a universal law |
| Donley et al. 2004 tuna/lamnid mechanical convergence | C5, C6 | SUPPORTED | Supports hydromechanical selection pressures and deeper functional convergence |
| Motani & Shimada 2023 skeletal convergence | C5, C6 | SUPPORTED | Multiple shared mechanical features; ecological links remain context-dependent |
| Vertebrate/cephalopod camera eyes | C6, C7, C8, C9 | SUPPORTED | Organ-level similarity coexists with major implementation differences |
| Cephalopod eye developmental/transcriptomic studies | C7, C8, C9 | SUPPORTED | Shared genes and independent recruitment form a mosaic |
| Nature Reviews Genetics 2026 | C7 | SUPPORTED | Genetic convergence has multiple forms; phenotype does not map one-to-one to genotype |

## External source register

1. Motani, R. (2002), *Scaling effects in caudal fin propulsion and the speed of ichthyosaurs*, Nature 415, 309–312. https://www.nature.com/articles/415309a
2. Donley, J.M. et al. (2004), *Convergent evolution in mechanical design of lamnid sharks and tunas*, Nature 429, 61–65. https://www.nature.com/articles/nature02435
3. Motani, R. & Shimada, K. (2023), *Skeletal convergence in thunniform sharks, ichthyosaurs, whales, and tunas*, Scientific Reports 13, 16664. https://www.nature.com/articles/s41598-023-41812-z
4. Yoshida, M. & Ogura, A. (2011), *Genetic mechanisms involved in the evolution of the cephalopod camera eye*, BMC Evolutionary Biology 11, 180. https://pmc.ncbi.nlm.nih.gov/articles/PMC3141435/
5. Kröger, R.H.H. et al. (2023), *Cephalopod versus vertebrate eyes*, Current Biology 33, R1100–R1105. https://pubmed.ncbi.nlm.nih.gov/37875092/
6. Allard, J.B. & Kumar, S. (2026), *The genetic foundations of convergent traits*, Nature Reviews Genetics 27, 563–578. https://www.nature.com/articles/s41576-026-00933-7

## Story spine that survives the evidence boundary

```text
Life inherits biological components from earlier lineages.
        ↓
Organisms repeatedly encounter functional and environmental problems.
        ↓
Physics, ecology, development and inherited architecture can restrict or bias accessible trajectories.
        ↓
Some solutions therefore recur independently.
        ↓
But recurrence does not mean identical construction: different lineages can reach similar phenotypes through different routes while also reusing ancient components.
        ↓
Therefore biological similarity has to be explained at the correct analytical level.
```

## Claims that must not be promoted

1. `Constraints force the same evolutionary solution.` — NOT SUPPORTED.
2. `Similar phenotype means common ancestry.` — NOT SUPPORTED.
3. `Independent phenotype means every underlying component evolved independently.` — NOT SUPPORTED.
4. `Convergent phenotype implies convergent genes.` — NOT SUPPORTED as a general rule.
5. `Evolution searches a globally small fixed set of designs.` — UNKNOWN.
6. `Physics is the sole explanation for convergence.` — NOT SUPPORTED.
7. `All similarities between vertebrate and cephalopod eyes are either wholly homologous or wholly convergent.` — NOT SUPPORTED; the evidence is multi-level/mosaic.

## Research closure condition

The current research question can be closed at the bounded synthesis level if final content only claims:

`inherited components + recurring problems + relevant constraints + available variation → some probability of recurrent solutions`

and explicitly distinguishes this from a universal law of evolutionary design.

If a production assertion requires a stronger causal statement, a quantitative generalization, or a new biological example, reopen external research for that specific assertion before production.

## Conclusion

The external evidence review strengthens the locomotion and camera-eye cases but also makes the camera-eye claim more nuanced: organ-level convergence can coexist with conserved developmental machinery and lineage-specific recruitment. The claim graph therefore remains suitable for editorial work, but the specification must preserve this mosaic rather than describe component reuse as a simple exception.
