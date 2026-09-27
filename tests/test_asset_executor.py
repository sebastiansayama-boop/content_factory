from content_factory.asset_executor import AssetExecutor
from content_factory.asset_jobs import AssetJobStore


def test_stub_executor_materializes_asset_candidate(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_ASSET_PROVIDER", "stub")
    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    plan = {
        "asset_requests": [
            {
                "asset_request_id": "request-1",
                "script_unit_id": "unit-1",
                "type": "visual",
                "claim_refs": ["kc-1"],
                "evidence_refs": ["ke-1"],
                "acceptance_criteria": ["preserve provenance"],
            }
        ]
    }
    jobs.create_from_plan("run-1", plan)

    result = AssetExecutor(jobs, tmp_path).execute_run("run-1")

    assert len(result) == 1
    assert result[0].status == "COMPLETED"
    assert result[0].result["provider"] == "stub"
    assert result[0].result["asset_id"].startswith("asset-")
    assert result[0].result["claim_refs"] == ["kc-1"]

    jobs.close()
