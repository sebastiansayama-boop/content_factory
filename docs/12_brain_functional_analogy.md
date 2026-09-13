# 12 — Brain Functional Analogy

This analogy is a design heuristic, not a claim that a repository or software system literally reproduces the human brain.

Modern neuroscience describes cognition through interacting distributed networks rather than isolated brain modules. Executive-control, salience, attention, default-mode, memory and sensorimotor systems dynamically interact. citeturn842770search1turn842770search3turn842770search8

## Functional analogy

| Human cognitive function | Useful analogy in Content Factory | Repository implication |
|---|---|---|
| Sensory input | signals, sources, incoming observations | `00_inbox/`, `01_observation/` |
| Salience / switching | decide what deserves attention | candidate admission, triage, research queue |
| Working memory / executive control | current task context and constraints | `03_working_context/` |
| Episodic / relational memory | recoverable prior episodes, sources, evidence and their relationships | `02_memory/`, `10_records/` |
| Semantic knowledge | reusable claims, context, evidence relationships | `02_memory/knowledge/` |
| Executive control | maintain goals, constraints, compare alternatives, choose next action | `04_reasoning/`, `05_decision/` |
| Action selection | select an authorized editorial action | decision records and transition rules |
| Motor execution | produce a concrete artifact | `06_production/` |
| Error monitoring / correction | detect mismatch and request revision | `07_verification/` |
| External interaction | publish and observe consequences | `08_effects_feedback/` |
| Learning / plasticity | revise future behavior and knowledge from experience | `09_learning/` |

## Important neuroscientific qualifications

### The brain is networked, not foldered

A repository folder should represent a stable information function or boundary, not a literal brain structure. Brain functions are distributed and dynamically coupled. citeturn842770search8

### Memory is not one store

The hippocampus and prefrontal cortex interact during episodic memory tasks, while large-scale networks also contribute to semantic and autobiographical processing. The repository should therefore distinguish durable records, reusable knowledge and active working context rather than creating one generic `memory/` bucket. citeturn842770search0turn842770search3

### Executive control is not the same as information storage

The frontoparietal/executive network is associated with working memory, task switching and cognitive control. This is a useful analogy for a separate working-context and decision layer. citeturn842770search1turn842770search11

### Salience is a switching function

The salience network is associated with detecting behaviorally relevant events and coordinating shifts between internally focused and externally directed modes. This is a useful analogy for triage and attention routing, not for a literal "salience folder." citeturn842770search3turn842770search12

### Action and learning are coupled

Research on prefrontal, basal-ganglia and thalamic interactions describes action selection, monitoring of ongoing actions and retrospective updating of strategies. This supports separating decision, effect and learning rather than collapsing them into one state. citeturn842770search7

## Design conclusion

The repository should behave less like a document archive and more like a functional cognitive environment:

```text
INPUT
  ↓
ATTENTION / TRIAGE
  ↓
MEMORY + WORKING CONTEXT
  ↓
REASONING
  ↓
DECISION
  ↓
ACTION / PRODUCTION
  ↓
VERIFICATION
  ↓
EXTERNAL EFFECT
  ↓
OBSERVATION
  ↓
LEARNING
  ↺
```

The repository must preserve both the current working state and the historical evidence that explains how it was reached.
