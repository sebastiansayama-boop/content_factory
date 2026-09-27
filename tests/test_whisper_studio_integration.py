import os
from pathlib import Path
import pytest

from content_factory.asset_executor import AssetExecutor
from content_factory.asset_jobs import AssetJobStore
from content_factory.asset_registry import AssetRegistry
from content_factory.assembly import ContentAssembler
from content_factory.renderer import WhisperStudioRenderer


@pytest.mark.external
def test_whisper_studio_renderer_real_local_pack(tmp_path):
    root = os.environ.get("WHISPER_STUDIO_ROOT")
    if not root:
        pytest.skip("WHISPER_STUDIO_ROOT is not configured")

    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    registry = AssetRegistry(tmp_path / "assets.sqlite3")
    requests = []
    for index in range(4):
        requests.extend([
            {
                "asset_request_id": f"visual-{index}",
                "script_unit_id": f"unit-{index}",
                "type": "visual",
                "claim_refs": [f"kc-{index}"],
                "evidence_refs": [f"ke-{index}"],
                "acceptance_criteria": ["preserve provenance"],
            },
            {
                "asset_request_id": f"voice-{index}",
                "script_unit_id": f"unit-{index}",
                "type": "voice",
                "claim_refs": [f"kc-{index}"],
                "evidence_refs": [f"ke-{index}"],
                "acceptance_criteria": ["preserve provenance"],
            },
        ])
    jobs.create_from_plan("run-real", {"format": "short_video", "asset_requests": requests})
    completed = AssetExecutor(jobs, tmp_path).execute_run("run-real")
    assets = [registry.register_completed_job(job) for job in completed]
    script = {
        "script_id": "script-real",
        "title": "Renderer integration fixture",
        "units": [
            {"unit_id": f"unit-{i}", "kind": "narration", "text": f"Line {i}", "visual_intent": f"Visual {i}"}
            for i in range(4)
        ],
    }
    plan = {"format": "short_video", "asset_requests": requests}
    output = ContentAssembler(registry, tmp_path).assemble(
        run_id="run-real", script=script, production_plan=plan
    )
    result = WhisperStudioRenderer(root=root, data_root=tmp_path).render(
        run_id="run-real", title="Renderer integration fixture",
        script=script, production={"output": output},
    )
    assert Path(result.final_video).is_file()
    assert Path(result.final_video).suffix.lower() == ".mp4"
    assert Path(result.manifest).is_file()
    jobs.close()
    registry.close()
