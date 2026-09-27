import os
from pathlib import Path
import wave

import pytest

from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace


class DummyHandler(ProductHandler):
    def __init__(self, path, body):
        self.path = path
        self.body = body
        self.status = None
        self.response = None
        self.response_headers = {}
        self.content_runs = None
        self.service = None
        self.workspace = None
        self.content_run_planner = None

    def _protect_product_api(self):
        return True

    def _body(self):
        return self.body

    def _json(self, status, body, retry_after=None):
        self.status = status
        self.response = body


@pytest.mark.external
def test_factory_full_lifecycle_to_real_whisper_studio_video(tmp_path, monkeypatch):
    whisper_root = os.environ.get("WHISPER_STUDIO_ROOT")
    whisper_python = os.environ.get("WHISPER_STUDIO_PYTHON")
    whisper_script = os.environ.get("WHISPER_STUDIO_SCRIPT", "one_command.py")

    if not whisper_root:
        pytest.skip("WHISPER_STUDIO_ROOT is not configured")
    if not whisper_python:
        pytest.skip("WHISPER_STUDIO_PYTHON is not configured")

    monkeypatch.setenv("FACTORY_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FACTORY_PROVIDER", "local")
    monkeypatch.setenv("FACTORY_RENDERER", "whisper_studio")
    monkeypatch.setenv("FACTORY_ASSET_PROVIDER", "local_media")
    monkeypatch.setenv("WHISPER_STUDIO_ROOT", whisper_root)
    monkeypatch.setenv("WHISPER_STUDIO_PYTHON", whisper_python)
    monkeypatch.setenv("WHISPER_STUDIO_SCRIPT", whisper_script)
    monkeypatch.setenv("WHISPER_STUDIO_RESOLUTION", "1080x1920")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    service = FactoryService()
    workspace = ContentWorkspace(service)
    try:
        run = service.content_runs.create(
            title="Full factory renderer proof",
            brief="Explain a factual topic with evidence in a short vertical video.",
            audience="general",
            goal="short video",
            formats=("short_video",),
            constraints=(),
        )

        first = DummyHandler(f"/api/runs/{run.run_id}/factory", {})
        first.content_runs = service.content_runs
        first.service = service
        first.workspace = workspace
        ProductHandler.do_POST(first)

        assert first.status == 409, first.response
        candidates = first.response["candidates"]
        assert candidates

        claim_id = candidates[0]["claim_id"]
        service.knowledge.promote_claim(claim_id, decision_ref="E2E-KNOWLEDGE-REVIEW")

        factory = DummyHandler(f"/api/runs/{run.run_id}/factory", {})
        factory.content_runs = service.content_runs
        factory.service = service
        factory.workspace = workspace
        ProductHandler.do_POST(factory)

        assert factory.status == 200, factory.response
        assert factory.response["qc"]["status"] == "PASSED"
        assert factory.response["run"]["status"] == "REVIEW"

        result = factory.response["run"]["result"]
        assert len(result["script"]["units"]) >= 4
        assert result["production"]["assets"]
        assert result["production"]["output"]["sequence"]

        assets = result["production"]["assets"]
        assert len(assets) >= len(result["script"]["units"]) * 2
        for asset in assets:
            asset_path = Path(asset["uri"])
            assert asset_path.is_file(), asset
            assert asset["claim_refs"]
            assert asset["evidence_refs"]
            if asset["asset_type"] == "voice":
                with wave.open(str(asset_path), "rb") as handle:
                    assert handle.getnchannels() == 1
                    assert handle.getnframes() > 0

        approve = DummyHandler(
            f"/api/runs/{run.run_id}/approve",
            {"decision_ref": "E2E-HUMAN-APPROVAL"},
        )
        approve.content_runs = service.content_runs
        approve.service = service
        approve.workspace = workspace
        ProductHandler.do_POST(approve)

        assert approve.status == 200, approve.response
        assert approve.response["status"] == "APPROVED"

        export = DummyHandler(f"/api/runs/{run.run_id}/export", {})
        export.content_runs = service.content_runs
        export.service = service
        export.workspace = workspace
        ProductHandler.do_POST(export)

        assert export.status == 200, export.response
        payload = export.response["export"]
        assert payload["renderer"] == "whisper-studio"
        assert payload["artifact_type"] == "video"
        assert payload["status"] == "EXPORTED"

        artifact = Path(tmp_path) / "exports" / run.run_id / payload["artifact"]
        manifest = Path(tmp_path) / "exports" / run.run_id / "manifest.json"
        source_video = Path(payload["source_video"])

        assert artifact.is_file()
        assert artifact.suffix.lower() == ".mp4"
        assert artifact.stat().st_size > 0
        assert source_video.is_file()
        assert source_video.suffix.lower() == ".mp4"
        assert manifest.is_file()

        stored = service.content_runs.get(run.run_id)
        assert stored is not None
        assert stored.status == "EXPORTED"
        assert stored.result["export"]["artifact_type"] == "video"
    finally:
        service.close()
