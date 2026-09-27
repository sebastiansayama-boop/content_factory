from content_factory.asset_jobs import AssetJobStore
from content_factory.asset_poller import AssetJobPoller


def test_stub_poll_completes_submitted_job(tmp_path):
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
    job = jobs.mark_running("job-run-1-request-1")
    jobs.submit(job.job_id, {
        "provider": "stub",
        "provider_request_id": "stub-1",
        "asset_id": "asset-1",
    })

    result = AssetJobPoller(jobs).poll_run("run-1")

    assert result[0].status == "COMPLETED"
    assert result[0].result["asset_id"] == "asset-1"
    jobs.close()
