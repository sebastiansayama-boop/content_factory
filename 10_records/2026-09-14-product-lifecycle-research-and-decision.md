# 2026-09-14 — Digital Product Lifecycle Research and Decision

Status: `SUPPORTED / MODEL CHANGE`

## Question

What should be the canonical stage-gated process for developing a digital product, what ends each stage, and how should the existing Content Factory ecosystem map to that process without creating a new repository or forcing repository boundaries to become stage ownership?

## External evidence

### GOV.UK Service Manual

GOV.UK defines a service lifecycle with Discovery, Alpha, Beta, Live and Retirement. Discovery is used to understand users, their current behavior, problems and needs before planning, designing or building. User research continues through alpha, beta and live rather than ending after discovery. Alpha is explicitly for testing different solutions and risky assumptions with prototypes; beta takes the selected idea into real implementation and progressively broader use; live focuses on ongoing operation, research, measurement and improvement.

Sources:
- https://www.gov.uk/service-manual/agile-delivery
- https://www.gov.uk/service-manual/user-research/user-research-in-discovery
- https://www.gov.uk/service-manual/agile-delivery/how-the-alpha-phase-works
- https://www.gov.uk/service-manual/agile-delivery/how-the-beta-phase-works
- https://www.gov.uk/service-manual/user-research/user-research-in-live

Classification: `SUPPORTS_CURRENT_MODEL` and `EXTENDS_CURRENT_MODEL`.

### IDEO

IDEO describes human-centered design as moving from understanding people and context through synthesis, idea generation, prototyping and testing, while explicitly warning that the practical process is iterative rather than a rigid universal sequence. This supports keeping the lifecycle gated while allowing bounded iteration inside a stage.

Sources:
- https://www.ideo.com/
- https://designthinking.ideo.com/process

Classification: `SUPPORTS_CURRENT_MODEL`.

## Reconciliation with current repository

The current Content Factory model already separates Discovery/Decision from the factory, defines an explicit Content Demand boundary, separates verification/acceptance/publication/outcome, and requires explicit authority transitions. `RULES.md` also requires evidence-to-decision bridges and prohibits silent promotion across boundaries.

The current model therefore does not need to absorb Discovery into Content Factory. Instead, the ecosystem needs a canonical product lifecycle above the factory, with Content Factory remaining the bounded production system.

Classification: `SUPPORTS_CURRENT_MODEL`.

## Decision

Adopt a nine-stage canonical digital product lifecycle:

```text
0 Product Brief
1 Discovery
2 Problem / Opportunity
3 Product Decision
4 Solution Design & Validation
5 Product Specification
6 Build & Integration
7 Release & Live Operation
8 Learning / Evolution / Retirement
```

The lifecycle is stage-gated. The default movement is one stage forward or one stage backward. Work inside a stage may iterate locally. A stage can end in PROCEED, RETURN, HOLD or STOP.

Persona and CJM are not mandatory stage gates. They are discovery/design instruments produced when they materially improve understanding or decision quality.

The lifecycle deliberately separates:

- evidence from interpretation;
- problem from solution;
- decision from implementation;
- solution validation from production build;
- verification from acceptance;
- acceptance from publication;
- publication from outcome;
- measurement from learning.

## Affected artifacts

- `docs/30_product_development_lifecycle.md`
- `model/product-development-lifecycle.yaml`
- `docs/29_project_direction_map.md` — must be synchronized in the same material cycle

## Known unresolved boundary

`DiscoveryResult → ProductDecision → AuthorizedProductDemand` remains a cross-system ownership gap. This is not resolved by this lifecycle definition. The next legitimate work on that gap must use a bounded real case after the lifecycle gate is accepted.

## Evidence limits

The external sources support the lifecycle structure and iterative/stage-gated principles. They do not prove that the proposed ownership mapping is correct for this specific ecosystem. Ownership remains based on current repository inspection and is explicitly marked unresolved where proof is absent.
