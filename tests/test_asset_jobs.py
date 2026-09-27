from content_factory.asset_jobs import AssetJobStore


def test_asset_jobs_are_durable_and_idempotent(tmp_path):
    store = AssetJobStore(tmp_path / "jobs.sqlite3")
    plan = {
        "production_plan_id": "production-run-1",
        "asset_requests": [
            {
                "asset_request_id": "asset-request-run-1-1",
                "script_unit_id": "unit-1",
                "type": "visual",
                "claim_refs": ["kc-1"],
                "evidence_refs": ["ke-1"],
                "acceptance_criteria": ["preserve provenance"],
            }
        ],
    }

    first = store.create_from_plan("run-1", plan)
    second = store.create_from_plan("run-1", plan)

    assert [job.job_id for job in first] == ["job-run-1-asset-request-run-1-1"]
    assert [job.job_id for job in second] == [first[0].job_id]
    assert first[0].status == "QUEUED"
    assert first[0].claim_refs == ("kc-1",)

    running = store.mark_running(first[0].job_id)
    completed = store.complete(
        running.job_id,
        {"asset_id": "asset-1", "kind": "visual", "uri": "file://asset-1.png"},
    )

    assert completed.status == "COMPLETED"
    assert completed.result["asset_id"] == "asset-1"
    assert [job.job_id for job in store.list_for_run("run-1")] == [first[0].job_id]

    store.close()
