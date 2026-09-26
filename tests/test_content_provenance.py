from content_factory.content_provenance import (
    ContentAsset,
    EditorialUnit,
    ProvenanceGraph,
    ProvenanceLink,
)


def test_cross_provider_provenance_links_editorial_unit_to_asset():
    graph = ProvenanceGraph()
    graph.add_editorial_unit(
        EditorialUnit(
            unit_id="eu-001",
            run_id="run-001",
            kind="youtube_sentence",
            text="Example factual statement.",
            provenance=ProvenanceLink(
                source_ids=("src-001",),
                evidence_ids=("ev-001",),
                claim_ids=("claim-001",),
            ),
        )
    )
    asset = graph.add_asset(
        ContentAsset(
            asset_id="asset-001",
            run_id="run-001",
            format="youtube_script",
            provider="provider-a",
            provider_job_id="job-001",
            editorial_unit_ids=("eu-001",),
        )
    )

    assert graph.affected_assets(claim_id="claim-001") == [asset]


def test_asset_cannot_reference_unknown_editorial_unit():
    graph = ProvenanceGraph()

    try:
        graph.add_asset(
            ContentAsset(
                asset_id="asset-001",
                run_id="run-001",
                format="video",
                provider="provider-b",
                provider_job_id="job-002",
                editorial_unit_ids=("missing",),
            )
        )
    except ValueError as exc:
        assert "unknown editorial units" in str(exc)
    else:
        raise AssertionError("expected provenance validation failure")


def test_duplicate_asset_identity_is_rejected():
    graph = ProvenanceGraph()
    graph.add_asset(
        ContentAsset(
            asset_id="asset-001",
            run_id="run-001",
            format="image",
            provider="provider-c",
            provider_job_id="job-003",
        )
    )

    try:
        graph.add_asset(
            ContentAsset(
                asset_id="asset-001",
                run_id="run-001",
                format="image",
                provider="provider-c",
                provider_job_id="job-004",
            )
        )
    except ValueError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("expected duplicate asset failure")
