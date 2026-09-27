from content_factory.asset_jobs import AssetJobStore
from content_factory.asset_registry import AssetRegistry
from content_factory.asset_executor import AssetExecutor
from content_factory.assembly import ContentAssembler, QualityGate


def test_completed_jobs_become_registered_assets_and_assemble(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_ASSET_PROVIDER", "stub")
    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    registry = AssetRegistry(tmp_path / "assets.sqlite3")
    plan = {
        "production_plan_id": "production-run-1",
        "format": "short_video",
        "asset_requests": [
            {
                "asset_request_id": "request-1",
                "script_unit_id": "unit-1",
                "type": "visual",
                "claim_refs": ["kc-1"],
                "evidence_refs": ["ke-1"],
                "acceptance_criteria": ["preserve provenance"],
            }
        ],
    }
    jobs.create_from_plan("run-1", plan)
    completed = AssetExecutor(jobs, tmp_path).execute_run("run-1")
    asset = registry.register_completed_job(completed[0])

    output = ContentAssembler(registry, tmp_path).assemble(
        run_id="run-1",
        script={
            "script_id": "script-1",
            "title": "Test",
            "units": [
                {
                    "unit_id": "unit-1",
                    "kind": "hook",
                    "text": "Hello",
                    "visual_intent": "A visual",
                }
            ],
        },
        production_plan=plan,
    )

    assert asset.asset_id.startswith("asset-")
    assert output["status"] == "ASSEMBLED"
    assert output["sequence"][0]["asset_id"] == asset.asset_id
    assert output["sequence"][0]["claim_refs"] == ["kc-1"]

    qc = QualityGate().evaluate(
        run_id="run-1",
        script={"units": [{"unit_id": "unit-1"}]},
        production_plan=plan,
        assets=[asset],
        output=output,
    )
    assert qc["passed"] is True
    assert qc["status"] == "PASSED"

    jobs.close()
    registry.close()


def test_qc_rejects_missing_provenance(tmp_path):
    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    registry = AssetRegistry(tmp_path / "assets.sqlite3")
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
    job = jobs.complete(
        job.job_id,
        {
            "asset_id": "asset-1",
            "provider": "test",
            "uri": "file://asset-1",
        },
    )
    asset = registry.register_completed_job(job)

    qc = QualityGate().evaluate(
        run_id="run-1",
        script={"units": [{"unit_id": "unit-1"}]},
        production_plan=plan,
        assets=[
            asset.__class__(
                **{
                    **asset.__dict__,
                    "claim_refs": (),
                    "evidence_refs": (),
                }
            )
        ],
        output={"output_id": "output-run-1", "uri": "file://sequence.json"},
    )
    assert qc["passed"] is False
    assert any(not check["passed"] for check in qc["checks"] if check["check"].startswith("provenance_"))

    jobs.close()
    registry.close()
