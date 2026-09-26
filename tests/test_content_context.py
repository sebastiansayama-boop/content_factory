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
        claim_ids=("claim-17",),
        evidence_ids=("evidence-12",),
        editorial_unit_ids=("editorial-12",),
        constraints=("avoid generic western ghost imagery",),
        source_asset_ids=("asset-02",),
    )

    provider = to_provider_context(context, provider="image")

    assert provider.run_id == "run-001"
    assert provider.task_id == "visual-004"
    assert provider.claim_ids == ("claim-17",)
    assert provider.editorial_unit_ids == ("editorial-12",)
    assert provider.constraints == ("avoid generic western ghost imagery",)
    assert provider.source_asset_ids == ("asset-02",)


def test_provider_translation_does_not_forward_irrelevant_evidence_to_media():
    context = ContentContext(
        run_id="run-001",
        task_id="video-004",
        purpose="illustrate a scene",
        claim_ids=("claim-17",),
        evidence_ids=("evidence-12",),
        editorial_unit_ids=("editorial-12",),
    )

    provider = to_provider_context(context, provider="video")

    assert provider.claim_ids == ("claim-17",)
    assert provider.editorial_unit_ids == ("editorial-12",)
    assert provider.source_asset_ids == ()
    assert not hasattr(provider, "evidence_ids")


def test_research_provider_receives_evidence_identity():
    context = ContentContext(
        run_id="run-001",
        task_id="research-001",
        purpose="verify claim",
        claim_ids=("claim-17",),
        evidence_ids=("evidence-12",),
    )

    provider = to_provider_context(context, provider="research")

    assert provider.provider == "research"
    assert provider.claim_ids == ("claim-17",)
    assert provider.editorial_unit_ids == ()
    assert provider.constraints == ()


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
