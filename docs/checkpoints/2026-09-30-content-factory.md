## Content Factory checkpoint — 2026-09-30

Repository: sebastiansayama-boop/content_factory
Branch: feat/information-flow-contract
Pull request: #56 — Implement canonical information flow and provenance contract
Base: main
Latest verified commit: 35bc443bbed6605ecb745fc290dc6d209ffe3f7e

### Verified state

GitHub Actions are green at this checkpoint:
- tests #773: 117 passed, 2 skipped
- CI #488: test job SUCCESS
- CI #488: container/Docker job SUCCESS

### Implemented

- Canonical information flow:
  Source → Evidence → Claim → EditorialPoint → ContentElement → Artifact → Publication
- Provenance and lineage validation with fail-closed behavior.
- Execution trace:
  RUN → STAGE → TASK → TOOL → ACTION → RESULT → DECISION
- Explicit ContentBrief as the bridge from research to production.
- Durable, immutable ContentBrief revisions in SQLite:
  brief_id → revision_id
- API access to current and exact ContentBrief revisions.
- Replay contract anchored to an exact durable ContentBrief revision:
  brief_id + revision_id
- Tests covering replay anchoring and missing revision input.

### Important boundary

Replay is currently a reproducibility/version-selection contract, not yet a full content regeneration.

It can identify the exact immutable ContentBrief revision that should drive replay, but it does not yet execute the complete downstream production path.

### Next implementation slice

Implement the real:

ContentBrief revision
→ Production
→ new Artifact
→ Assembly
→ QC

Requirements:
1. Load the exact immutable ContentBrief revision requested by replay.
2. Rebuild the downstream production plan from that revision, not from a mutable run snapshot.
3. Generate new artifact/job IDs; never overwrite previous artifacts.
4. Preserve the original artifacts and all previous ContentBrief revisions.
5. Record lineage from the new artifact back to the exact ContentBrief revision.
6. Record replay execution trace with the actual revision reference.
7. Run Assembly and QC against the newly generated artifact.
8. Verify persistence after restart.
9. Add an end-to-end test proving:
   - r1 → Artifact A
   - r2 → Artifact B
   - replay r1 → Artifact C
   - C is based on r1, not r2
   - A and B remain unchanged
   - all three survive restart
   - QC lineage points to r1.

### Terminology

ContentBrief = the production instruction/decision.
Artifact = the actual produced content/output, such as a script, image, video, audio file, or publication-ready asset.

The next step should produce a real new Artifact, not another architecture-only contract.
