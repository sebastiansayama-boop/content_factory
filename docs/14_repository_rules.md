# 14 — Repository Rules

These rules govern how `content_factory` is used while it remains a research and model-building environment.

## R1 — Evidence before model

External findings, case observations and experiment results are evidence. They do not become part of `model/` automatically.

Path preference:

```text
raw input → observation/research → reasoning → decision → model
```

## R2 — Current model is not history

`model/` describes the current working model. Historical alternatives belong in `10_records/` or `archive/`.

Never use an old document as a current instruction merely because it is present in Git.

## R3 — One object, one lifecycle

Do not build one giant state machine that treats unrelated objects as one object.

Candidate, research, knowledge revision, editorial decision, specification revision, asset revision, verification result, release, observation and learning have separate lifecycles.

A case-level pipeline is a projection over these lifecycles.

## R4 — Revision is part of identity for mutable information

Whenever a verification, acceptance or publication decision concerns mutable information, identify the exact revision.

```text
object_id + revision_id
```

is the minimum meaningful target.

## R5 — Never silently mutate accepted history

Material changes produce a new revision.

Do not rewrite a published or accepted historical state in place merely to make the current output look correct.

## R6 — Observation is not interpretation

Record what happened before explaining why it happened.

```text
observation → interpretation → learning candidate
```

Do not write conclusions into observation records.

## R7 — Learning is not automatically knowledge

A learning candidate requires explicit support before it can alter reusable knowledge or the working model.

## R8 — Unknown is valid

When the repository does not know something, record the unknown explicitly.

Never fill an evidence gap with plausible generated content.

## R9 — Provenance and dependency are different

`produced_from` answers where something came from.

`depends_on` answers what must remain valid for it to remain usable.

`impacts` answers what requires reconsideration when an upstream object changes.

Do not collapse these relations into one generic `source` field.

## R10 — Decisions are bounded

Every significant decision should identify:

```text
what
which revision
based on what evidence
who has authority
what is authorized
what is not authorized
```

## R11 — Review is not acceptance

A successful check means only that the check passed.

It does not imply human/product acceptance unless the workflow explicitly defines that equivalence and the case demonstrates that it is safe.

## R12 — Acceptance is not external effect

Saving, producing, verifying, accepting and publishing are separate operations.

An external effect requires an explicit transition and an identifiable target revision/release.

## R13 — Production cannot silently expand facts

Production can transform approved knowledge into a representation. It cannot silently introduce new factual claims.

A new factual claim re-enters the appropriate research/verification boundary.

## R14 — No automatic propagation of authority

A role that owns one transition does not automatically own downstream decisions.

Authority must be explicit at each decision boundary.

## R15 — Pull, not uncontrolled propagation

The existence of knowledge does not create publication work automatically.

Editorial need pulls relevant knowledge into a production job.

## R16 — New folders require repeated need

Do not create a new top-level zone for one unusual example.

A new folder should appear only when a distinct information type or control boundary recurs and cannot be represented safely by an existing zone.

## R17 — Do not copy Atlas execution controls without need

Leases, heartbeats, process isolation, worker reclaim, shell argument restrictions and similar controls belong to execution infrastructure unless a real editorial case demonstrates that the same failure mode exists here.

## R18 — Cases are the primary validator

A conceptual rule is not considered stable merely because it is elegant.

Test it against real editorial cases and record:

```text
expected transition
observed transition
failure / ambiguity
model consequence
```

## R19 — Research the question before inventing the answer

When a structural question is unresolved, search external references and inspect relevant existing repositories before adding a new primitive, state or process.

## R20 — Every model change must be traceable

A change to `model/` should be explainable through one or more of:

```text
research finding
experiment result
case failure
explicit decision
```

If no reason can be cited, the change is premature.

## R21 — Keep current state inspectable

A person entering the repository should be able to determine quickly:

```text
what the current model is
what is historical
what is unknown
what is under investigation
what changed most recently
```

## R22 — Do not turn the analogy into ontology

The brain analogy is useful for discovering functions and relationships. It does not establish that a repository folder corresponds to one anatomical structure or that a software state has a biological equivalent.

When neuroscience and the repository model diverge, preserve the repository model that is better supported by information-flow evidence.

## R23 — Prefer explicit transitions over implied meaning

Do not infer state from filenames, timestamps or the mere existence of an artifact.

Use explicit state and decision records.

## R24 — History observes the system

`10_records/` records what happened. It must not become an alternate current model.

## R25 — Archive is inert by default

Material in `archive/` has no current authority and must not be reactivated implicitly.
