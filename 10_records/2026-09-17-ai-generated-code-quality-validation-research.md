# AI-generated code quality validation — research record

Date: 2026-09-17
Status: research-derived engineering constraint

## Question

How should Content Factory validate AI-generated code changes so that `tests pass` is not treated as equivalent to `correct`, `structurally sound`, `in-scope`, or `maintainable`?

## External evidence

The 2026 Journal of Systems and Software study `Quality assurance of LLM-generated code: Addressing non-functional quality characteristics` combines a review of 109 papers, industry workshops, and repository-level experiments. It treats maintainability, security, and performance efficiency as quality dimensions beyond functional correctness and concludes that LLM-generated code needs QA mechanisms that verify quality rather than only test execution.

The same study reports that generated patches can trigger substantially more maintainability findings than reference patches. In its experiment, CodeQL maintainability queries produced hundreds of recommendations for generated patches while the reference patches produced far fewer. The study also reports cyclic-import findings concentrated in generated patches and links this to incomplete project-level awareness.

A 2026 empirical study, `On the risk of coding before testing`, reports error propagation when an LLM generates tests after seeing faulty generated code. The implication is not that generated tests are useless, but that implementation and tests produced by the same generative process are not independent evidence of correctness.

GitHub's randomized controlled study of Copilot provides the necessary counterpoint: AI-assisted code can be functionally and qualitatively strong on some tasks. Therefore the engineering requirement must not be `AI code is bad`; it must be `AI-generated changes require explicit quality evidence appropriate to the claim being verified`.

## Engineering interpretation

`TEST_PASS` is one observation. It is not a universal quality verdict.

The minimum independent dimensions for an AI-generated repository change are:

1. Syntax / type / lint validity.
2. Functional behavior.
3. Regression behavior.
4. Structural properties such as duplication, dependency cycles, unnecessary complexity, and module-boundary violations.
5. Scope adherence: changed files and behavior remain within the requested change.
6. Requirement conformance: implementation satisfies the actual requirement, not merely the tests written around the implementation.
7. Runtime/external observation where the change claims an externally observable effect.

Each dimension should produce explicit evidence. A missing observation is `UNKNOWN`, not `PASS`.

## Existing Content Factory alignment

The repository already models exact revision binding and evidence references in `VerificationResult`, and the runtime separates verification from acceptance and release. The cross-repository contract also defines verification as an evidence-bearing object bound to an exact `output_revision_id`.

Current gap identified during this audit: the runtime data model allows `VerificationResult(passed=True)` with an empty `evidence_refs` tuple. That permits a successful verification state without an explicit evidence reference. This is inconsistent with the repository's own evidence-oriented contract and should be treated as a validation defect, not hidden behind a prompt instruction.

## Decision constraint

Do not introduce a generic `AI slop score`.

Do not use diff size, LOC, or number of files as automatic proof of bad quality. These are signals that can trigger inspection, not universal failure criteria.

Prefer explicit, independently checkable gates whose output is an evidence record. A final acceptance decision may combine required gates, but one verifier must not silently stand in for all others.

## Target model

```text
REQUIREMENT
    -> explicit criteria / invariants
    -> implementation
    -> independent observations
       -> behavior
       -> structure
       -> regression
       -> scope
       -> requirement conformance
       -> external/runtime effect when applicable
    -> evidence set
    -> verification verdict
    -> acceptance decision
```

`TEXT != STATE`
`TEXT != EVIDENCE`
`TEST EXECUTION != TEST VALIDITY`
`VERIFICATION != ACCEPTANCE`
`LOCAL SUCCESS != EXTERNAL OUTCOME`

## Repository consequence

The validation system should grow by converting repeated manual review questions into deterministic or independently observable checks. It should not grow by adding increasingly long instructions to the generating model.
