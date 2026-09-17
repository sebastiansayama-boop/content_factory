# User Sector 1 — Source to Reviewable Content Package

## Product sector

One complete user-visible business flow:

1. open Content Factory;
2. paste a substantive source and optional title;
3. analyze the source;
4. inspect summary, themes, stories, moments, and source evidence;
5. select one story angle from that source;
6. generate an article and/or social posts;
7. review and edit the generated assets;
8. copy a final asset for use outside the factory.

The sector is deliberately narrow. It does not try to be a general content platform yet.

## Included

- text source input;
- AI analysis;
- explicit story selection;
- source identity attached to analyzed stories;
- evidence-backed story selection;
- article generation;
- social-post generation;
- source references on generated assets;
- inline editing;
- clipboard export.

## Excluded

- transcription;
- media generation;
- video scripts;
- external publishing;
- scheduling;
- accounts;
- billing.

## User-value hypothesis

A user with substantive source material can turn one source into a coherent article and social-post package faster than producing each asset independently, while retaining visibility into the selected story and its source evidence.

## Definition of done for this sector

The sector is complete only when the same path works end-to-end:

`SOURCE → ANALYZE → STORIES + EVIDENCE → SELECT → ARTICLE + SOCIAL POSTS → REVIEW → COPY`

The following must all be observable:

- public user interface is reachable;
- real AI provider generates the analysis and package;
- selected story is tied to the analyzed source;
- generated assets contain source references;
- generated assets are editable;
- a user can copy the result without developer intervention;
- the deployed path can be repeated from a clean session.

Automated tests are necessary evidence for specific technical properties but are not the user-test verdict.

## User-test gate

The user test observes:

- task completion without developer intervention;
- whether the user understands the Source → Explore → Produce flow;
- whether the user can identify and select a useful story;
- whether the article and social posts are usable;
- whether source references affect trust;
- what the user edits or rejects;
- where the user becomes blocked or confused.

## Technical boundary

The sector uses the executable factory runtime and the configured production AI provider. Draft generation stays behind the internal release boundary; external publishing is not part of this sector.

## Evidence boundary

A successful user task is evidence about usability and perceived value for that tested case. It is not evidence of market demand, retention, willingness to pay, or general product-market fit.
