# Learning Loop Research — Program 1 synthesis

Date: 2026-09-13
Status: `COMPLETED / EXTERNAL EVIDENCE SYNTHESIS`
Scope: A–P learning mechanism research tree

## Research question

Can Content Factory use accumulated experience to change later behavior in a controlled, evidence-aware and reversible way without converting isolated observations into false reusable knowledge?

## Epistemic rule

Repository state is evidence of what Content Factory contains or has executed. It is not evidence that an external principle is universally valid. General claims below are supported only where external scientific, empirical, normative, or documented real-world evidence was found.

## External evidence base

1. Tannenbaum & Cerasoli, 2013, meta-analysis of 46 debrief samples: after-action reviews/debriefs improved effectiveness on average; alignment, facilitation and structure influenced effect.
   https://pubmed.ncbi.nlm.nih.gov/23516804/
2. Tannenbaum et al., 2020/2021, meta-analysis of 61 studies: AAR/debriefing effects depend on interacting characteristics; objective performance review and alignment were recurring contributors.
   https://pubmed.ncbi.nlm.nih.gov/32852990/
3. Sanna & Lagnado, 2025, four experiments on belief updating: source reliability, trustworthiness and expertise affected updating under contradictory information.
   https://pubmed.ncbi.nlm.nih.gov/39986181/
4. Burchett et al., 2011, review of external-validity/applicability/transferability frameworks: criteria clustered around setting, intervention, outcomes and evidence; frameworks were heterogeneous and incompletely validated.
   https://pubmed.ncbi.nlm.nih.gov/21965426/
5. Weise et al., 2020, integrative review: context suitability/generalizability/transferability assessment is heterogeneous and must be tailored to context.
   https://pubmed.ncbi.nlm.nih.gov/32920989/
6. NIST AI RMF Measure: recommends repeatable TEVV, uncertainty, validity/reliability, documented generalizability limits, feedback and continual reassessment.
   https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
7. NIST AI RMF Playbook Measure 2.5: distinguishes construct, internal and external validity and calls for documenting operating conditions, assumptions, variance, robustness and reliability.
   https://airc.nist.gov/docs/AI_RMF_Playbook.pdf
8. Agent Security Bench, ICLR 2025: benchmarked memory poisoning among other attacks and found vulnerabilities in memory retrieval and other agent stages.
   https://proceedings.iclr.cc/paper_files/paper/2025/hash/5750f91d8fb9d5c02bd8ad2c3b44456b-Abstract-Conference.html
9. Mem2ActBench, ACL 2026: distinguishes passive memory retrieval from active memory use in tool-based task execution and reports inadequate active memory utilization in evaluated systems.
   https://aclanthology.org/2026.acl-long.370/
10. Memory poisoning attacks on RAG agents, Engineering Applications of Artificial Intelligence, 2026: reports strong attack success and generalization across models/retrievers against memory-augmented agents.
    https://www.sciencedirect.com/science/article/pii/S0952197626002496
11. Systematic review of knowledge-management systems, 2025: identifies competency traps caused by codification bias, algorithmic reinforcement, rigid governance, narrow classification and failure to remove outdated knowledge; recommends challenge/unlearning mechanisms.
    https://www.sciencedirect.com/science/article/pii/S2468227625004168
12. NIST AI RMF Effectiveness: states that framework users should periodically evaluate whether risk-management practices improve processes and outcomes rather than assuming effectiveness from adoption.
    https://airc.nist.gov/airmf-resources/airmf/4-effectiveness/

## Program-wide findings

### A — Epistemic integrity

`SUPPORTED`: observation, evidence, interpretation and claim should not be collapsed; provenance and uncertainty require explicit treatment. Evidence quality and validity are distinct from the existence of an observation.

`NOT ESTABLISHED`: a universal evidence score or a Content Factory-specific ontology is externally validated.

### B — Promotion

`SUPPORTED`: experience can be converted into lessons and application of lessons can improve performance in studied settings.

`NOT ESTABLISHED`: one universal promotion threshold, automatic promotion, or a proof that any particular promotion predicate guarantees future usefulness.

### C — Retrieval

`SUPPORTED`: retrieval is a separate capability and can be evaluated quantitatively.

`SUPPORTED`: retrieval success is not equivalent to successful task use. Mem2ActBench explicitly evaluates active memory use in tool execution.

`NOT ESTABLISHED`: vector search, graph storage, or a separate memory service is universally required.

### D — Decision impact

`SUPPORTED`: decision-support interventions can alter decisions and, in some settings, improve outcomes.

`SUPPORTED`: changing a decision does not by itself prove improved outcome; prospective evaluation is required.

`NOT ESTABLISHED`: a universal decision-delta metric.

### E — Validation

`SUPPORTED`: reproduction, robustness, falsification and generalizability are distinct concerns. NIST explicitly separates validity, reliability, robustness and generalizability limits.

### F — Contradiction

`SUPPORTED`: contradictory evidence requires evaluation, not blind replacement. Source reliability and credibility affect belief updating.

`NOT ESTABLISHED`: contradiction should always invalidate prior knowledge. Scope changes, source-quality differences and context changes can produce different resolutions.

### G — Lifecycle

`SUPPORTED`: knowledge can become stale and knowledge-management systems can reinforce outdated practices. Deliberate challenge/unlearning is externally supported.

`NOT ESTABLISHED`: the exact Content Factory state machine (`CANDIDATE`, `PROMOTED`, `ACTIVE`, `STALE`, `CONTRADICTED`, `SUPERSEDED`, `REJECTED`, `RETIRED`) is externally validated.

### H — Attribution

`SUPPORTED`: temporal sequence is not causal attribution. Causal claims require appropriate intervention/counterfactual or other causal-inference designs.

`NOT ESTABLISHED`: complete causal attribution is always necessary for operational reuse; the required confidence depends on consequence and use.

### I — Transfer

`SUPPORTED`: applicability/transferability requires context assessment. Setting, intervention, outcomes and evidence are recurring dimensions in external-validity literature.

`NOT ESTABLISHED`: semantic similarity alone is a valid transfer criterion or a universal transfer threshold exists.

### J — Automation

`SUPPORTED`: retrieval, measurement and candidate generation can be automated in principle and are actively researched.

`SUPPORTED`: automation introduces new failure/security modes; memory retrieval is an attack surface.

`NOT ESTABLISHED`: automatic promotion or automatic authority is safe as a default.

### K — Architecture

`NOT ESTABLISHED`: any specific database/search architecture is mandatory. Mechanism choice should follow demonstrated workload, query class, scale and required guarantees.

### L — Governance/security

`SUPPORTED`: measurement, documentation, validity limits, feedback, human intervention and continual improvement are established governance practices. Memory poisoning is empirically demonstrated in agent research.

### M — Measurement

`SUPPORTED`: learning mechanisms require process, quality and outcome measurement; measurement itself must be evaluated for validity and effectiveness.

`NOT SUPPORTED`: memory count, retrieval count or promotion count alone is a quality metric.

### N — External learning

`SUPPORTED AS REAL-WORLD ANALOGUE`: after-action/lessons-learned systems in operational organizations demonstrate loops from experience to lessons to changed practice.

`NOT PROVEN FOR CONTENT FACTORY`: Content Factory has not yet demonstrated a real external effect followed by outcome-based memory revision.

### O — Meta-learning

`SUPPORTED AS RELATED RESEARCH AREA`: adaptive systems and concept-drift research establish the problem of systems needing to detect changing conditions.

`NOT ESTABLISHED`: self-modification of Content Factory's own learning policy is safe or effective.

### P — Product-level learning

`SUPPORTED`: organizational learning and structured debriefing can correlate with or improve performance in studied settings.

`NOT ESTABLISHED`: Content Factory learning will improve business/product outcomes without direct outcome evidence.

## Consolidated learning mechanism

External evidence supports treating these as distinct claims:

1. knowledge is valid;
2. knowledge is applicable to this context;
3. knowledge was retrieved;
4. knowledge was used;
5. knowledge changed a decision;
6. the changed decision changed execution;
7. execution changed an external outcome;
8. the outcome provides evidence about the knowledge;
9. the knowledge is retained, revised, superseded, scoped, or rejected accordingly.

No one of these states proves the next.

## Security boundary

Memory admission is a security boundary. External evidence and retrieved content must not become trusted reusable knowledge merely because they entered the repository or memory store. Agent Security Bench and later memory-poisoning research demonstrate attacks targeting memory retrieval and knowledge bases.

## Evolution candidate

The current Content Factory model should evolve from a mostly linear learning representation to an explicit, bounded loop with these semantic distinctions:

`candidate → validation/applicability → reusable knowledge → retrieval → application/decision → execution → outcome → evaluation → retain/revise/supersede/reject`.

This is a model evolution, not an implementation mandate. No vector database, knowledge graph, automatic promotion, or self-modifying learning engine is justified by this research alone.

## Remaining empirical frontier

The next proof boundary is L6 → L7 → L8 → L9 → L10:

`memory changes decision → decision changes execution → real external outcome → outcome evaluates memory → memory revision`.

The first real external case should be bounded, reversible where possible, explicitly authorized, and designed to capture expected state, actual state, outcome, attribution confidence, and memory effect.

## Classification summary

- `SUPPORTS_CURRENT_MODEL`: provenance, explicit separation of observation/interpretation/decision/effect, explicit promotion, external-effect boundary, explicit governance.
- `EXTENDS_CURRENT_MODEL`: applicability, active memory use, outcome evaluation, deliberate unlearning/challenge, memory as security boundary, measurement of learning effectiveness.
- `REVEALS_GAP`: causal attribution, transfer evidence, real external feedback, contradiction resolution, automatic promotion safety.
- `NOT_APPLICABLE`: none identified for the core learning mechanism.
- `UNCERTAIN`: universal promotion threshold, exact lifecycle ontology, exact retrieval architecture, automatic self-modification.

## Evidence limitation

The external sources establish mechanisms, empirical findings, or normative evaluation practices in their respective contexts. They do not prove that the same mechanisms will work unchanged in Content Factory. Local correctness still requires controlled experiments and real operational evidence.
