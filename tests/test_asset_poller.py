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


def test_higgsfield_poller_uses_current_status_endpoint(tmp_path, monkeypatch):
    import json

    class FakeResponse:
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return json.dumps({
                "status": "completed",
                "output": {"images": [{"url": "https://cdn.example/image.png"}]},
            }).encode("utf-8")

    seen = []

    def fake_urlopen(request, timeout=30):
        seen.append((request.full_url, request.method, dict(request.header_items())))
        return FakeResponse()

    monkeypatch.setattr("content_factory.asset_poller.urllib.request.urlopen", fake_urlopen)
    monkeypatch.setenv("HF_KEY", "test-key")
    monkeypatch.delenv("HF_STATUS_URL", raising=False)

    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    jobs.create_from_plan(
        "run-1",
        {
            "asset_requests": [{
                "asset_request_id": "request-1",
                "script_unit_id": "unit-1",
                "type": "visual",
                "claim_refs": ["kc-1"],
                "evidence_refs": ["ke-1"],
                "acceptance_criteria": ["preserve provenance"],
            }]
        },
    )
    job = jobs.mark_running("job-run-1-request-1")
    jobs.submit(job.job_id, {
        "provider": "higgsfield",
        "provider_request_id": "req-1",
        "asset_id": "asset-1",
    })

    result = AssetJobPoller(jobs).poll_run("run-1")

    assert result[0].status == "COMPLETED"
    assert seen[0][0] == "https://api.higgsfield.ai/requests/req-1/status"
    assert result[0].result["provider_status"] == "COMPLETED"
    jobs.close()
