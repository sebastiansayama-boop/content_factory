# Runtime → Repository Persistence Research — 2026-09-13

## Question

Why did `FactoryRuntime` materialize files locally while the GitHub repository remained empty in the working zones, and what is the smallest safe mechanism for making runtime evidence durable in the repository without collapsing execution, authority and publication boundaries?

## Repository evidence

- `FactoryRuntime` stores state, events, executions, verifications, acceptances and publications in memory. `ArtifactStore` writes JSON to a filesystem root, but no repository synchronization or Git commit is performed by the runtime.
- The repository protocol requires the repository to remain the durable working model and requires explicit verification after writes.
- The operating model separates production, verification, acceptance, distribution and external effect.
- The engineering model explicitly separates capability execution from authority and publication.
- The current GitHub tree still contains only README files in the working zones; therefore the previous filesystem sink did not by itself solve repository persistence.

## External research

### 1. W3C PROV

Source: W3C PROV Model Primer, https://www.w3.org/TR/prov-primer/

Finding: provenance represents entities, activities and agents involved in producing or influencing an object, with explicit generation/usage and responsibility relations.

Classification: `SUPPORTS_CURRENT_MODEL`.

Consequence: runtime evidence should preserve provenance and should not be conflated with the semantic truth of the produced content.

### 2. GitHub Actions / GITHUB_TOKEN

Sources:
- https://docs.github.com/en/actions/concepts/security/github_token
- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

Finding: a workflow receives a repository-scoped `GITHUB_TOKEN`; write access to repository contents can be explicitly granted with `permissions: contents: write`. GitHub recommends minimum required permissions.

Classification: `EXTENDS_CURRENT_MODEL`.

Consequence: repository synchronization can be implemented as an explicit infrastructure boundary rather than coupling the runtime directly to GitHub credentials.

### 3. Manual workflow dispatch

Source: GitHub documentation on manually triggered workflows, https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow

Finding: `workflow_dispatch` provides an explicit manual trigger and can receive inputs; manual triggering requires repository write access. GitHub also documents environments as an approval boundary for consequential workflow jobs.

Classification: `SUPPORTS_CURRENT_MODEL`.

Consequence: repository materialization should not run automatically on every runtime execution. An explicit repository-sync operation is a safer authority boundary.

### 4. NIST AI RMF governance

Source: NIST AI RMF Core, https://airc.nist.gov/airmf-resources/airmf/5-sec-core/

Finding: governance, documentation, accountability and human oversight should be integrated into AI system operation.

Classification: `SUPPORTS_CURRENT_MODEL`.

Consequence: repository synchronization must remain inspectable and explicitly authorized rather than being an invisible side effect of execution.

## Reconciliation

The external evidence does not establish that the repository should auto-commit every runtime execution. It supports the narrower conclusion that durable provenance needs an explicit persistence path and that the path should have a controlled authority boundary.

## Unresolved

No real editorial case currently exists in `00_inbox` from which a genuine observation/effect record can be generated. Synthetic demo execution must therefore remain identifiable as an experiment and must not be represented as a real external observation.
