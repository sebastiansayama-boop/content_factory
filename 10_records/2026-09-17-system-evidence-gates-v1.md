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
2. CI runs Ruff as an independent static-analysis gate.
3. CodeQL scans Python and JavaScript/TypeScript with the `security-and-quality` suite.
4. Existing pytest and container build gates remain unchanged.

## What this proves

If the workflow passes, it proves only that the repository passed these concrete gates for that commit:

`compile -> static analysis -> pytest -> container build -> CodeQL`

It does not prove product usefulness, semantic correctness of every requirement, external business outcome, or absence of all AI-generated defects.

## Known remaining gap

The runtime currently permits a `VerificationResult` with `passed=True` and no `evidence_refs`. This is a concrete contract weakness identified in the previous research record. It must be fixed in the runtime itself; a prompt or documentation rule is not an enforcement mechanism.

## Evidence rule

`PASS` is valid only for the gate that actually ran. Missing evidence remains `UNKNOWN`; it is never promoted to `PASS` by narrative text.
