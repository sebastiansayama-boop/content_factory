# Impact Test v0.1

Purpose:
Test semantic downstream impact rather than simple file dependency.

Initial state:
All production objects are based on SCRIPT-001 and its claim references.

Controlled change:
Replace C004 with a revised formulation that materially changes the description of San Phra Phum.

Expected analysis:
- SCRIPT-001 -> REVIEW
- VIDEO-001 -> REVIEW or REGENERATE depending on whether the visual explanation uses the changed fact
- SHORT-002 -> REGENERATE
- SHORT-001 -> KEEP
- SHORT-003 -> KEEP
- TELEGRAM-001 -> REVIEW only if its final wording uses C004

Required explanation:
The system must provide the causal path for every affected object.

Example:
C004 changed
-> paragraph 4 in SCRIPT-001
-> explanation of San Phra Phum in VIDEO-001
-> SHORT-002

Negative test:
Changing C004 must not automatically invalidate every artifact in the project.

Success criteria:
1. Changed claim is identified.
2. Direct dependents are identified.
3. Transitive dependents are identified.
4. Affected and unaffected objects are distinguished.
5. Each proposed action has a reason.
6. User can override at least one proposed action.
7. No execution occurs until the user approves the resulting plan.
8. New versions preserve the previous versions.
9. Provenance remains traceable.
