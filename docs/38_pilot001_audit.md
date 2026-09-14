# Pilot001 Audit

## Product target

Pilot001 is the first real product loop for Content Factory:

`direction -> current research -> content angle -> post -> carousel -> Telegram review -> human approval/rejection/regeneration -> manual publication`

The objective is not to prove an HTTP integration. The objective is to produce a useful content package from a direction with minimal human intervention.

## Audit against stated goals

### User goal: choose a direction
Status: IMPLEMENTED.

Telegram accepts `/pilot <direction>`.

### User goal: research audience/market signals
Status: IMPLEMENTED_V0.

Pilot001 retrieves current Google News RSS results for the direction, plus separate trend/audience queries. This is signal collection, not a full market research engine.

### User goal: make production decisions autonomously
Status: IMPLEMENTED_V0.

The local model selects an angle, explains why it is timely, chooses research items, writes the post and decomposes it into carousel slides.

### User goal: receive a finished package in Telegram
Status: IMPLEMENTED_V0.

The system sends the post preview and generated PNG carousel assets through the Telegram Bot API.

### User goal: regenerate
Status: IMPLEMENTED_V0.

`Regenerate` creates a new draft using the same research context and a new revision/angle.

### User goal: human remains the publication boundary
Status: IMPLEMENTED.

`Approve` stops the automated loop at approval and explicitly tells the user to publish manually to Instagram / Threads.

### User goal: real execution without paid API dependency
Status: IMPLEMENTED_V0.

Ollama is used as the default model provider. The default model is `qwen3:8b`, configurable through `OLLAMA_MODEL`.

## Acceptance criteria

Pilot001 is accepted only when all of the following are observed on the user's machine:

1. `/pilot <direction>` produces a non-empty research set.
2. Ollama produces a structured draft with an angle, post and >=4 carousel slides.
3. PNG carousel assets are created on disk.
4. Telegram receives the package.
5. Regenerate produces a distinct revision without changing the original draft record.
6. Approve persists an `APPROVED` state and does not publish externally.
7. Reject persists a `REJECTED` state.
8. The output files and draft metadata remain available after process restart.

## Not yet claimed

Pilot001 does not yet claim:

- autonomous Instagram publication;
- autonomous Threads publication;
- image-model generation;
- long-horizon planning;
- autonomous QA beyond structural/model constraints;
- audience-performance feedback;
- learning from published outcomes.

Those are next experiments only after Pilot001 produces a real human-reviewed result.
