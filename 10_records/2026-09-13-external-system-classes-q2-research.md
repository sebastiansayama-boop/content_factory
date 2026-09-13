# Research Record — Q2 External-System Classes

Date: 2026-09-13
Status: `RESEARCHED / MODEL IMPACT ASSESSED`

## Question

Which external-system roles actually require different evidence, authority and recovery semantics?

The prior Q0–Q4 model proposed six semantic roles: source/information, execution, publication, transaction, control/governance, and observation. Q1 then established that system/control boundary and state/effect ownership are separate axes. This cycle tests whether the six roles correspond to materially different proof and control requirements, or whether they are merely provider categories.

## Research depth

The question was decomposed to five levels before evidence collection:

`Q2`
→ `Q2.1 Semantic role`
→ `Q2.1.1 State/effect behavior`
→ `Q2.1.1.1 Authority and evidence requirements`
→ `Q2.1.1.1.1 Failure/recovery consequences`

Each role was then compared across the same dimensions rather than evaluated independently.

## Source map

### Primary / authoritative sources

1. NIST SP 800-160 Rev. 1 — systems engineering; explicit interfaces, interconnections, interactions, security context and boundaries.
2. W3C PROV Primer / PROV-O — provenance entities, activities, agents, roles and responsibility.
3. RFC 9110 — HTTP semantics; request intent, target resources, safe/idempotent behavior and retry implications.
4. NIST AI RMF Core — third-party components, governance, testing, human oversight and contingency processes.

### Comparative semantic evidence

The same semantic dimensions were tested against information retrieval, execution, publication, transactional mutation, control/governance, and observation interactions. The comparison is deliberately provider-neutral; no GitHub-specific mechanism is used as the model.

## Common comparison dimensions

Every external role was evaluated against:

1. primary state relationship;
2. whether the factory requests mutation;
3. authority sensitivity;
4. minimum execution evidence;
5. minimum effect evidence;
6. observation independence;
7. retry/idempotency sensitivity;
8. recovery/reconciliation requirement;
9. consequence sensitivity;
10. provenance identity requirements.

This prevents the role names themselves from becoming the architecture.

## Evidence and analysis

### R1 — Source / information role

Primary semantic job: obtain information whose authoritative state is outside the factory.

Typical interactions: `OBSERVE / QUERY / RETRIEVE`.

State relationship: external source state; local copy or extracted representation may become factory-owned state.

Authority: usually authority to read, not authority to mutate the source.

Evidence requirement: identify the source, retrieval activity, retrieval time/context, representation or revision observed, and provenance of the resulting factory artifact. Successful retrieval proves access and acquisition, not truth of the source content or persistence of the source state.

Recovery: normally re-retrieval, freshness assessment, provenance comparison, and conflict handling. Duplicate retrieval is usually safer than duplicate mutation, but freshness and source volatility remain material.

Consequence sensitivity: primarily epistemic. A bad source claim can propagate into production even when the retrieval technically succeeded.

Classification: materially distinct for evidence and freshness semantics, but does not require a dedicated implementation primitive by itself.

### R2 — Execution role

Primary semantic job: request an operation whose processing is performed by an external execution system.

Typical interactions: `PREPARE / AUTHORIZE / EXECUTE / TRIGGER`.

State relationship: operation state may be external and may transition asynchronously.

Authority: high. Possession of connectivity or credentials is not equivalent to contextual authorization for a particular operation.

Evidence requirement: preserve operation identity where available, exact request/revision, authorization context, response/acceptance evidence, and later execution/effect observation where the operation is consequential.

Recovery: strongly dependent on idempotency, deduplication and ability to observe the external operation after communication failure. RFC 9110 explicitly distinguishes idempotent operations because automatic retry can be safe when intended effect is unchanged; non-idempotent operations require stronger detection/reconciliation before retry. citeturn0search0turn0search5

Consequence sensitivity: potentially high because execution can cause downstream mutations.

Classification: materially distinct in authority and uncertainty/recovery semantics.

### R3 — Publication role

Primary semantic job: make a content artifact externally available or visible.

Typical interactions: `PUBLISH / EXECUTE / OBSERVE_AFTER_EFFECT`.

State relationship: factory-owned artifact/revision crosses into externally governed visibility/state.

Authority: explicit publication authority is required; content acceptance/verification inside the factory does not itself authorize publication.

Evidence requirement: exact artifact/revision published, target identity, publication request, external acceptance/operation identity where available, resulting external object/URL/revision, and independent observation of externally visible state when consequential.

Recovery: must distinguish request failure from unknown publication outcome. Repeating a publication request may duplicate or overwrite depending on provider semantics; therefore idempotency or reconciliation is material.

Consequence sensitivity: high because publication crosses the factory's information boundary and may be externally visible and difficult to reverse.

Classification: materially distinct because external visibility/effect must be proven, not inferred from internal production completion.

### R4 — Transaction / durable business-state role

Primary semantic job: change externally governed durable state with business, financial, entitlement or other consequential meaning.

Typical interactions: `AUTHORIZE / EXECUTE / MUTATE / OBSERVE_AFTER_EFFECT / RECONCILE`.

State relationship: external authoritative state is the object of the operation.

Authority: strongest sensitivity. Scope, identity, conditions, limits and often explicit human or policy authorization matter.

Evidence requirement: target identity, precondition/current revision, exact mutation, authorization context, transaction/operation identity, authoritative result, and independent post-state observation where possible.

Recovery: reconciliation is often mandatory before retry when outcome is ambiguous. A technical timeout cannot safely be interpreted as failed mutation. Compensation may be required where reversal exists, but compensation is not equivalent to erasing the original effect.

Consequence sensitivity: very high.

Classification: materially distinct from ordinary execution because state change itself is the primary authoritative result and duplicate execution may be harmful.

### R5 — Control / governance role

Primary semantic job: determine or constrain whether another operation is permitted, how it is bounded, or how automation behaves.

Typical interactions: `QUERY / AUTHORIZE / PREPARE / OBSERVE / RECONCILE`.

State relationship: policy, permission, configuration, workflow or control state.

Authority: the central semantic concern. A control system can change what operations are possible without being the target of the final business/content effect.

Evidence requirement: policy/permission identity, version or revision, applicable scope, actor/agent, decision/authorization result, effective time, and relevant constraints.

Recovery: stale or changed policy can invalidate an otherwise technically valid execution plan. Reconciliation therefore includes checking whether the authorization/control state remains applicable.

Consequence sensitivity: indirect but potentially system-wide; a wrong control decision can amplify many subsequent operations.

Classification: materially distinct in authority semantics and temporal validity, but should not be confused with execution itself.

### R6 — Observation role

Primary semantic job: provide independent evidence about state, effect or consequence.

Typical interactions: `OBSERVE / QUERY / RETRIEVE / VERIFY`.

State relationship: observation source may be external and independently governed.

Authority: often read authority; independence from the actor that performed the original mutation is the key semantic property.

Evidence requirement: source identity, observation time, observed object/state identity, representation/revision, and relationship to the claim being verified.

Recovery: repeated observation, alternate observation source, staleness detection and conflict resolution. An observation source can itself be unavailable or inconsistent.

Consequence sensitivity: depends on what claim it verifies; its importance is epistemic rather than necessarily mutational.

Classification: materially distinct because its job is evidence about another activity/effect, not execution of that effect.

## Cross-role result

The six roles do not form six independent implementation primitives.

They differ materially along a smaller set of semantic dimensions:

### Dimension A — State relationship

`READ_EXTERNAL_STATE`
`MUTATE_EXTERNAL_STATE`
`CONTROL_AUTHORIZATION_STATE`
`OBSERVE_EXTERNAL_EFFECT`
`PUBLISH_EXTERNAL_VISIBILITY`

### Dimension B — Authority sensitivity

Low/ordinary read authority → scoped operation authority → consequential mutation/publication authority → control-policy authority.

### Dimension C — Evidence target

`SOURCE_REPRESENTATION`
`REQUEST/OPERATION`
`EXTERNAL_STATE/EFFECT`
`AUTHORIZATION/POLICY DECISION`
`OBSERVED STATE/CONSEQUENCE`

### Dimension D — Recovery mode

`RETRIEVE_AGAIN`
`RETRY_IF_IDEMPOTENT`
`RECONCILE_BEFORE_RETRY`
`RECHECK_AUTHORITY`
`REPEAT_OBSERVATION`
`COMPENSATE_WHERE_SUPPORTED`

These dimensions explain most of the semantic differences without requiring one connector type per role.

## Mechanism reconstruction

The strongest model emerging from the comparison is therefore:

`ROLE`
→ determines the semantic job;

`STATE/EFFECT RELATION`
→ determines what can actually change or be observed;

`AUTHORITY`
→ determines what the factory is permitted to request;

`EVIDENCE CONTRACT`
→ determines what must be recorded to substantiate the claim;

`RECOVERY SEMANTICS`
→ determines what may safely happen after failure or uncertainty.

This is consistent with NIST's treatment of interfaces/interactions as requiring explicit security context and with W3C PROV's separation of activities, entities, agents and roles. citeturn0search48turn0search1

RFC 9110 provides a concrete example of the same principle: a uniform transport can expose semantically different operations, and properties such as safety and idempotency affect whether automation and retry are appropriate. citeturn0search0turn0search2

NIST AI RMF also treats third-party components as a distinct governance concern, including documented risk controls, testing and contingency processes, reinforcing that provider integration cannot be reduced to connectivity alone. citeturn0search9

## Contradictions / negative evidence

1. `one external role = one connector primitive` is not supported. The same transport/provider can expose multiple roles.
2. `execution = effect` is contradicted by asynchronous processing and independent observation requirements.
3. `publication = ordinary execution` loses the distinction between internal artifact verification and externally visible state.
4. `transaction = generic mutation` loses stronger authority, reconciliation and consequence semantics.
5. `observation = passive read` is incomplete: observation has an evidentiary role and therefore provenance/independence requirements.
6. `control = execution` collapses authorization/policy state into the operation it governs.
7. `credentials = authority` is not supported; authority is contextual and scoped.

## Inference boundary

### Proven by external sources

- Interfaces and interactions across system boundaries have semantic/security implications beyond transport. citeturn0search48
- Provenance benefits from explicit entities, activities, agents and roles/responsibility. citeturn0search1turn0search7
- Request semantics and retry safety depend on operation semantics such as safety and idempotency, not merely transport success. citeturn0search0
- Third-party components require explicit governance, risk controls, testing and contingency handling in relevant AI-system contexts. citeturn0search9

### Inferred for Content Factory

- The six proposed roles should remain semantic roles rather than top-level provider classes.
- Evidence, authority and recovery should be attached to the semantic operation/state relationship rather than merely to the connector.
- Observation should be modeled as an evidentiary activity that can be independent of the actor performing the original operation.
- Publication and transaction semantics deserve stronger external-effect boundaries than ordinary execution.

### Not yet proven

- The four dimensions above are sufficient for every future external-system class.
- A single generic operation/evidence contract can represent all six roles without role-specific constraints.
- The exact minimum evidence set for each operation can be standardized now.
- The factory can safely compose multiple roles into one action without losing authority/provenance.

## Conclusion

The six external-system roles are useful as **semantic roles**, but they are not six architectural primitives.

The research identifies four deeper dimensions that actually explain why the roles differ:

`STATE/EFFECT RELATION`
`AUTHORITY SENSITIVITY`
`EVIDENCE TARGET`
`RECOVERY SEMANTICS`

Therefore the candidate model should move from:

`EXTERNAL SYSTEM CLASS → CONNECTOR`

toward:

`SEMANTIC ROLE + STATE/EFFECT RELATION + AUTHORITY + EVIDENCE + RECOVERY`

Confidence: `HIGH` that the six roles should remain semantic rather than provider primitives; `MEDIUM` that the four dimensions are the final minimal basis.

## Decision

`EXTENDS_CURRENT_MODEL`

No implementation primitive is justified yet.

Adopt the following research constraints for Q3–Q6:

1. classify external interactions by semantic role, not provider;
2. evaluate state/effect relation independently from system identity;
3. require authority semantics appropriate to the operation;
4. define evidence around the claim being made, not merely around request completion;
5. choose recovery behavior from operation semantics, especially idempotency and external-state observability;
6. keep observation semantically distinct from execution.

## Repository impact

No implementation change.
No ontology change.
No new top-level folder.

This result is durable research history only. It constrains the next research branch on composition of interaction semantics and evidence preservation.

## Derived questions

1. Can multiple semantic interactions compose into one external action without losing provenance and authority boundaries?
2. What is the minimum evidence contract for each state/effect relation?
3. Can an action cross source → execution → publication → observation roles while retaining one causal identity?
4. When should observation be required to be independent from the executing provider?
5. Which recovery semantics can be selected mechanically from operation properties such as idempotency, reversibility and observability?
6. Can the same external operation simultaneously have control, execution and publication roles without collapsing their distinct authority/evidence requirements?

## Post-write verification

Required:

- fetch this exact record from `main`;
- confirm commit and blob identity;
- compare conclusions against Q0–Q4, Q1 ambiguity research, `docs/32_external_system_research_tree.md` and `RULES.md`;
- confirm no model, ontology or implementation artifact changed in this cycle.
