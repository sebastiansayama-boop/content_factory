from content_factory.content_context import (
    ContentContext,
    ContextError,
    to_provider_context,
)


def test_provider_translation_preserves_shared_identity_and_semantics():
    context = ContentContext(
        run_id="run-001",
        task_id="visual-004",
        purpose="illustrate phra phum",
        claims=("claim-17: Phra Phum is distinct from Jao Thii",),
        evidence=("evidence-12: source excerpt",),
        editorial_units=("editorial-12: explain distinction",),
        constraints=("avoid generic western ghost imagery",),
        source_asset_ids=("asset-02",),
    )

    provider = to_provider_context(context, provider="image")

    assert provider.run_id == "run-001"
    assert provider.task_id == "visual-004"
    assert provider.claims == context.claims
    assert provider.editorial_units == context.editorial_units
    assert provider.constraints == context.constraints
    assert provider.source_asset_ids == ("asset-02",)


def test_provider_translation_does_not_forward_irrelevant_evidence_to_media():
    context = ContentContext(
        run_id="run-001",
        task_id="video-004",
        purpose="illustrate a scene",
        claims=("claim-17: factual statement",),
        evidence=("evidence-12: source excerpt",),
        editorial_units=("editorial-12: scene instruction",),
    )

    provider = to_provider_context(context, provider="video")

    assert provider.claims == ("claim-17: factual statement",)
    assert provider.editorial_units == ("editorial-12: scene instruction",)
    assert provider.source_asset_ids == ()
    assert provider.evidence == ()


def test_research_provider_receives_evidence_context():
    context = ContentContext(
        run_id="run-001",
        task_id="research-001",
        purpose="verify a claim",
        claims=("claim-17: factual statement",),
        evidence=("evidence-12: source excerpt",),
    )

    provider = to_provider_context(context, provider="research")

    assert provider.provider == "research"
    assert provider.claims == context.claims
    assert provider.evidence == context.evidence


def test_text_provider_receives_claim_and_editorial_context():
    context = ContentContext(
        run_id="run-001",
        task_id="text-001",
        purpose="write the narration",
        claims=("claim-17: factual statement",),
        evidence=("evidence-12: source excerpt",),
        editorial_units=("editorial-12: narration instruction",),
    )

    provider = to_provider_context(context, provider="text")

    assert provider.claims == context.claims
    assert provider.editorial_units == context.editorial_units
    assert provider.evidence == ()


def test_context_requires_stable_identity():
    try:
        to_provider_context(
            ContentContext(
                run_id="",
                task_id="task-001",
                purpose="produce",
            ),
            provider="text",
        )
    except ContextError as exc:
        assert "run_id" in str(exc)
    else:
        raise AssertionError("expected context validation failure")
