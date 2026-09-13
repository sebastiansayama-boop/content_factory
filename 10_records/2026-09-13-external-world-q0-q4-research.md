# Research Record — External World Q0–Q4

Date: 2026-09-13
Status: `RESEARCHED / MODEL IMPACT ASSESSED`

## Scope

This record opens the first research cycle from the generic external-system tree. It covers Q0–Q4 and deliberately stops before GitHub-specific implementation research.

Research path:

`L0 External World → L1 External Systems → L2 System Classes → L3 Interaction Semantics → L4 External Action`

Each question was decomposed into material subquestions and investigated across systems engineering, security, provenance, AI governance and protocol semantics. The repository model was inspected before drawing conclusions.

## Q0 — What must Content Factory be able to do to interact with reality outside its own information space?

### Decomposition

Q0.1 What is outside the factory boundary?
Q0.2 What information can cross the boundary?
Q0.3 What actions can cross the boundary?
Q0.4 What external state can be changed?
Q0.5 What evidence can establish that the intended consequence occurred?
Q0.6 What must remain outside factory ownership?

### Sources

- NIST system-boundary terminology: a system boundary separates components authorized as part of a system from separately authorized connected systems. https://csrc.nist.gov/glossary/term/system_boundary
- ISO/IEC/IEEE terminology exposed through ISO: a system boundary is the conceptual interface between a system and its environment; a system is a combination of interacting elements organized for stated purposes.
- NIST SP 800-160: security architecture explicitly models interfaces, interconnections and interactions with external entities and distinguishes functional/security boundaries.
- W3C PROV: provenance represents entities, activities and agents involved in producing or influencing things, including time and responsibility.
- Current repository model: `docs/23_content_factory_operating_model.md`, `docs/10_effect_and_authority_boundaries.md`, `RULES.md`.

### Findings

1. The factory boundary is not a filesystem boundary. It is a semantic/control boundary between factory-owned state and state governed by an external system or environment.
2. Crossing the boundary has at least three distinct purposes: obtain information, cause/prepare an operation, and establish evidence about what happened.
3. The factory can own intent, work specification, accepted revision, authorization decision and internal provenance without owning the external system's state.
4. External outcome cannot be inferred solely from successful internal completion. Independent observation is required when the claim concerns external state or consequence.
5. The factory therefore needs a general ability to `observe → prepare/authorize → execute → observe effect → verify → reconcile → learn`, with the exact subset depending on the external system.

### Classification

`EXTENDS_CURRENT_MODEL` and `SUPPORTS_CURRENT_MODEL`.

The existing model already says the factory does not own the entire ecosystem outcome and separates distribution from external effect. The research makes the boundary more explicit: external interaction is a semantic boundary, not merely a later workflow stage.

### Conclusion

**PROVISIONAL MODEL:** Content Factory should model external interaction as a controlled crossing of a semantic boundary, not as an extension of the internal production pipeline. Its responsibility ends at the point where external state/consequence becomes independently governed; it must retain enough provenance to reconstruct what it intended, authorized, executed, observed and verified.

Confidence: `HIGH` for the boundary principle; `MEDIUM` for the exact generic capability surface.

## Q1 — What is an external system, and what makes its state genuinely external?

### Decomposition

Q1.1 What constitutes a system?
Q1.2 What constitutes a boundary?
Q1.3 Who controls state and mutation rules?
Q1.4 Who controls identity/authorization?
Q1.5 Who can independently reject, delay or transform an operation?
Q1.6 When are two components actually one system rather than connected systems?

### Findings

1. Systems engineering treats a system boundary as the conceptual interface with the environment.
2. NIST distinguishes external systems from organizational systems by ownership/control and trust relationship; connected external systems remain outside the organization's system boundary.
3. NIST system-of-systems terminology recognizes interacting heterogeneous systems that retain their own identities/capabilities while contributing to a larger capability.
4. Therefore physical hosting is not sufficient to determine externality. A component may be technically colocated and still be external if its state, authorization, mutation rules or operational authority are independently governed.
5. Conversely, two networked components can be part of one system if the relevant state and control are governed as one system of interest.

### Operational criterion derived

For Content Factory, treat a state domain as externally owned when at least one material control dimension is outside the factory's authority: state ownership, mutation semantics, authorization authority, independent acceptance/rejection, or independent operational lifecycle.

This is a working criterion, not a universal systems-engineering definition.

### Classification

`EXTENDS_CURRENT_MODEL`.

### Conclusion

Externality is primarily a question of **independent state/control semantics**, not network location, API presence, or folder placement.

Confidence: `HIGH` for the general principle; `MEDIUM` for the proposed factory-specific operational criterion.

## Q2 — Which classes of external systems have materially different semantics?

### Decomposition

Q2.1 Which systems primarily provide information?
Q2.2 Which systems execute mutations?
Q2.3 Which systems publish externally visible artifacts?
Q2.4 Which systems own transactional/business state?
Q2.5 Which systems govern authorization/policy/automation?
Q2.6 Which systems provide independent observation?
Q2.7 Can one external system occupy multiple classes?
Q2.8 Do classes require different core primitives?

### Findings

The research supports distinguishing semantic roles rather than assuming one external-system category:

- source/information systems: external state is primarily queried or retrieved;
- execution systems: the central concern is causing an operation;
- publication systems: externally visible availability/distribution is the effect;
- transaction systems: durable business/financial state is changed;
- control/governance systems: permissions, policy, automation or constraints determine what operations are allowed;
- observation systems: provide evidence about state/effect/consequence.

These are roles, not necessarily mutually exclusive system identities. One system can perform several roles. HTTP itself demonstrates that a generic protocol can expose both read-oriented and state-changing semantics through a uniform interface; method semantics determine intended action and properties such as safety and idempotency.

The current repository already separates publication/effect, verification and authority. The research supports preserving those semantic distinctions without creating six implementation adapters by default.

### Classification

`SUPPORTS_CURRENT_MODEL` + `EXTENDS_CURRENT_MODEL`.

### Conclusion

The factory should distinguish **external interaction semantics/roles** from concrete providers. System class is useful when it changes proof, authority, failure, recovery or observation requirements. It is not sufficient justification for a new primitive.

Confidence: `HIGH` on the role distinction; `MEDIUM` on the eventual minimal primitive set.

## Q3 — What kinds of interaction can occur across the boundary?

### Decomposition

Q3.1 What interactions only read?
Q3.2 What interactions establish a plan?
Q3.3 What interactions establish authority?
Q3.4 What interactions request execution?
Q3.5 What interactions mutate state?
Q3.6 What interactions publish or trigger?
Q3.7 What interactions observe after an action?
Q3.8 What interactions reconcile divergent state?
Q3.9 What interactions recover from partial/unknown outcomes?

### Findings

HTTP semantics provide a concrete authoritative example of separating request purpose from transport: request methods carry intended semantics; safe methods are essentially read-only, while idempotency determines whether repeated identical requests have the same intended effect and therefore affects automatic retry behavior. This demonstrates that interaction semantics cannot be reduced to `API call`.

The broader factory interaction vocabulary should therefore distinguish at least:

`OBSERVE / QUERY / RETRIEVE / PREPARE / AUTHORIZE / EXECUTE / MUTATE / PUBLISH / TRIGGER / OBSERVE_AFTER_EFFECT / RECONCILE / RECOVER / LEARN`.

These are semantic interaction types. They are not yet repository ontology classes and must not be promoted automatically.

### Classification

`EXTENDS_CURRENT_MODEL`.

### Conclusion

The interaction model needs a semantic layer above transports/adapters. A single transport can support multiple interaction semantics, and one semantic interaction may require multiple protocol operations.

Confidence: `HIGH`.

## Q4 — What is the generic structure of an external action?

### Decomposition

Q4.1 What is the intended operation?
Q4.2 What target/state is addressed?
Q4.3 What authority permits it?
Q4.4 What preconditions and exact revision constrain it?
Q4.5 What request is executed?
Q4.6 What does the external system actually process?
Q4.7 What effect occurs?
Q4.8 How is the effect observed?
Q4.9 How is the observation verified?
Q4.10 What later consequence can invalidate the desired outcome?

### Findings

A generic external action must be represented as more than a request/response pair. HTTP semantics explicitly model a client intention, target resource, request semantics and server response; the client interprets the response to determine what to do next. RFC 9457 further demonstrates that a response may carry structured information about a problem rather than merely a success/failure bit.

W3C PROV independently supports the need to preserve entities, activities, agents, responsibility and time so that a causal history can be reconstructed.

Combining these findings with the current factory boundary gives the following working action chain:

`INTENT → TARGET → AUTHORITY → PRECONDITIONS/EXACT REVISION → EXECUTION REQUEST → EXTERNAL PROCESSING → EFFECT → OBSERVATION → VERIFICATION → CONSEQUENCE`

The chain deliberately distinguishes:

`request sent ≠ request accepted ≠ operation completed ≠ external state changed ≠ desired consequence occurred`.

### Classification

`SUPPORTS_CURRENT_MODEL` + `EXTENDS_CURRENT_MODEL`.

### Conclusion

This action chain is the first candidate generic contract for external effects. It should remain a **candidate model** until tested against multiple materially different external systems and failure modes.

Confidence: `HIGH` for the decomposition; `MEDIUM` for its sufficiency as the final contract.

## Cross-question synthesis

The first five questions produce a coherent boundary model:

```text
FACTORY-OWNED INTENT / KNOWLEDGE / REVISION / AUTHORITY
                     ↓
              EXTERNAL BOUNDARY
                     ↓
       INTERACTION SEMANTICS
                     ↓
              EXTERNAL ACTION
                     ↓
              EXTERNAL STATE
                     ↓
             OBSERVATION
                     ↓
              VERIFICATION
                     ↓
             CONSEQUENCE
                     ↓
               LEARNING
```

The central finding is that **external integration is not primarily an API-connectivity problem**. It is a state/control/evidence problem. Transport, credentials and adapters are implementation mechanisms below this semantic layer.

## Repository reconciliation

### Current model

`docs/23_content_factory_operating_model.md` already states that the factory does not own the entire ecosystem outcome, that distribution leads to external effect and learning, and that consequential/externally irreversible work requires an explicit authority boundary.

`RULES.md` requires explicit separation of observation, interpretation, decision and effect; contextual authority; provenance; unknowns; external-world boundary; and evidence before model changes.

### Research classification

- Q0: `SUPPORTS_CURRENT_MODEL / EXTENDS_CURRENT_MODEL`
- Q1: `EXTENDS_CURRENT_MODEL`
- Q2: `SUPPORTS_CURRENT_MODEL / EXTENDS_CURRENT_MODEL`
- Q3: `EXTENDS_CURRENT_MODEL`
- Q4: `SUPPORTS_CURRENT_MODEL / EXTENDS_CURRENT_MODEL`

### Model changes justified now

No new implementation primitive is justified by Q0–Q4 alone.

The research justifies maintaining three explicit conceptual distinctions in subsequent work:

1. external boundary vs internal factory state;
2. interaction semantics vs transport/provider;
3. execution evidence vs external-effect evidence vs consequence evidence.

These distinctions already exist partially in the repository and should be tested before being promoted into new ontology or implementation classes.

## Not proven

- No real external effect was executed by Content Factory in this research cycle.
- No provider-specific integration was proven.
- No generic external-effect contract was implemented.
- No recovery/reconciliation mechanism was proven.
- The proposed action chain has not yet been tested against multiple external-system classes.

## Derived questions

Q0–Q4 generate the next research branches rather than closing the program:

1. Can the proposed external-boundary criterion distinguish internal factory components from connected external systems in ambiguous cases?
2. Which external-system roles actually require different evidence, authority and recovery semantics?
3. Which interaction semantics can be composed into a single external action without losing provenance?
4. What evidence is independently sufficient to distinguish execution from effect for each external-system class?
5. Which parts of the action chain are invariant across GitHub, HTTP APIs, publication platforms, transactional systems and automation/control systems?
6. What failure modes create `UNKNOWN` external outcomes, and what reconciliation evidence is required before retry?

## Decision

`ADOPT_AS_CANDIDATE_MODEL`

Use the Q0–Q4 synthesis as the research baseline for the next cycle. Do not implement a generic external-effect primitive yet.

## Verification after write

Required after repository write:

- fetch this exact record;
- confirm it exists on `main`;
- confirm commit identity;
- compare its claims against `docs/32_external_system_research_tree.md`, `docs/23_content_factory_operating_model.md` and `RULES.md`;
- confirm no implementation/ontology artifact was changed without evidence.
