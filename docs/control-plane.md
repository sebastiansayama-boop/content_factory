# Content Factory Control Plane

GitHub is the command surface for the Content Factory.

COMMAND -> GitHub Issue -> Control Plane Action -> Allowlisted Executor -> Observed Result -> Issue comment

Commands:
- control: status
- control: product-test
- control: visual-test
- control: test
- control: telegram-test

Only the repository owner account sebastiansayama-boop is admitted.
Commands are allowlisted. Issue text is never executed as shell input.

This is deliberately not a second orchestration framework. GitHub provides command persistence, identity, execution history, logs, artifacts and an audit trail. The existing Content Factory runtime remains responsible for durable state and evidence.

Next commands should map directly to existing deterministic APIs: run:create, run:execute, run:inspect, run:approve, run:regenerate, publish:telegram.