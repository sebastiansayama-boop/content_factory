# Content Factory — Research Program: 100 Questions

## Purpose

This document defines a cumulative research program for acquiring operational knowledge and experience about Content Factory. The questions are not a development backlog. Each question is an investigation unit that should produce observable evidence, a bounded interpretation, and, where justified, an explicit decision or knowledge update.

The program follows the project learning lifecycle:

`Question → Research/Experiment → Evidence → Interpretation → Lesson → Knowledge → Decision → Work/Outcome → New Question`

A question is not considered answered merely because an implementation exists. The answer must be classified as one of:

- `PROVEN` — supported by direct, reproducible evidence.
- `DISPROVEN` — the tested hypothesis did not hold.
- `OBSERVED` — directly observed, but not sufficient for a general claim.
- `CANDIDATE` — plausible interpretation requiring further evidence.
- `UNKNOWN` — currently unresolved or not testable with available access.

## Research record

For every investigated question, record:

```text
Question:
Hypothesis:
Method:
Evidence:
Result: PROVEN | DISPROVEN | OBSERVED | CANDIDATE | UNKNOWN
Interpretation:
Learning:
Decision:
Repository impact:
Next question:
```

The evidence must identify what was actually observed. Claims about capabilities, reliability, external effects, or recovery must not be inferred solely from source code or documentation.

## 1. Factory boundaries

1. What exactly is the unit of work in Content Factory?
2. Where does human intent end and factory work begin?
3. Can one task produce multiple independent WorkItems?
4. Can one WorkItem produce multiple results?
5. Which objects require their own lifecycle?
6. Which states are primary and which are derived?
7. What is the minimum sufficient data for reproducible work?
8. Which information must never be lost between stages?
9. How can completion of work be demonstrated?
10. Which events represent real state changes versus computation only?

## 2. Research and knowledge acquisition

11. How does the factory formulate a research question?
12. When does a task require research rather than existing knowledge?
13. How is an information source distinguished from evidence for a claim?
14. How is the source of a specific claim recorded?
15. How are contradictions between sources represented?
16. How is an unknown recorded without turning it into false knowledge?
17. How is observation distinguished from interpretation?
18. When is an observation sufficient to create a learning candidate?
19. How does research modify an existing knowledge item?
20. How can closure of a research question be demonstrated?

## 3. Decision and human authority

21. Which decisions may the factory make autonomously?
22. Which decisions must require human authority?
23. How should ACCEPT / REVISE / REJECT be represented?
24. How can actual authorization be proven?
25. What happens when required authorization is absent?
26. Can an expired or superseded decision be reused?
27. How can authority be scoped to one task or operation?
28. How can previously granted authority be revoked?
29. How are conflicting decisions detected and resolved?
30. How can compliance with the exact accepted decision be proven?

## 4. AI and provider execution

31. What exactly constitutes execution in Content Factory?
32. How does a provider capability differ from a concrete API integration?
33. Can a provider be replaced without changing the WorkItem contract?
34. Which properties of a provider response must be preserved?
35. How is one external execution uniquely identified?
36. How is provider failure distinguished from an ambiguous external outcome?
37. What happens when a request is accepted externally but its response is lost?
38. Under what conditions is repeating such a request safe?
39. How can WorkItem → Execution → Result provenance be demonstrated?
40. Which parts of an execution result must be immutable?

## 5. Content as a production object

41. What is the canonical content object?
42. What is a revision, and why must results be revision-bound?
43. How does one content revision become another?
44. Can multiple candidate revisions coexist safely?
45. How is the canonical revision selected?
46. How is an approved revision protected from accidental mutation?
47. Which metadata must accompany content?
48. How are text, image, video, and audio assets associated with one content unit?
49. How are incompatible assets detected?
50. How can the complete input provenance of a content artifact be demonstrated?

## 6. Verification and quality

51. What exactly does Verification verify?
52. How does verification differ from acceptance?
53. Which result properties can be checked deterministically?
54. Which checks require AI judgment?
55. How should deterministic and judgment-based checks coexist?
56. How is verification bound to a specific revision?
57. What happens when verification refers to an obsolete revision?
58. Can several independent verification results coexist?
59. What is the minimum evidence required for PASS?
60. Can a release occur without successful verification?

## 7. Real external effects

61. What qualifies as an external effect?
62. How does execution differ from an external effect?
63. How can occurrence of an external effect be proven?
64. How is the external identifier of a created object captured?
65. How is the external object's state observed after the operation?
66. What happens when an effect occurred but confirmation was lost?
67. When should an outcome be classified as UNKNOWN instead of FAILED?
68. How can an external operation be retried safely?
69. How should idempotency be implemented for an external action?
70. How can operation_id → external effect → observation be demonstrated?

## 8. GitHub as the first external system

71. Can Content Factory make a controlled change to a real GitHub repository?
72. How does a WorkItem become a concrete repository change?
73. How can correspondence between the WorkItem and the resulting diff be proven?
74. How is the change bound to a commit?
75. How is a commit bound to its CI run?
76. Can CI provide independent verification evidence?
77. What is the correct factory behavior when CI fails?
78. Can the factory propose or perform a bounded correction after a failing CI run?
79. Where should human approval occur before merge?
80. Can the complete provenance chain `task → decision → diff → commit → CI → outcome` be reconstructed?

## 9. Reliability and recovery

81. What happens if the process crashes during execution?
82. What happens if an external effect occurs immediately before a crash?
83. Which states can be reconstructed after restart?
84. Which states cannot currently be reconstructed?
85. How can orphaned executions be detected?
86. How is a retry distinguished from a new operation?
87. What ownership/lease semantics are required for concurrent execution?
88. Under what conditions is retry safe?
89. Under what conditions can retry create a duplicate external effect?
90. How can recovery be proven not to fabricate a result?

## 10. Learning loop

91. How does an observation become a learning candidate?
92. How does a learning candidate become an explicit decision?
93. When should new experience change architecture?
94. When should experience change only the operating process?
95. How are failed experiments recorded and retained?
96. How is repetition of an already demonstrated failure prevented?
97. How can duplicate or equivalent learning from different experiments be detected?
98. How can knowledge accumulation be assessed without treating record count as a KPI?
99. How can improvement caused by accumulated knowledge be demonstrated in a later experiment?
100. Can the full lifecycle `Question → Experiment → Evidence → Interpretation → Lesson → Knowledge → Decision → Work → Outcome → New Question` be reproduced across multiple experiments?

## Operating rules

1. Do not implement a capability solely to make a question appear answered.
2. Prefer the smallest experiment that can produce decisive evidence.
3. Record negative results and unresolved questions as first-class project knowledge.
4. Do not promote an observation into a general architectural claim without sufficient evidence.
5. Every material conclusion should point to its evidence and, where applicable, its repository impact.
6. Research records should preserve the distinction between what was observed, what was inferred, and what was decided.
7. When an experiment changes the repository, preserve the link between the research record and the resulting change/commit.
8. When an experiment creates a real external effect, capture the external identifier and an independent observation of the resulting state whenever possible.
9. The next research question should be selected from the current evidence and unresolved boundary, not from an arbitrary implementation roadmap.

## Initial execution order

The 100 questions are intentionally not numbered as a mandatory implementation sequence. For the current repository state, the highest-value early track is:

`71–80 GitHub external-system proof → 31–40 real provider execution → 61–70 external-effect semantics → 81–90 recovery → 91–100 learning-loop validation`.

Questions 1–30 and 41–60 should be used whenever an experiment exposes an ambiguity in boundaries, authority, content identity, revision, or verification.
