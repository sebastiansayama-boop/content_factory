# External-System Research — Q3: Can multiple semantic interactions compose into one external action without losing provenance and authority?

Date: 2026-09-13
Research branch: External World → External Systems → System Classes → Interaction Semantics → Composition
Status: COMPLETE FOR CURRENT SCOPE
Decision: EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE
Confidence: HIGH for the core composition principle; MEDIUM for a future generic contract

## 1. Question

Can multiple semantic interactions compose into one external action without losing causal provenance, authority boundaries, and recoverability?

The current model distinguishes interactions such as `AUTHORIZE`, `PREPARE`, `EXECUTE`, `MUTATE`, `PUBLISH`, `OBSERVE_AFTER_EFFECT`, `RECONCILE`, and `RECOVER`. The question is whether these can be composed into one externally meaningful action without collapsing them into one undifferentiated operation.

## 2. Decomposition

### Q3.1 — Action composition

Can several interaction steps be treated as one logical external action?

### Q3.1.1 — Causal identity and provenance

Can the steps be linked so that the factory can reconstruct that they belong to one causal action while retaining their individual activities and outputs?

### Q3.1.1.1 — Authority continuity

Can authority be carried across the composed action without assuming that authorization of one step automatically authorizes every later step?

### Q3.1.1.1.1 — Partial completion and failure

What happens if preparation, execution, publication, or observation succeeds only partially, or if the boundary fails between two steps?

### Q3.1.1.1.1.1 — Recovery and reconciliation

Can the factory determine which steps actually happened, which external states resulted, and whether a retry is safe, without fabricating continuity from the internal action record?

This sixth level is required because the evidence shows that composition becomes materially different once distributed failure and ambiguous responses are introduced.

## 3. Source map

### A. Provenance and responsibility

1. W3C PROV Data Model / PROV Semantics.
2. W3C PROV-O.

Relevant mechanisms:
- entities, activities, and agents are distinct provenance concepts;
- derivation can connect entities through explicit activities, usage, and generation;
- delegation can express one agent acting for another for a specific activity.

### B. Distributed causal correlation

3. W3C Trace Context.

Relevant mechanism:
- a distributed trace has a common trace identity across participating components;
- individual requests remain identifiable within that larger trace;
- propagation crosses process, network, and security boundaries.

### C. Interaction and retry semantics

4. RFC 9110 HTTP Semantics.

Relevant mechanisms:
- request methods carry semantic meaning;
- idempotency is a property relevant to repeating an operation after communication failure;
- non-idempotent requests should not be automatically retried unless the client has additional knowledge or a way to detect whether the original operation was applied;
- recovery can require inspecting target state before retry.

### D. System boundaries and interactions

5. NIST SP 800-160, Systems Security Engineering.

Relevant mechanism:
- interfaces, interconnections, and interactions with external entities are security-relevant architectural relationships;
- boundaries can be logical, security, protection, or trust boundaries and need not coincide with physical boundaries.

## 4. Evidence

### Evidence E1 — Provenance models composition as a graph, not a single opaque event

W3C PROV explicitly represents activities, entities, agents, usage, generation, derivation, communication, and delegation. A derivation can contain a path through multiple activities rather than requiring all work to be represented as one activity.

Therefore a composed action can have a higher-level causal identity while preserving the fact that multiple distinct activities occurred.

Source: W3C PROV Semantics and PROV-O. citeturn0search3turn0search10

### Evidence E2 — Distributed tracing independently confirms the need for two levels of identity

W3C Trace Context defines a trace identity that links a distributed transaction across components while each request has its own position/parent relationship. This supports the distinction between:

`logical action / trace` → `individual interaction / request`.

A single identifier replacing all step identities would lose useful causal structure; independent step identifiers without a common parent would lose composition context.

Source: W3C Trace Context. citeturn0search1turn0search6

### Evidence E3 — Authority cannot be inferred from causal membership

PROV distinguishes agents, activities, and delegation. An agent acting on behalf of another is explicitly modeled as a relationship tied to an activity. This is evidence against treating membership in one composed action as proof that the same authority automatically applies to every constituent interaction.

Therefore:

`same action` ≠ `same authority`.

Authority must remain attached to the activity or operation for which it is valid, even when several activities share one parent action.

Source: W3C PROV semantics and namespace. citeturn0search3turn0search4

### Evidence E4 — Retry/recovery semantics belong to individual operation semantics

RFC 9110 makes idempotency relevant to whether a request can safely be repeated after a communication failure. It explicitly warns against automatic retry of non-idempotent operations unless the client has additional means to establish that the operation was not applied or otherwise knows its semantics are safe.

Therefore a composed action cannot have one global `retry=true/false` property without losing information. Different constituent operations may have different retry, reconciliation, or compensation rules.

Source: RFC 9110 §9.2.2. citeturn0search0turn0search11

### Evidence E5 — External interaction boundaries can exist inside a composed action

NIST SP 800-160 treats interfaces, interconnections, interactions, trust domains, and security boundaries as distinct architectural concerns. This supports preserving the boundary crossings inside a larger action rather than reducing the entire action to one provider call.

Source: NIST SP 800-160. citeturn0search65

## 5. Cross-source comparison

| Question | PROV | Trace Context | RFC 9110 | NIST 800-160 | Combined implication |
|---|---|---|---|---|---|
| Can multiple steps form one logical action? | Yes, via derivation/activity graph | Yes, via one trace over many requests | Not a primary concern | Yes, interactions form system relationships | Yes |
| Should individual steps remain identifiable? | Yes | Yes, parent/request context | Yes, each request has semantics | Yes, interactions/interfaces matter | Required |
| Does shared causality imply shared authority? | No; delegation is explicit | No | No | No | Authority must remain scoped |
| Can one retry rule govern all steps? | Not specified | Not specified | No; semantics vary by request | Not implied | Recovery must be step/operation-aware |
| Can boundaries exist within one logical action? | Yes | Yes | Yes | Yes | Preserve boundary crossings |
| Is transport identity sufficient provenance? | No | No | No | No | Need semantic identities and evidence |

## 6. Mechanism reconstruction

The evidence supports a two-layer composition model:

`LOGICAL ACTION / PARENT CAUSAL IDENTITY`
→ contains →
`INTERACTION 1`
`INTERACTION 2`
`INTERACTION 3`
...

Each interaction retains at minimum:

- interaction identity;
- semantic type;
- parent action identity;
- input entity/revision where relevant;
- target/external resource where relevant;
- authority context applicable to that interaction;
- execution/request identity where one exists;
- produced evidence/result;
- external object/state identity where known;
- temporal position;
- failure/uncertainty state;
- recovery/reconciliation rule or requirement.

The parent action is therefore a causal container, not a substitute for the constituent interactions.

## 7. Critical distinction: composition is not atomicity

A composed action can be logically grouped without being an atomic transaction.

For example:

`AUTHORIZE → EXECUTE → PUBLISH → OBSERVE`

may be one business-level action, but it does not follow that all four steps commit or roll back together.

A failure after `EXECUTE` but before `OBSERVE` does not justify recording `FAILED` for the whole action if the external operation may already have happened. The action becomes partially known and may require reconciliation.

Likewise, successful `AUTHORIZE` does not prove successful `EXECUTE`, and successful `EXECUTE` does not prove external publication or desired consequence.

This preserves the existing model's distinction:

`request sent ≠ accepted ≠ completed ≠ state changed ≠ consequence achieved`.

## 8. Failure cases tested conceptually

### Case A — Prepare succeeds, execute never starts

Known:
- preparation activity occurred;
- no evidence of execution request.

Safe conclusion:
- action is incomplete;
- execution may be retried if authorization remains valid and preparation is still valid.

### Case B — Execute request sent, response lost

Known:
- request was attempted/sent;
- external result is not known.

Safe conclusion:
- do not convert the action to ordinary failure automatically;
- determine idempotency and reconcile external state before retry when required.

RFC 9110 directly supports this distinction for HTTP operations. citeturn0search0

### Case C — Execute succeeds, publication fails

Known:
- execution produced an external result;
- publication did not complete or is unknown.

Safe conclusion:
- preserve successful execution evidence;
- isolate publication as a separate interaction;
- do not erase or overwrite the execution result with a generic action failure.

### Case D — Publication succeeds, observation is unavailable

Known:
- publication request/response evidence may exist;
- independent observation is unavailable.

Safe conclusion:
- observation is unknown, not necessarily publication failure;
- the factory must distinguish `effect unverified` from `effect failed`.

### Case E — Authorization expires between steps

Known:
- earlier authorization was valid for an earlier interaction;
- later interaction occurs after its validity boundary.

Safe conclusion:
- shared parent action does not grant automatic continued authority;
- later interaction requires its own authority validation.

This follows the provenance distinction between action/agent/delegation and the general security-boundary model; exact implementation policy remains a future Content Factory decision.

## 9. Contradictions and negative evidence

### N1 — "One action = one request"

Rejected.

A logical action can span multiple requests and components. W3C Trace Context explicitly addresses traces spanning distributed components, while PROV represents multi-activity derivation paths. citeturn0search1turn0search3

### N2 — "One action = one authority"

Rejected.

Delegation and activity-specific responsibility show that authority/responsibility can be scoped to particular activities. Shared causal membership is insufficient evidence of shared authority. citeturn0search3turn0search4

### N3 — "One action = one retry policy"

Rejected.

Constituent operations can differ in idempotency and retry safety. RFC 9110 explicitly makes retry depend on operation semantics. citeturn0search0

### N4 — "If the parent action failed, every child effect failed"

Rejected.

A communication failure can leave the external state unknown after an operation was attempted. The parent action status cannot replace evidence about each constituent external interaction.

### N5 — "A common trace ID is sufficient provenance"

Rejected.

Trace context establishes correlation, not the complete semantic provenance required by Content Factory. PROV additionally models entities, activities, agents, derivation, and responsibility. citeturn0search1turn0search10

## 10. Inference boundary

### Directly supported by external evidence

- Multiple distributed interactions can share a higher-level causal identity while retaining individual identities.
- Provenance should preserve entities, activities, agents, derivations, and responsibility/delegation where relevant.
- Authorization/responsibility is not equivalent to causal membership.
- Retry safety depends on operation semantics such as idempotency and ability to establish whether an operation already occurred.
- System/security boundaries can occur between participating components and external entities.

### Inferred for Content Factory

- Introduce the concept of a logical external action as a causal container, without making it an atomic transaction.
- Preserve constituent interactions as independently attributable semantic activities.
- Attach authority to the interaction/operation for which it is valid rather than to the parent action alone.
- Attach recovery/reconciliation semantics to constituent operations, while allowing the parent action to aggregate status.
- Treat correlation IDs and provenance as complementary rather than interchangeable.

### Not yet proven

- The exact minimum fields of a generic `ExternalAction` contract.
- Whether one parent action should be represented as a new persistent object or derived from existing WorkItem/event identities.
- Whether the factory needs separate `action_id`, `trace_id`, and `operation_id`, or whether some can safely be mapped to existing identities.
- Whether all future integrations can use one composition model without operation-class-specific extensions.
- Whether compensation can be modeled generically enough to belong in the core contract.

## 11. Conclusion

Result: PROVEN at the architectural principle level; CANDIDATE at the contract level.

Multiple semantic interactions can compose into one logical external action without losing provenance or authority only if composition is modeled as a causal relationship/container rather than as a flattening of the constituent interactions.

The correct structure is:

`logical action`
`  ├── interaction / activity`
`  │     ├── authority context`
`  │     ├── input/revision`
`  │     ├── external target`
`  │     ├── operation identity`
`  │     ├── result/evidence`
`  │     ├── external state/effect evidence`
`  │     └── recovery semantics`
`  ├── interaction / activity`
`  └── ...`

The parent action provides causal continuity. It does not imply atomicity, shared authority, shared retry semantics, or successful external effect.

## 12. Decision

`EXTENDS_CURRENT_MODEL`

No implementation change is justified yet.

The existing research tree already has the necessary conceptual separation between interaction semantics, external action, authority, effect, observation, uncertainty, recovery, and provenance. Q3 strengthens the relationships between those nodes but does not yet justify a new repository primitive.

The next research target should therefore move to Q4/Q6 rather than prematurely implementing an `ExternalAction` object.

Recommended next question:

**Q4/Q6 — What is the minimum evidence contract required to distinguish request, acceptance, execution, external state change, observation, and desired consequence for each major external-system role?**

This is the next bottleneck because composition is now sufficiently understood at the principle level; evidence sufficiency determines whether the composed action can be safely verified and recovered.

## 13. Repository impact

- New durable research record only.
- No production code changes.
- No ontology or generic external capability primitive added.
- Existing research tree remains valid.
- Q3 result should constrain future external-action design: causal grouping must not collapse interaction-level provenance, authority, or recovery semantics.

## 14. Post-write verification target

After writing this record, verify on `main`:

1. exact file exists;
2. content contains decomposition, source map, evidence, contradictions, inference boundary, conclusion, decision, and derived question;
3. commit is on the expected branch;
4. no production files changed as part of Q3.

## 15. Derived questions

1. What is the minimum evidence contract for each interaction/result boundary?
2. Can one causal action retain a single identity while crossing multiple external systems?
3. When must an interaction receive a distinct operation identity rather than inheriting the parent action identity?
4. How should authority validity be represented when one logical action spans time and multiple systems?
5. Which evidence relationships are necessary to prove external state change rather than merely request completion?
6. Can recovery policy be selected from operation properties such as idempotency, reversibility, observability, and external object identity?
7. Which parts of this model can be demonstrated against GitHub without allowing GitHub's API shape to redefine the generic model?
