# Blind Semantic Impact Test — BLIND-001

## Question

Can the factory distinguish semantic impact from simple graph reachability when the source claim changes?

## Input boundary

The analysis used the change object, claim versions, production artifacts, derivative declarations and lineage. It did not use the previously written expected-impact classification.

## Result

The analysis classified:

- SCRIPT-001 — REVIEW
- VIDEO-001 — REVIEW
- SHORT-002 — REGENERATE
- TELEGRAM-001 — REVIEW
- SHORT-001 — KEEP
- SHORT-003 — KEEP

A graph-only traversal would have marked all six downstream objects as candidates.

## What was actually demonstrated

The factory can represent and evaluate a narrower impact set when semantic source declarations are available. The result is not equivalent to graph reachability.

The distinction is especially visible for SHORT-001 and SHORT-003. Both are downstream of VIDEO-001, but their declared subject matter does not depend on C004.

## What was not demonstrated

This test did not demonstrate autonomous semantic inference. The dependency declarations already expose the relevant claim usage.

Therefore the current evidence supports this narrower statement:

Explicit semantic dependency metadata enables more precise impact analysis than graph traversal alone.

It does not yet support:

The factory can automatically infer semantic dependencies reliably from arbitrary content.

## Next controlled test

Create a second fixture in which dependency annotations are withheld from the analyzer. Provide only the changed source, old/new versions and the actual artifact text. Require the analyzer to return:

affected object -> evidence span -> dependency reason -> KEEP/REVIEW/REGENERATE -> confidence

Then compare the inferred result against a human adjudicated reference set.

No production execution should occur during this inference test.
