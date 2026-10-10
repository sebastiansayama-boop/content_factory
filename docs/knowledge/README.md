# Knowledge and skills registry

Purpose: retain reusable knowledge discovered during real Content Factory work, without turning documentation into a new execution architecture.

## Information types
| Type | Meaning | Storage | Use |
| --- | --- | --- | --- |
| FACT | Stable, source-supported principle | knowledge/<domain>.md | Ground generation and QC |
| HEURISTIC | Practical rule that depends on conditions | skills/<skill>.md | Guide production |
| PROCEDURE | Repeatable steps with inputs, outputs and checks | skills/<skill>.md | Execute a task |
| CONSTRAINT | Must/avoid rule or platform requirement | Existing product contract or skill | Gate outputs; recheck time-sensitive policies |
| OBSERVATION | Result of a specific real run | Run/ExperienceRecord, not generic knowledge | Diagnose and learn |
| HYPOTHESIS | Plausible but unverified explanation | Skill's open questions | Test before promoting |
| FUTURE | Useful possible capability without a demonstrated need | Skill's future considerations | Do not implement prematurely |

## Capture rules
1. When a reusable insight emerges, classify it; preserve the distinction between established principles, heuristics, observations and hypotheses.
2. Store domain knowledge once; link to it from relevant skills. Avoid duplicating the same rule across files.
3. Each skill specifies trigger, inputs, steps, expected output, QC, limits and future considerations.
4. Real results belong to ExperienceRecord or a linked test record; do not label an unrun check as passed.
5. Update only documentation or a proven broken workflow; do not build new registries, agents, pipelines or gates without a real failing scenario.
6. Cite external references where available, and date-check provider/platform policies before relying on them.

Current entries:
- [Photography principles](photography.md)
- [Natural photo generation skill](../skills/natural_photography.md)
