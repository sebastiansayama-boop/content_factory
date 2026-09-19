# Impact Analysis — CHANGE-001

The first important result is the difference between graph reachability and semantic impact.

A graph-only traversal from C004 reaches SCRIPT-001, VIDEO-001, all three shorts, and TELEGRAM-001. That is a useful blast-radius candidate, but it is not yet a decision.

The semantic analysis narrows the action set:

- SCRIPT-001 — REVIEW
- VIDEO-001 — REVIEW
- SHORT-002 — REGENERATE
- TELEGRAM-001 — REVIEW
- SHORT-001 — KEEP
- SHORT-003 — KEEP

The causal explanation matters. SHORT-001 and SHORT-003 are downstream of the same VIDEO-001 node, but their actual subject matter does not depend on the changed C004 meaning. A pure descendant traversal would over-invalidate them.

This is the behavior the experiment is testing:

CHANGE → FIND CANDIDATES → INSPECT SEMANTIC USE → CLASSIFY → HUMAN REVIEW → EXECUTION

No production execution is authorized by this artifact. The result is an impact proposal only.

The experiment does not yet prove that a general semantic impact engine can reliably infer dependencies. It demonstrates a concrete test case where semantic dependency is narrower than graph dependency.
