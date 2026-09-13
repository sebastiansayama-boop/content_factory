# External-System Research — Q12 GitHub Mutation Identity Matrix

Date: 2026-09-13
Research branch: External World → External Systems → Reconciliation → GitHub concrete mutation classes
Status: COMPLETE
Decision: EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE
Confidence: HIGH for documented GitHub response/state semantics; MEDIUM for recovery-policy conclusions because mutation safety remains operation-specific

## 1. Question

Which GitHub mutation classes expose enough operation/effect identity to distinguish a prior mutation from merely observing the resulting state?

Required comparison:

`request identity → operation identity → resulting object/state → causal attribution → independent observation → safe recovery claim`

The purpose is not to invent a generic GitHub reconciliation primitive. The purpose is to determine what identity and evidence GitHub actually exposes for materially different mutation classes.

## 2. Decomposition

### Q12.1 — Mutation class semantics

Do GitHub mutation classes expose the same identity model?

### Q12.1.1 — Request identity

What identifies the submitted request or its intended target?

### Q12.1.1.1 — Operation identity

Does GitHub expose a distinct durable identifier for the mutation operation, or only an object/state identifier produced by it?

### Q12.1.1.1.1 — Result identity

What resulting object, revision, reference, or execution instance can be independently observed?

### Q12.1.1.1.1.1 — Causal attribution

Can the resulting observation be uniquely tied to the specific prior mutation rather than merely showing compatible resulting state?

### Q12.1.1.1.1.1.1 — Recovery claim

What additional conditions are required before the factory can decide that retrying, stopping, waiting, or reconciling is safe?

## 3. Source map

Primary sources were GitHub REST API documentation for Git references, Git commits, repository Contents, pull requests, workflow dispatches, and workflow runs.

GitHub's documentation distinguishes Git objects/references from higher-level resources. Git reference creation/update returns the reference and referenced commit SHA. Git commit creation returns a commit object identified by SHA. Contents mutation returns both a file/blob identity and the generated commit identity. Pull-request creation creates a durable pull-request resource. Workflow dispatch can return a workflow-run ID when run details are requested. Workflow runs have their own durable ID and head SHA. citeturn0search1turn0search2turn1search1turn1search2turn0search3turn1search0

## 4. Comparative matrix

| Mutation class | Request / target identity | Distinct operation identity exposed? | Result identity | Independent observation | Attribution strength | Recovery conclusion |
|---|---|---|---|---|---|---|
| Branch/reference creation | `ref` + target commit SHA | No separate mutation-operation ID documented | Reference + referenced commit SHA | GET reference | Medium for resulting branch state; weak for causal history | State observation can reconcile existence/target, but does not by itself prove which mutation created it or whether repeating is safe |
| Reference update | ref name + new commit SHA + optional force flag | No separate mutation-operation ID documented | Reference + resulting commit SHA | GET reference / commit | Medium for resulting state; weak for causal history | Resulting ref state is observable, but retry requires knowledge of intended prior state, current state, concurrency and duplication semantics |
| Git commit creation | message/tree/parents and supplied metadata | No separate mutation-operation ID documented | Commit SHA + tree + parents | GET commit | Strong for the created immutable commit object; not automatically proof that a particular ref was updated because commit creation and ref movement are separate Git operations | Commit existence can be reconciled; it does not by itself establish publication of that commit through a ref |
| Contents API file create/update | path + branch; update additionally requires current file blob SHA | No separate mutation-operation ID documented | File/blob SHA + generated commit SHA | GET Contents / commit / blob | Stronger than raw ref observation for the resulting file revision; still no separate request-operation identity | File and commit state can be reconciled, but retry safety depends on exact path, expected prior blob SHA, branch state and duplicate-commit consequences |
| Pull request creation/update | head/base + PR parameters; existing PR number for updates | The PR resource itself supplies durable identity (`number`/resource identity), but docs do not define it as a generic idempotency key for the mutation request | Pull request resource, number, head/base state | GET pull request | High for resource attribution once PR identity is known; not equivalent to proving every attempted mutation request | A known PR number allows direct reconciliation of resource state. Retry still requires checking whether desired mutation already exists and whether repeating it changes semantics |
| Workflow dispatch | workflow ID/file + ref + inputs | When `return_run_details=true`, resulting workflow run ID is returned; without it the response may contain no run identity | Workflow run ID, run URL, head SHA, event, status/conclusion | GET workflow run | High for a specific triggered run when run ID is returned; otherwise correlation may be ambiguous | Prefer durable run identity before treating dispatch as safely reconciled; otherwise independent run discovery may not uniquely identify the triggering dispatch |

The matrix is a semantic comparison, not a claim that every API version or client wrapper exposes identical fields. The cited GitHub REST documentation is the authority for the documented response behavior. citeturn0search1turn0search2turn1search1turn1search2turn0search3turn1search0

## 5. Mutation-class findings

### 5.1 Branch creation

GitHub's reference-create endpoint takes a fully qualified ref and a commit SHA and returns the created reference plus its target commit object. There is no separately documented operation identifier in the response. The durable identity is therefore primarily the resulting reference and its target commit.

This is enough to reconcile a state claim such as:

`refs/heads/X exists and points to commit C`

It is not enough to establish a unique mutation history merely from the state observation. A branch reference is a current state projection, not an operation log. citeturn0search1

### 5.2 Reference update

Reference update similarly accepts the ref name and target SHA, with an optional force flag, and returns the resulting ref and object SHA. GitHub documents `409 Conflict` behavior for conflicts and explicitly distinguishes non-force fast-forward semantics from forced updates.

Therefore the observed ref state is strong evidence of the current external state, but the state alone does not identify which update request produced it. Safe recovery must account for the expected previous state, concurrent writers, force/non-force semantics, and consequences of repeating the update. citeturn0search1

### 5.3 Commit creation

A Git commit is a content/state object: GitHub documents its tree, parents and resulting commit SHA. Creating a commit does not itself establish that a branch/reference now points to it; the Git reference is a separate object and update operation.

This creates an important two-stage boundary:

`commit object exists ≠ commit is published through target ref`

A commit SHA is therefore a strong immutable result identity, but not a generic mutation-operation identity. citeturn0search2

### 5.4 Contents API file mutation

The Contents API's create/update operation returns both the resulting file content/blob identity and the commit identity. Updates require the current file blob SHA, and GitHub documents conflict responses.

This gives reconciliation two useful state identities:

`file path → blob SHA`

and:

`mutation result → commit SHA`

That is stronger than a bare branch observation for reconstructing the resulting file state. However, neither SHA is documented as an idempotency key or generic request-operation ID. A retry therefore cannot be declared safe solely because the resulting file/commit can be observed. The factory must compare the intended revision and current state and evaluate duplicate-commit and concurrent-change consequences. citeturn1search1

### 5.5 Pull request creation/update

A pull request is a durable higher-level resource. Creation takes head/base and returns the created pull-request resource; subsequent mutations address the resource by its PR number. This gives the factory a stronger reconciliation handle than a raw Git ref: once the PR identity is known, its current state can be queried directly.

However, the PR number is a resource identity, not automatically an idempotency key for an arbitrary create request. A lost create response therefore still requires correlation/reconciliation before a duplicate create is attempted. Once an existing PR is uniquely identified, subsequent update operations can be reconciled against that resource's state. citeturn1search2

### 5.6 Workflow dispatch

Workflow dispatch is materially different because GitHub can return the resulting workflow-run ID when `return_run_details=true`. The run then has a durable `id`, head SHA, event, status, conclusion, timestamps and actor/triggering-actor information.

This is the strongest case in this matrix for a direct mutation-to-operation identity projection:

`dispatch request → workflow run ID → independently observable run state`

But the distinction matters: if run details are not requested, GitHub may return an empty `204` response, leaving the factory without the durable run identity from the dispatch response. Independent discovery can then be ambiguous if multiple runs are plausible. Therefore the run ID is highly useful for reconciliation, but the factory should not assume that every dispatch has an independently reconstructable operation identity after response loss. citeturn0search3turn0search4turn1search0

## 6. Identity hierarchy revealed by the comparison

The GitHub cases expose at least five different identity layers:

1. `REQUEST / INTENT IDENTITY` — what the factory intended to mutate.
2. `RESOURCE / TARGET IDENTITY` — branch, file path, PR, workflow, etc.
3. `STATE / REVISION IDENTITY` — commit SHA, blob SHA, current ref target, PR state.
4. `OPERATION / EXECUTION IDENTITY` — a durable run or higher-level resource identity when GitHub exposes one.
5. `CAUSAL ATTRIBUTION` — evidence that this particular prior interaction produced the observed result.

These layers must not be collapsed.

A SHA is not automatically an operation ID.
A resource ID is not automatically an idempotency key.
A successful GET is not automatically causal attribution.
A mutation response is not automatically a durable recovery policy.

## 7. Evidence ladder applied to Q12

Using the candidate Q10 ladder:

`R0 NO_CORRELATION`

Possible for mutation classes where only generic target state remains and no reliable correlation survives.

`R1 INTERACTION_IDENTIFIED`

Can be established when a request/interaction record is retained, but this is not necessarily reconstructable from GitHub state alone.

`R2 OPERATION_STATE_IDENTIFIED`

Strongest for workflow runs when a run ID is returned and subsequently observed; also potentially available through durable higher-level resources such as an existing PR, but semantics differ by mutation.

`R3 EFFECT_OR_STATE_IDENTIFIED`

Strongly available for refs, commits, Contents file state, PR state, and workflow-run state through independent GET operations.

`R4 EFFECT_ATTRIBUTED`

Not universal. It is strongest where a durable resource/execution identity is directly connected to the initiating mutation and can be independently observed. It is weaker for raw Git object/ref mutations where the API exposes resulting state but no distinct operation record.

`R5 RECOVERY_CLAIM_VERIFIED`

Not supplied by GitHub's object identity alone. It requires a factory-side recovery policy that specifies the exact claim, acceptable state, idempotency/duplication semantics, authority validity, concurrency assumptions, and consequence risk.

## 8. Contradictions / rejected simplifications

### N1 — `commit SHA = operation ID`

Rejected.

A commit SHA identifies a Git commit object. GitHub documents commit creation and reference updates as separate operations. citeturn0search2turn0search1

### N2 — `current ref SHA = mutation attribution`

Rejected.

A ref observation identifies current state, not a unique mutation history. citeturn0search1

### N3 — `file blob SHA = request idempotency key`

Rejected.

The Contents API uses the current blob SHA as an update precondition and returns a new blob/commit identity; the documentation does not define the blob SHA as a generic mutation-operation idempotency key. citeturn1search1

### N4 — `PR number = universal create idempotency key`

Rejected.

The PR number is a durable resource identity after creation. It is not documented as a generic idempotency mechanism for duplicate create requests. citeturn1search2

### N5 — `workflow dispatch accepted = workflow outcome known`

Rejected.

A dispatch identifies a run when run details are returned, but run state continues through queued/in-progress/completed lifecycle. The run ID is an operation/execution handle, not immediate proof of the desired consequence. citeturn0search3turn1search0

## 9. Cross-source synthesis

The comparison supports the current Content Factory model and sharpens one boundary:

```text
FACTORY INTENT
    ↓
TARGET / REQUEST IDENTITY
    ↓
GITHUB MUTATION
    ↓
RESOURCE / STATE / REVISION IDENTITY
    ↓
[optional durable OPERATION / EXECUTION IDENTITY]
    ↓
INDEPENDENT OBSERVATION
    ↓
CAUSAL ATTRIBUTION
    ↓
RECOVERY CLAIM
```

GitHub does not expose one universal identity mechanism across mutation classes. Instead, identity follows the semantic resource being mutated.

Therefore a generic external-action model should not require every provider to expose a provider-generated `operation_id`. It should require the factory to preserve whatever identity layers the specific operation actually provides and to record when a layer is unavailable.

This is an extension of the current model, not a new runtime primitive.

## 10. Recovery implications

The mutation matrix does not authorize automatic retry.

For raw ref/object operations, reconciliation should normally start from exact target + expected revision/state and determine whether the desired external state already holds.

For Contents mutations, reconciliation can compare the exact path, expected prior blob SHA, resulting blob SHA and associated commit.

For pull requests, reconciliation should use the PR resource identity and compare head/base/title/body/state as relevant to the intended mutation.

For workflow dispatch, reconciliation should prefer a known workflow-run ID. If no run ID was returned, discovery must be treated as a correlation problem rather than assumed to identify the prior dispatch uniquely.

In every case:

`observation → claim resolution`

must be kept separate from:

`claim resolution → retry authorization`.

The second transition requires operation-specific safety rules.

## 11. Inference boundary

### Directly documented / observed

- Git references expose ref identity and target commit SHA, with conflict semantics for updates. citeturn0search1
- Git commits expose immutable commit identity and parent/tree relationships. citeturn0search2
- Contents mutations expose resulting file/blob and commit identities and require the current blob SHA for updates. citeturn1search1
- Pull requests are durable resources addressed by PR number and expose head/base state. citeturn1search2
- Workflow dispatch can return a workflow-run ID; workflow runs have durable IDs and independently observable state. citeturn0search3turn1search0

### Inferred

- GitHub mutation classes have materially different reconciliation strength.
- Resource/state identity and operation identity should remain separate in the factory model.
- Workflow runs provide a stronger operation/execution identity than raw Git refs/objects.
- Higher-level resource identity can provide stronger attribution than raw state identity, but still does not automatically define retry safety.

### Unknown / not proven

- A generic GitHub guarantee that every mutation can be reconstructed after a lost transport response.
- A universal idempotency mechanism across these mutation classes.
- A universal causal-history API for raw Git reference/object mutations.
- A generic rule allowing retry from observed state alone.
- Whether every connector/provider wrapper preserves all identity fields exposed by the underlying GitHub API.

## 12. Decision

`EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE`

Q12 is complete.

The central result is:

> GitHub does not provide one universal mutation-operation identity. Some mutation classes expose only resulting resource/state identities; higher-level operations such as workflow dispatch can expose a durable execution identity. Reconciliation therefore has to be operation-specific and identity-aware rather than based on a universal `GET target` rule.

The current Content Factory model is sufficient to represent this finding. No new ontology class, runtime state, retry primitive, or connector abstraction is justified yet.

## 13. Derived questions

Q13 — What is the minimum factory-side identity/provenance record that preserves reconciliation capability when the external provider exposes only target/resource/revision identity and no operation ID?

Q14 — Which operation-specific preconditions are sufficient to convert an observed external state into an authorized recovery decision?

Q15 — Which external mutation classes require provider-side idempotency keys or client-generated correlation identifiers before execution can be admitted as safely recoverable?

These are research questions, not implementation commitments.

## 14. Repository impact

- Added this durable research record.
- No production implementation changes.
- No ontology changes.
- No generic reconciliation primitive introduced.
- No retry behavior introduced.
- No new external mutations performed for Q12.
- Existing experimental branches from the prior controlled experiment remain classified as experimental/control artifacts and are not reinterpreted as factory production effects.

## 15. Post-write verification

Required verification after writing this record:

1. Fetch the committed file from `main`.
2. Verify the content includes the Q12 matrix and final decision.
3. Verify the resulting commit SHA.
4. Confirm no production/runtime artifact was changed by Q12.
5. Confirm the next research step is Q13 rather than implementation of a generic reconciliation primitive.
