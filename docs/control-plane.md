# Content Factory Control Plane

GitHub is the command surface for the Content Factory.

COMMAND -> GitHub Issue -> Control Plane Action -> Allowlisted Executor -> Observed Result -> Issue comment

Commands:
- control: status
- control: product-test
- control: visual-test
- control: policy-test
- control: test
- control: telegram-test

Only the repository owner account sebastiansayama-boop is admitted.
Commands are allowlisted. Issue text is never executed as shell input.

## Role policy

The control plane separates capabilities by role:

| Action | Operator | Editor | QC | Publisher |
|---|---:|---:|---:|---:|
| CREATE | yes | no | no | no |
| EXECUTE | yes | no | no | no |
| EDIT | no | yes | no | no |
| REGENERATE | no | yes | yes | no |
| APPROVE | no | no | yes | no |
| REJECT | no | no | yes | no |
| PUBLISH | no | no | no | yes |
| EXPORT | no | no | no | yes |
| INSPECT | yes | yes | yes | yes |

The policy has two modes:

- PERSONAL: one actor may hold all four roles. State, QC and artifact-version gates still apply.
- STRICT_SOD: conflicting actor identities are rejected at approval/publication boundaries.

Mandatory release invariants:
- APPROVE requires REVIEW and QC PASSED.
- PUBLISH requires APPROVED, QC PASSED, approval, and an exact approved_version == artifact_version.
- Editing or regeneration of an approved version requires a new artifact version; approval does not silently transfer to the new version.
- Strict SoD rejects creator/editor as approver and creator/editor/approver as publisher.

The policy implementation is deterministic in src/content_factory/access_policy.py and is covered by tests/test_access_policy.py. Run control: policy-test to verify it through GitHub Actions.

This is deliberately not a second orchestration framework. GitHub provides command persistence, identity, execution history, logs, artifacts and an audit trail. The existing Content Factory runtime remains responsible for durable state and evidence.

Next control commands should map directly to existing deterministic APIs: run:create, run:execute, run:inspect, run:approve, run:regenerate, publish:telegram.