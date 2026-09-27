from pathlib import Path
import wave
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


def test_local_media_executor_materializes_authored_visual_and_voice(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_ASSET_PROVIDER", "local_media")
    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    plan = {"asset_requests": [
        {"asset_request_id": "visual-1", "script_unit_id": "unit-1", "type": "visual", "claim_refs": ["kc-1"], "evidence_refs": ["ke-1"], "acceptance_criteria": ["preserve provenance"], "text": "A real local narration.", "visual_intent": "A documentary scene about evidence."},
        {"asset_request_id": "voice-1", "script_unit_id": "unit-1", "type": "voice", "claim_refs": ["kc-1"], "evidence_refs": ["ke-1"], "acceptance_criteria": ["preserve provenance"], "text": "Narrate the evidence carefully."},
    ]}
    jobs.create_from_plan("run-local-media", plan)
    result = AssetExecutor(jobs, tmp_path).execute_run("run-local-media")
    assert {job.result["provider"] for job in result} == {"local_media"}
    visual = Path(result[0].result["path"])
    voice = Path(result[1].result["path"])
    assert visual.suffix == ".png" and visual.stat().st_size > 1000
    assert voice.suffix == ".wav" and voice.stat().st_size > 1000
    with wave.open(str(voice), "rb") as handle:
        assert handle.getnchannels() == 1
        assert handle.getframerate() > 0
        assert handle.getnframes() > 0
    jobs.close()
