# Product Brief — Content Factory End-user Content Workspace

Status: `ACCEPTED / STAGE 0 PASS`

## Product

`Content Factory — End-user Content Workspace / text-source vertical slice`

## Desired outcome

Give a user a bounded workspace in which existing source material can be explored for distinct, evidence-grounded stories and a selected story can be turned into a reusable multi-format content package.

The product outcome is not simply "generate content". The intended outcome is a controlled path from source material to a selected editorial direction and then to usable draft assets, while preserving the connection to the source.

## Primary user / context

Primary user: a person responsible for turning substantive source material into multiple content formats and who needs to choose the editorial angle before production.

Current bounded context: one user, one supplied text source, one workspace session, and a bounded set of output formats. The repository does not currently prove a broader multi-user, media-ingestion, or publishing product context.

## In scope

- accept pasted source text;
- analyze the source into summary, themes, stories, evidence and moments;
- let the user select one story;
- produce requested content formats from the selected story and original source;
- preserve source/story/evidence references in the product response;
- execute analysis and production through the existing factory runtime;
- keep workspace-generated output on the internal draft/release boundary.

## Out of scope for this case

- media upload and transcription;
- autonomous discovery of market opportunities;
- user research or competitor research performed by the workspace itself;
- product strategy decisions;
- multi-user identity and permissions;
- external publication;
- claims that draft generation proves audience or business outcomes;
- replacing the upstream Discovery / Decision function.

## Constraints

- source-grounded generation; unsupported facts must not be introduced;
- production must occur only after an editorial story is selected;
- existing runtime and semantic boundaries are reused rather than creating a parallel execution system;
- external publication is not implied by draft generation;
- credentials and external-effect authority remain outside the workspace product surface;
- the product must remain bounded enough that its lifecycle gates can be evaluated independently.

## Initial success signals

For this Stage 0 case, success signals are intentionally provisional and are not yet treated as validated product metrics:

1. a user can move from supplied source to a materially distinct story choice;
2. the selected story remains traceable to source evidence;
3. requested output formats are produced without unsupported factual invention;
4. the user can inspect the resulting package before any external effect;
5. the path is sufficiently understandable that the user does not need to reconstruct the editorial decision outside the workspace.

These are hypotheses to be tested during Discovery and Solution Validation, not evidence that the product currently achieves them.

## Critical unknowns

- whether users actually need story exploration before production, rather than direct transformation;
- whether the proposed story/evidence representation is understandable and useful to the target user;
- which source types and lengths constitute the highest-value initial use case;
- which output formats provide meaningful value versus superficial repackaging;
- whether source traceability materially increases trust or review efficiency;
- what users currently do instead and where the current workflow fails;
- which product outcome should ultimately determine investment beyond successful draft generation.

## Stage 0 gate decision

`PROCEED → STAGE 1 DISCOVERY`

The brief satisfies the lifecycle Stage 0 exit gate: it states why the initiative exists, who/what is in scope, the sought outcome, material constraints, explicit non-goals, and the material questions that must be answered in Discovery. fileciteturn230file0

External practice is consistent with this boundary. GOV.UK guidance treats Discovery as the phase for understanding users, current behaviour, problems, needs, constraints and alternatives before planning/design/build, and recommends turning assumptions into explicit research questions. citeturn0search0turn0search3turn0search8

This gate decision does not validate the problem, demand, solution or success signals. It only authorizes movement from Product Brief to Discovery.

## Stage 1 boundary

The next permitted work is Discovery. Discovery must investigate the critical unknowns above using evidence from users/context, existing workflows, relevant alternatives/market/domain research and available data. No Discovery finding becomes a product decision or build authorization without an explicit later gate.

No implementation change is authorized by this gate decision.
