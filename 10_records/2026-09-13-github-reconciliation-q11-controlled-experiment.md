# External-System Research — GitHub Controlled Reconciliation Experiment

Date: 2026-09-13
Research branch: External World → External Systems → Reconciliation → GitHub concrete case
Status: COMPLETE FOR CURRENT EXPERIMENT
Decision: EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE
Confidence: HIGH for the observed GitHub state boundary; LOW/MEDIUM for transport-failure generalization

## 1. Question

Can the Content Factory reconciliation model resolve an intentionally induced epistemic `UNKNOWN` against a real external GitHub state, and what evidence level does the resulting observation actually establish?

This experiment deliberately does **not** simulate a real network timeout. Instead, the external mutation response is excluded from the evidence set and the resulting state is reconstructed by a separate observation. Therefore this is evidence about reconciliation and attribution boundaries, not proof of transport-failure handling.

## 2. Decomposition

### Q11.1 — External mutation

Can a low-consequence GitHub external action create a durable externally observable state without changing `main`?

### Q11.1.1 — State identity

Can the resulting branch reference be identified independently of the mutation response?

### Q11.1.1.1 — Revision identity

Can the observed branch state be tied to an exact commit SHA?

### Q11.1.1.1.1 — Claim separation

Does observing the branch reference prove only state/effect, or also prove the causal mutation that produced it?

### Q11.1.1.1.1.1 — Attribution

What additional evidence is required to move from `EFFECT_OR_STATE_IDENTIFIED` to `EFFECT_ATTRIBUTED`?

### Q11.1.1.1.1.1.1 — Recovery relevance

Would the observed evidence be sufficient to decide whether repeating the same branch mutation is necessary or safe?

## 3. Source map

### Primary external documentation

1. GitHub REST Git Database documentation.
2. GitHub REST Git References documentation.
3. GitHub REST Git Commits documentation.
4. GitHub REST repository Contents documentation.

GitHub documents Git objects and references as distinct resources. The documented low-level write sequence creates objects/commit and then updates a branch reference. Reference updates return the resulting ref and commit SHA; reference updates also have explicit conflict semantics. The Contents API similarly returns both file/blob and commit identity.

### Repository evidence

The repository's current `main` reference before the experiment pointed to:

`fb8de2e979f05aa93a3b9dfccbf77a99131c2d00`

The experiment created three disposable experimental branch references from `main` while testing the connector path:

- `experiment/reconciliation-q10`
- `experiment/reconciliation-q11`
- `experiment/reconciliation-q12`

All three were observed afterwards to point to the same commit SHA as `main`.

These branches are experimental/control artifacts created during this research. They are **not** Content Factory-generated production effects and must not be represented as such.

## 4. Method

1. Read the current `main` reference.
2. Establish a low-consequence branch target from `main` using the GitHub connector.
3. Treat the direct mutation response as deliberately unavailable to the reconciliation evidence set.
4. Query the branch reference independently.
5. Compare the observed branch object SHA with the known `main` commit SHA.
6. Evaluate which claims are established and which remain unresolved.

The experiment therefore creates an artificial epistemic boundary:

`mutation occurred → mutation response intentionally discarded → external state independently observed`

This is not equivalent to a real lost-response network failure.

## 5. Observed evidence

### E1 — External branch state exists

The independent reference lookup returned:

`refs/heads/experiment/reconciliation-q12`

with object SHA:

`fb8de2e979f05aa93a3b9dfccbf77a99131c2d00`

The same SHA was independently observed on `main` immediately before the experiment.

### E2 — Object/state identity is available

The observation provides both the external target identity (branch reference) and the referenced commit identity (SHA).

Therefore the observation establishes at least:

`TARGET_IDENTITY = branch ref`
`STATE/REVISION IDENTITY = commit SHA`

### E3 — External state/effect is observable independently

The branch reference can be queried without relying on the mutation response. This establishes that GitHub exposes an observation path separate from the mutation path.

### E4 — Causal attribution remains weaker

The branch reference and commit SHA establish the resulting state, but the observation alone does not encode a unique operation identity proving which mutation created the branch.

Another actor could theoretically have created the same branch with the same target state. Therefore:

`observed state ≠ complete causal attribution`

The direct mutation response was intentionally excluded from the reconciliation evidence set, so this experiment does not claim R4 causal attribution from the observation alone.

## 6. Evidence classification

Using the candidate Q10 evidence ladder:

`R0 NO_CORRELATION` — disproven for this case.

`R1 INTERACTION_IDENTIFIED` — not established by the reconciliation read alone.

`R2 OPERATION_STATE_IDENTIFIED` — not established; the branch reference does not expose a historical operation lifecycle.

`R3 EFFECT_OR_STATE_IDENTIFIED` — established. The external branch target and commit SHA are directly observable.

`R4 EFFECT_ATTRIBUTED` — not established from the independent observation alone.

`R5 RECOVERY_CLAIM_VERIFIED` — not established generically; the exact recovery claim has not been supplied with a mutation-specific safety policy.

Therefore the experiment demonstrates a concrete `R3` reconciliation result and a boundary between R3 and R4.

## 7. What the experiment proves

### Proven

- A real GitHub external mutation can produce a durable branch-reference state independently observable through the Git reference API.
- The observation exposes target identity and exact commit SHA.
- External state can therefore be reconstructed without relying on the mutation response.
- The resulting state is sufficient to establish an external effect/state claim at approximately R3 of the candidate ladder.

### Not proven

- That the mutation response can be lost through a real transport failure while the mutation succeeds.
- That GitHub provides a generic operation identity allowing the branch creation itself to be causally reconstructed after response loss.
- That branch state alone is sufficient to prove causality.
- That branch state alone is sufficient to decide a retry policy for every mutation type.
- That all GitHub operations expose the same reconciliation semantics.

## 8. Important boundary

This experiment reveals a stronger distinction:

```text
MUTATION RESULT
    ↓
EXTERNAL STATE OBSERVATION
    ↓
STATE CLAIM
    ↓
CAUSAL ATTRIBUTION
    ↓
RECOVERY CLAIM
```

Each arrow requires additional evidence. The GitHub branch reference gives strong state evidence, but it does not automatically supply operation history or causal attribution.

This directly supports Q10's rejection of:

`object exists = operation succeeded`

and:

`GET target = universal reconciliation`.

The GET/reference observation is useful because it resolves one claim, not every possible claim.

## 9. Cross-source reconciliation

The experiment is consistent with the broader research:

- Q3: logical action and constituent interaction remain distinct.
- Q4/Q6: evidence must prove the particular transition/claim.
- Q7–Q9: unknown outcome must not be collapsed into failure or automatic retry.
- Q10: reconciliation is claim-oriented and must preserve residual uncertainty.

GitHub provides a concrete instance of the generic model:

`prior interaction → external reference state → independent observation → state claim`

but does not yet provide evidence for the full generic operation-attribution chain.

## 10. Contradictions / negative evidence

### N1 — `branch exists = mutation causally proven`

Rejected.

The observed branch state does not contain sufficient information by itself to establish the unique causal mutation that produced it.

### N2 — `commit SHA = operation identity`

Rejected.

A commit SHA identifies a Git object/state, not necessarily the external operation that caused a branch reference to point at it.

### N3 — `successful observation = recovery decision`

Rejected.

The observation resolves state uncertainty but does not by itself specify whether retry, stop, wait, or another recovery action is safe.

## 11. Inference boundary

### Directly observed

- The branch reference exists.
- It points to the recorded commit SHA.
- The same SHA is the current `main` target.
- The observation was obtained separately from the mutation call.

### Inferred

- GitHub's reference observation can serve as a reconciliation mechanism for branch-state claims.
- State identity and causal operation identity must remain separate.
- A generic reconciliation result should be able to terminate at an effect/state claim without pretending that attribution has also been established.

### Unknown

- Real response-loss behavior for GitHub mutations.
- Whether a specific GitHub mutation can be safely retried from state evidence alone.
- The minimum operation identity required for each GitHub mutation class.

## 12. Repository impact

- Added this durable research record only.
- No production implementation changes.
- No ontology changes.
- No runtime reconciliation primitive introduced.
- No retry behavior introduced.
- Three experimental branch refs were created during the connector experiment and remain explicitly classified as experimental/control artifacts:
  `experiment/reconciliation-q10`, `experiment/reconciliation-q11`, `experiment/reconciliation-q12`.

These refs should not be treated as factory-generated production effects.

## 13. Decision

`EXTENDS_CURRENT_MODEL / NO_IMPLEMENTATION_CHANGE`

The real GitHub case confirms the Q10 semantic boundary:

`reconciliation can establish external state without necessarily establishing causal operation identity.`

The next research question is therefore narrower and more important than implementing a generic reconciliation interface:

**Q12 — Which GitHub mutation classes expose enough operation/effect identity to distinguish a prior mutation from merely observing the resulting state?**

The investigation should compare:

- branch creation;
- reference update;
- commit creation;
- Contents API file mutation;
- pull request creation/update;
- workflow dispatch where applicable.

For each class determine:

`request identity → operation identity → resulting object/state → causal attribution → independent observation → safe recovery claim`.

No further external mutation should be performed until this matrix is established.

## 14. Post-write verification

Required and completed:

1. The experiment's branch references were independently fetched after creation.
2. Each observed branch pointed to `fb8de2e979f05aa93a3b9dfccbf77a99131c2d00`.
3. `main` was observed at the same commit before the experiment.
4. The research conclusion is limited to the evidence actually observed.
5. No production/model artifact was changed by the experiment itself.
