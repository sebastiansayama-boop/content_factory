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


def test_production_package_maps_one_claim_to_multiple_affected_assets():
    package = {
        "package": [
            {
                "id": "article-001",
                "format": "article",
                "claim_refs": ["claim-001"],
            },
            {
                "id": "video-001",
                "format": "long_video",
                "claim_refs": ["claim-001", "claim-002"],
            },
            {
                "id": "social-001",
                "format": "social_post",
                "claim_refs": ["claim-002"],
            },
        ]
    }

    graph = ProvenanceGraph.from_package(package, run_id="run-001")

    assert graph.affected_asset_ids(claim_id="claim-001") == [
        "article-001",
        "video-001",
    ]
    assert graph.affected_asset_ids(claim_id="claim-002") == [
        "video-001",
        "social-001",
    ]
    assert graph.affected_asset_ids(claim_id="claim-003") == []


def test_production_package_rejects_invalid_claim_refs():
    package = {
        "package": [
            {
                "id": "asset-001",
                "format": "video",
                "claim_refs": ["claim-001", 2],
            }
        ]
    }

    try:
        ProvenanceGraph.from_package(package, run_id="run-001")
    except ValueError as exc:
        assert "claim_refs" in str(exc)
    else:
        raise AssertionError("expected invalid claim_refs failure")


def test_regeneration_plan_only_rebuilds_assets_affected_by_changed_claims():
    package = {
        "package": [
            {"id": "article-001", "format": "article", "claim_refs": ["claim-001"]},
            {"id": "video-001", "format": "video", "claim_refs": ["claim-001", "claim-002"]},
            {"id": "social-001", "format": "social_post", "claim_refs": ["claim-002"]},
            {"id": "image-001", "format": "image", "claim_refs": ["claim-003"]},
        ]
    }

    graph = ProvenanceGraph.from_package(package, run_id="run-001")

    plan = graph.regeneration_plan(changed_claim_ids=["claim-001"])

    assert plan.changed_claim_ids == ("claim-001",)
    assert plan.regenerate_asset_ids == ("article-001", "video-001")
    assert plan.retain_asset_ids == ("social-001", "image-001")


def test_regeneration_plan_deduplicates_overlapping_claim_dependencies():
    package = {
        "package": [
            {"id": "video-001", "format": "video", "claim_refs": ["claim-001", "claim-002"]},
            {"id": "article-001", "format": "article", "claim_refs": ["claim-002"]},
        ]
    }

    graph = ProvenanceGraph.from_package(package, run_id="run-001")

    plan = graph.regeneration_plan(changed_claim_ids=["claim-001", "claim-002"])

    assert plan.regenerate_asset_ids == ("video-001", "article-001")
    assert plan.retain_asset_ids == ()
