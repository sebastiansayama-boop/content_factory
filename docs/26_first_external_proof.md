# 26 — First External Proof of Content Factory Operation

Status: `CANDIDATE / TEST CRITERION`

## 1. Question

What is the first external observation that is strong enough to demonstrate that the Content Factory itself has operated, rather than merely that its repository, model, or individual tools exist?

## 2. Decision

The first external proof is **one completed end-to-end content work item that crosses the factory boundary into an external experience and produces an independently observable external effect, with the complete provenance and authority chain recoverable**.

Minimum proof:

```text
BOUNDED DEMAND / INPUT
        ↓
WORK ITEM
        ↓
KNOWLEDGE BASIS
        ↓
EDITORIAL DECISION + SPECIFICATION
        ↓
PRODUCTION VIA CAPABILITY
        ↓
EXACT REVISION
        ↓
VERIFICATION
        ↓
ACCEPTANCE
        ↓
AUTHORIZED RELEASE
        ↓
PUBLICATION / DELIVERY
        ↓
EXTERNAL EFFECT
        ↓
OBSERVATION
```

The proof is therefore not merely a published article, image, video or post.

## 3. Why publication alone is insufficient

A successful publication proves that a distribution boundary was crossed. It does not, by itself, prove that the complete factory operated as modeled.

The repository already distinguishes:

```text
verification ≠ acceptance
acceptance ≠ publication
publication ≠ outcome
```

That distinction is also consistent with current content-system practice: Sanity separates drafts, release versions, validation, authorization and publication, while Contentful describes the lifecycle from planning through creation, review, publication, maintenance and retirement. citeturn617973search0turn617973search8

## 4. What makes the proof external

The proof must include an observation that cannot be established solely by inspecting the repository.

Acceptable external observations include, depending on the channel:

```text
publicly accessible published artifact
successful delivery to an external destination
observable audience interaction
measurable response event
external system acknowledgement
```

For the first proof, the minimum external observation is **successful external delivery/public accessibility**. Audience response is stronger evidence but is not required to prove the basic execution of the factory.

This preserves the distinction between:

```text
FACTORY OPERATION PROOF
→ external delivery/effect exists

FACTORY VALUE PROOF
→ audience / market / business response is observed
```

## 5. Provenance requirement

The external artifact must be traceable backward to the work item and its inputs.

At minimum, the record must identify:

```text
work_item_id
input / source references
knowledge revision(s)
editorial decision
specification revision
capability / executor used
asset revision
verification result
acceptance decision + authority
release identity
publication / delivery target
external effect
observation timestamp
```

This follows the general provenance requirement that the entities, activities and responsible agents involved in producing or delivering an object be representable and traceable. W3C PROV explicitly treats provenance as a record of entities, activities and agents involved in producing, influencing or delivering a thing. citeturn821195search0turn821195search5

## 6. Exact success test

The first proof is `PASS` only when all of the following are true:

```text
[ ] A bounded work item existed.
[ ] The intended outcome was explicit.
[ ] The knowledge basis was identifiable.
[ ] An editorial decision and specification existed.
[ ] A concrete capability execution occurred.
[ ] The resulting asset/content revision is identifiable.
[ ] Verification was performed against the exact revision.
[ ] Acceptance was explicit and attributable to an authority.
[ ] A release/publication was explicitly authorized.
[ ] An external delivery/effect actually occurred.
[ ] The external effect can be independently inspected or evidenced.
[ ] The complete provenance chain can be reconstructed.
[ ] No material boundary was silently skipped.
```

If any required item is absent, the result is not the first proof; it is a partial demonstration.

## 7. Stronger second-order proof

After the minimum proof, the next test should establish that the factory can learn from the external effect without corrupting its epistemic boundaries:

```text
EXTERNAL EFFECT
    ↓
OBSERVATION
    ↓
MEASUREMENT
    ↓
INTERPRETATION
    ↓
LEARNING CANDIDATE
    ↓
EXPLICIT PROMOTION
    ↓
KNOWLEDGE / EDITORIAL / PRODUCTION UPDATE
```

A metric alone is not learning, and an observation is not automatically a knowledge claim.

## 8. Strongest practical proof

The strongest early demonstration is not the most elaborate content package. It is the smallest real case that closes the loop and can be independently reconstructed.

Therefore the recommended first case is:

```text
ONE WORK ITEM
→ ONE CONTENT PRODUCT
→ ONE EXTERNAL CHANNEL
→ ONE AUTHORIZED PUBLICATION
→ ONE OBSERVABLE EXTERNAL RESPONSE
→ ONE RECOVERABLE PROVENANCE CHAIN
```

This keeps the test bounded while exercising the actual factory boundaries.

## 9. External research reconciliation

### SUPPORTS_CURRENT_MODEL

Current repository documents already define the value flow through `distribution → external effect → learning`, distinguish the factory from the wider ecosystem, and require exact revision, verification, acceptance, authority and provenance boundaries. fileciteturn37file0 fileciteturn34file0

Current machine-readable model also defines `publication_effect_record`, explicit release readiness, revision-bound verification, separate acceptance/publication/outcome boundaries, and explicit authority for external effects. fileciteturn45file0

### EXTENDS_CURRENT_MODEL

The repository currently specifies the external-effect path but does not yet define the **minimum evidentiary threshold** that qualifies one real case as the first external proof. This document adds that test criterion without changing the factory's value-flow architecture.

External systems corroborate the need to separate draft/version state, validation, release and publication, and to preserve provenance across generation and delivery. citeturn617973search0turn617973search11turn821195search0

### NOT_PROVEN_YET

The repository does not currently contain a real case satisfying this criterion. The architecture remains `candidate` until such a case is executed and independently observed.

## 10. Terminal condition

The first external proof is achieved only when a real case reaches:

```text
EXTERNAL_EFFECT_OBSERVED = TRUE
AND
PROVENANCE_RECONSTRUCTABLE = TRUE
AND
AUTHORITY_CHAIN_RECONSTRUCTABLE = TRUE
AND
NO_SILENT_BOUNDARY_SKIPPED = TRUE
```

Until then, claims about the factory remain architectural hypotheses rather than operational proof.
