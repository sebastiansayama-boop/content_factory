# First executable Content Factory test

This is the smallest real vertical slice used to test the factory as a content-production system.

## Scope

```text
source fixture
  -> /api/analyze
  -> editorial stories + source evidence
  -> select one story
  -> /api/produce
  -> article + social_posts
  -> runtime identity
```

The test deliberately excludes transcription, media ingestion, image/video generation, external publishing, audience metrics, and business outcomes.

## Preconditions

The service must be running and configured with a real text-generation provider. `FACTORY_API_TOKEN` must be available to the test process.

For a local run, start the product HTTP service with the required provider credentials and authority configuration, then run:

```text
python scripts/first_prototype_test.py
```

For a hosted service:

```text
FACTORY_URL=https://<service> FACTORY_API_TOKEN=<token> python scripts/first_prototype_test.py
```

No secret belongs in Git.

## Pass criteria

The test passes only when all of these are observed from the service response:

1. `/api/analyze` returns at least one story with an id and title.
2. The selected story is sent explicitly to `/api/produce`.
3. `/api/produce` returns both requested formats: `article` and `social_posts`.
4. The production response contains `work_item_id`, `operation_id`, `execution_id`, `output_revision_id`, and a final runtime state.
5. The final state is `OBSERVED` or `DELIVERED`.

A passing test proves that this bounded execution path worked. It does not prove factual accuracy, editorial quality, audience value, or external business outcome.

## Why this is the first test

Official verification guidance recommends combining automated testing and static analysis with checks against requirements and intended behavior. NIST explicitly describes verification as a set of interrelated techniques rather than a single test, and GitHub's guidance for AI-generated code likewise separates functional checks from context, intent, quality, dependencies, and AI-specific pitfalls. This prototype therefore starts with one observable functional slice before adding additional quality gates.
