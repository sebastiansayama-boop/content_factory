# System evidence gates v1

Date: 2026-09-17
Status: implementation candidate on `evidence/system-gates-v1`

## Purpose

Reduce the validation system to observable gates instead of treating repository text, test success, or model output as a universal quality verdict.

## External basis

NIST's current TEVV-Athlon work frames evaluation around test, evaluation, verification, and validation of real-world outcomes. NIST's SSDF and its generative-AI profile likewise treat verification and secure development as lifecycle practices rather than a single test result.

GitHub's official guidance for AI-generated code explicitly recommends functional checks plus static analysis, context/intent review, dependency scrutiny, and human review. GitHub also documents CodeQL as a code-scanning system for vulnerabilities and errors and exposes security-and-quality query suites.

## Changes in this candidate

1. CI compiles `src`, `tests`, and `scripts` before tests.
2. CI runs Ruff as an independent static-analysis gate on changed Python files.
3. CodeQL scans Python and JavaScript/TypeScript with the `security-and-quality` suite.
4. Existing pytest and container build gates remain unchanged.

## Evidence from the first run

The first CI run of this candidate was intentionally treated as a real validation result, not hidden.

- Compile gate: PASS.
- Ruff gate: FAIL.
- Pytest: SKIPPED because the static gate failed.
- Container: SKIPPED because the test job failed.

Ruff reported pre-existing findings across source, tests, and scripts, including unused imports, broad exception catches, import-order issues, mutable class defaults, and other maintainability findings. The failure was therefore useful evidence: a naive full-repository lint gate would not distinguish new defects from the repository's existing baseline.

## Repair after observation

The CI gate was narrowed to changed Python files for the current pull request. This preserves the useful property—new Python changes must pass static analysis—without falsely treating the entire historical repository as newly introduced debt.

This is an intentional correction cycle:

`external guidance → implementation → observed failure → scope diagnosis → gate repair`

The repair is not considered successful until a new CI run passes the scoped static gate and the remaining functional/container/CodeQL jobs are observed.

## What this proves

If the repaired workflow passes, it proves only that the repository passed these concrete gates for that commit:

`compile -> changed-file static analysis -> pytest -> container build -> CodeQL`

It does not prove product usefulness, semantic correctness of every requirement, external business outcome, or absence of all AI-generated defects.

## Known remaining gap

The runtime currently permits a `VerificationResult` with `passed=True` and no `evidence_refs`. This is a concrete contract weakness identified in the previous research record. It must be fixed in the runtime itself; a prompt or documentation rule is not an enforcement mechanism.

## Evidence rule

`PASS` is valid only for the gate that actually ran. Missing evidence remains `UNKNOWN`; it is never promoted to `PASS` by narrative text.
