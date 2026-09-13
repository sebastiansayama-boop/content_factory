# Research Record — Q1 External-Boundary Ambiguity

Date: 2026-09-13
Status: `RESEARCHED / MODEL IMPACT ASSESSED`

## Question

Can the proposed Content Factory external-boundary criterion distinguish internal factory components from connected external systems in ambiguous cases?

Working criterion from Q0–Q4:

> Treat a state domain as externally owned when at least one material control dimension is outside factory authority: state ownership, mutation semantics, authorization authority, independent acceptance/rejection, or independent operational lifecycle.

This cycle tests that criterion against boundary cases rather than assuming that process separation, networking, API availability, hosting, or vendor identity determine externality.

## Research depth

The question was decomposed to five levels before evidence collection:

`Q1`
→ `Q1.1 Boundary semantics`
→ `Q1.1.1 State/control identity`
→ `Q1.1.1.1 Independent mutation and authorization`
→ `Q1.1.1.1.1 Operational classification in ambiguous cases`

The fifth level was expanded into concrete cases because the ambiguity is not resolved by terminology alone.

## Source map

### Primary / authoritative sources

1. NIST CSRC glossary — external information system/component. Defines an external system as outside the organization's authorization boundary and typically outside direct control over required security controls.
2. NIST SP 800-171r3 — boundary protection and managed interfaces. Requires external connections to occur through managed interfaces and treats the external boundary as a security/control boundary.
3. NIST SP 800-160 — systems security engineering. Requires explicit definition of interfaces, interconnections and interactions with external entities and notes that security boundaries may be logical rather than physical.
4. NIST CSRC glossary — interface. Defines an interface as a common boundary between independent systems or modules where interactions take place.
5. W3C PROV Primer / PROV-O — provenance. Separates entities, activities and agents; roles and responsibility can be represented independently of physical deployment.
6. RFC 9110 — HTTP Semantics. Separates resource identity from request semantics and distinguishes safe/idempotent behavior from transport mechanics.

## Evidence

### E1 — Externality is a boundary/control property, not a network property

NIST defines an external information system/component by its position outside an authorization boundary and lack of direct control over relevant controls. NIST SP 800-160 separately requires security interfaces, interconnections and interactions with external entities and recognizes logical as well as physical boundaries.

Implication: `remote` is neither necessary nor sufficient. A local subprocess can be outside a particular control boundary; a remote service can be part of a system's managed architecture for some purposes. The relevant question is which authority and state are being considered.

Classification: `SUPPORTS_CURRENT_MODEL / EXTENDS_CURRENT_MODEL`.

### E2 — External system and external state are different dimensions

A factory may use an external system without transferring ownership of every state domain involved. For example, a managed database service may be externally operated while the logical records stored in it are factory-owned application state. Conversely, an externally operated publishing platform may contain a public artifact whose externally visible state is not controlled by the factory after publication.

Therefore two questions must not be collapsed:

1. Is the system/service used by the factory externally governed?
2. Is the particular state/effect relevant to the current operation externally governed?

The first determines integration/control boundary. The second determines whether the factory can claim or guarantee a state transition.

Classification: `EXTENDS_CURRENT_MODEL`.

### E3 — Process, repository, and module boundaries do not determine semantic ownership

A separate process, package, repository, container or server is not automatically an external system. If the factory controls its lifecycle, mutation semantics, authorization and relevant state, it can remain an internal component despite physical/process separation.

Conversely, a component can be deployed in the same infrastructure and still be externally governed if another authority independently controls its relevant state, permissions, lifecycle or acceptance rules.

This follows the NIST logical-boundary treatment and the general interface concept: the existence of an interface does not itself establish the semantic ownership of the connected systems.

Classification: `EXTENDS_CURRENT_MODEL`.

### E4 — API availability does not determine externality or authority

RFC 9110 demonstrates that transport-level access and semantic action are distinct: the request method supplies semantics, while the target resource is separately identified. NIST boundary guidance similarly distinguishes managed interfaces from the systems on either side.

Therefore `has API` means only that an interaction mechanism exists. It does not establish:

- who owns the target state;
- who can authorize the mutation;
- whether the operation can be rejected or transformed independently;
- whether the factory can verify the resulting state;
- whether the factory has authority to invoke the operation.

Classification: `SUPPORTS_CURRENT_MODEL / EXTENDS_CURRENT_MODEL`.

### E5 — Provenance reinforces the need to distinguish agent, activity, entity and role

W3C PROV models entities, activities and agents separately and allows agents to have roles and responsibility for activities. This means the same physical actor or software provider can participate in different semantic roles without becoming identical to the state or activity itself.

For Content Factory this supports keeping at least these identities distinct:

`factory agent` / `external system` / `external resource or state` / `interaction activity` / `authorization context` / `observation`.

Classification: `SUPPORTS_CURRENT_MODEL / EXTENDS_CURRENT_MODEL`.

## Boundary-case analysis

### Case A — In-process library

Example: a parser or renderer imported into the factory process.

Result: normally `INTERNAL_COMPONENT`.

Reason: process co-location is not the decisive fact; more importantly, the factory controls the relevant lifecycle and state semantics. If a library invokes a separately governed external service, that nested interaction crosses a boundary even though the call originates inside the process.

### Case B — Factory-owned worker in a separate process/container/server

Result: normally `INTERNAL_COMPONENT`.

Reason: operational separation does not by itself create external state/control. If the factory owns the worker's lifecycle, authorization context, state semantics and failure/recovery contract, the worker remains part of the factory system of interest.

### Case C — Managed database service used for factory state

Result: `EXTERNAL_SERVICE / INTERNAL_LOGICAL_STATE`.

Reason: the database provider is externally governed at the infrastructure/service layer, while the application records may remain factory-owned logical state. The integration boundary exists at the service interface, but the factory should not incorrectly classify every stored record as external state.

This is a critical correction to a simplistic `external system = external state` rule.

### Case D — SaaS platform containing a published factory artifact

Result: `EXTERNAL_SYSTEM + EXTERNAL_EFFECT`.

Reason: the SaaS platform independently controls acceptance, storage, visibility, publication rules, identity/permissions and lifecycle. The factory can own the intended artifact/revision before publication, but cannot infer the platform's resulting public state merely from successful request execution.

### Case E — Public information source

Result: `EXTERNAL_SYSTEM`, but usually `NO_FACTORY_MUTATION`.

Reason: the system is external because its source state and acceptance/retention semantics are outside factory control. The factory may retrieve information and preserve a local representation with provenance. Retrieval success does not transfer ownership of the source state to the factory.

### Case F — External webhook/event source

Result: `EXTERNAL_SYSTEM / EXTERNAL_ACTOR`, with an inbound interaction boundary.

Reason: the external system can initiate an event that the factory did not schedule. The factory owns its interpretation and subsequent internal work, but must not treat the external assertion as equivalent to verified external fact without appropriate observation/verification.

### Case G — Third-party API invoked using a factory-controlled credential

Result: `EXTERNAL_SYSTEM`.

Reason: credential possession establishes an authentication mechanism, not ownership of the target system. NIST's external-system definition explicitly centers the authorization/control boundary rather than credential possession.

### Case H — Another component in the same organization

Result: `CONTEXT-DEPENDENT`.

Organizational ownership alone does not decide the system boundary. If the component has independently governed authorization, state, lifecycle or acceptance semantics, it may be external to the factory's system of interest. If those controls are jointly governed as one system for the relevant purpose, it may remain internal.

### Case I — Same vendor / same cloud account / same server

Result: `NOT DETERMINATIVE`.

Commercial ownership, vendor identity and physical hosting do not establish semantic system ownership. The boundary must be evaluated for the specific state and operation.

### Case J — External system accepts a request but asynchronously transforms it

Result: `EXTERNAL_SYSTEM + EFFECT_REQUIRES_OBSERVATION`.

Acceptance is not equivalent to final effect. The external system retains independent processing semantics and may delay, transform, reject later, or produce a state that must be observed independently.

## Mechanism reconstruction

The evidence supports a two-axis boundary model rather than one binary `internal/external` flag.

### Axis A — System/control boundary

Who controls:

`identity → authorization → mutation rules → acceptance/rejection → lifecycle → operational controls`

### Axis B — State/effect boundary

Who controls:

`target state → resulting revision/object → visibility → downstream consequence`

These axes can differ.

Examples:

- managed DB: external service boundary + internal logical state;
- public SaaS publication: external service boundary + external published state;
- internal worker: internal service boundary + internal state;
- public source: external service boundary + external source state, but usually no mutation authority;
- webhook: external actor/system + inbound assertion, followed by factory-owned interpretation/state.

## Proposed classification vocabulary

Do not promote this vocabulary to ontology yet. It is a research classification for testing the model.

`INTERNAL_COMPONENT`
Factory controls the relevant system semantics and state.

`EXTERNAL_SYSTEM`
Relevant system/control semantics are independently governed outside the factory boundary.

`EXTERNAL_SERVICE_INTERNAL_STATE`
The service boundary is external, but the relevant logical state remains factory-owned.

`EXTERNAL_EFFECT`
The operation changes externally governed state or visibility.

`EXTERNAL_OBSERVATION_SOURCE`
The external system supplies evidence about state/consequence without being controlled by the factory.

`BOUNDARY_AMBIGUOUS`
Available evidence is insufficient to classify the relevant boundary.

The classifications are deliberately orthogonal where necessary; they should not become a single mutually exclusive enum without further evidence.

## Contradictions / negative evidence

1. A simplistic rule `different process = external` is contradicted by internally controlled workers and services.
2. A simplistic rule `different network = external` is contradicted by logically unified systems distributed across networks.
3. A simplistic rule `same organization = internal` is contradicted by independently governed subsystems.
4. A simplistic rule `API = external system` confuses interaction mechanism with semantic boundary.
5. A simplistic rule `external provider = external state` confuses service/infrastructure control with application-level logical state.
6. A simplistic binary `internal/external` state classification cannot represent the managed-service case without losing important authority information.

## Inference boundary

Proven by external sources:

- system boundaries can be logical and are tied to control/authorization semantics;
- external systems are outside a relevant authorization boundary and are not directly controlled in the relevant dimensions;
- interfaces separate interacting systems/modules but do not alone define ownership;
- provenance benefits from distinguishing entities, activities, agents, roles and responsibility;
- protocol semantics must be distinguished from transport mechanics.

Inferred for Content Factory:

- the boundary criterion should be evaluated per state domain and operation, not once per provider;
- system/control boundary and state/effect boundary should be represented separately;
- externality should not become a single global boolean attached to every connector.

Not yet proven:

- the proposed classification vocabulary is sufficient for all integration classes;
- every future provider can be represented without additional dimensions;
- the exact machine-readable representation of the two axes;
- whether external state needs a dedicated ontology class or can remain a contextual relation.

## Conclusion

The proposed external-boundary criterion survives the ambiguity tests only after one important refinement:

**Content Factory must distinguish the boundary of an external system/service from the ownership of the particular state or effect involved in an operation.**

Externality is therefore evaluated at the level of the relevant control/state domain and operation, not at the level of network location, process, repository, vendor, API or credential.

The strongest current model is:

`FACTORY SYSTEM / CONTROL BOUNDARY`
`        ↕ interaction interface`
`EXTERNAL SYSTEM / SERVICE CONTROL`

and separately:

`FACTORY-OWNED LOGICAL STATE`
`        ↕ representation / synchronization`
`EXTERNAL STATE / EFFECT`

The two boundaries may align, but they need not.

Confidence: `HIGH` for the distinction; `MEDIUM` for the proposed classification vocabulary.

## Decision

`EXTENDS_CURRENT_MODEL`

Do not implement an ontology class or generic connector primitive from this result alone.

Adopt the distinction as a research constraint for Q2–Q6:

1. system/control boundary must be evaluated separately from state/effect ownership;
2. boundary classification is operation- and state-domain-specific;
3. transport/API/hosting/credential facts are evidence about integration, not proof of externality;
4. ambiguous boundary remains explicit rather than being forced into internal/external.

## Repository impact

No implementation change.

No ontology change.

No new top-level folder.

The result belongs in durable research history and should constrain the next research branches on external-system classes and execution/effect evidence.

## Derived questions

1. For each external-system role, which of the two axes (system control vs state/effect) is decisive for authority?
2. Can one operation cross multiple external boundaries and still preserve one causal/provenance chain?
3. Which external-system classes require independently verifiable state identifiers?
4. When does a managed external service become part of the factory's effective system of interest for a particular claim?
5. What evidence is sufficient to classify a boundary as `AMBIGUOUS` versus merely `EXTERNAL`?
6. How should inbound external assertions and outbound external effects share the same provenance model?

## Post-write verification required

- fetch this exact file from `main`;
- confirm the resulting commit and blob identity;
- compare the conclusion against `docs/32_external_system_research_tree.md` and `RULES.md`;
- confirm that no model/ontology/implementation artifact was changed by this research cycle.
