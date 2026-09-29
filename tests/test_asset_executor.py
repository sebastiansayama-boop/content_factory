import io
import json
import os
from pathlib import Path
import wave

import pytest
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


def test_local_media_executor_persists_provider_metadata_for_visual(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_ASSET_PROVIDER", "local_media")
    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    plan = {"asset_requests": [
        {"asset_request_id": "visual-provider", "script_unit_id": "unit-1", "type": "visual",
         "claim_refs": ["kc-1"], "evidence_refs": ["ke-1"],
         "acceptance_criteria": ["preserve provenance"], "text": "Provider metadata test.",
         "visual_intent": "A simple editorial image."},
    ]}
    jobs.create_from_plan("run-provider", plan)
    result = AssetExecutor(jobs, tmp_path).execute_run("run-provider")
    assert len(result) == 1
    assert result[0].status == "COMPLETED"
    assert result[0].result["provider"] == "local_media"
    assert Path(result[0].result["path"]).is_file()
    jobs.close()


@pytest.mark.skipif(os.name != "nt", reason="local_media voice requires Windows SAPI")
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


def test_openverse_executor_downloads_image_and_persists_license_metadata(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_ASSET_PROVIDER", "openverse")
    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    plan = {"asset_requests": [
        {
            "asset_request_id": "openverse-visual",
            "script_unit_id": "unit-1",
            "type": "visual",
            "claim_refs": ["kc-1"],
            "evidence_refs": ["ke-1"],
            "acceptance_criteria": ["preserve provenance"],
            "text": "Convergent evolution can produce similar functional traits.",
            "visual_intent": "A documentary photograph of birds in flight.",
        },
    ]}
    jobs.create_from_plan("run-openverse", plan)

    from PIL import Image

    image_buffer = io.BytesIO()
    Image.new("RGB", (512, 512), (80, 120, 160)).save(image_buffer, format="PNG")
    api_payload = json.dumps({
        "results": [{
            "id": "ov-image-1",
            "url": "https://images.example.test/bird.png",
            "foreign_landing_url": "https://commons.example.test/bird",
            "title": "Birds in flight",
            "creator": "Example Photographer",
            "license": "cc-by",
            "license_version": "4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "thumbnail": "https://images.example.test/bird-thumb.png",
        }]
    }).encode("utf-8")

    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def read(self, _limit=None):
            return self.payload

    responses = iter([FakeResponse(api_payload), FakeResponse(image_buffer.getvalue())])
    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: next(responses))

    result = AssetExecutor(jobs, tmp_path).execute_run("run-openverse")

    assert len(result) == 1
    assert result[0].status == "COMPLETED"
    assert result[0].result["provider"] == "openverse"
    path = Path(result[0].result["path"])
    assert path.is_file()
    assert path.suffix == ".png"
    metadata = result[0].result["metadata"]
    assert metadata["source"] == "openverse"
    assert metadata["license"] == "cc-by"
    assert metadata["foreign_landing_url"] == "https://commons.example.test/bird"
    assert metadata["license_verification_required"] is True

    jobs.close()


def test_pexels_executor_downloads_photo_and_persists_attribution_metadata(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_ASSET_PROVIDER", "pexels")
    monkeypatch.setenv("PEXELS_API_KEY", "test-key")
    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    jobs.create_from_plan("run-pexels-photo", {"asset_requests": [{
        "asset_request_id": "photo-1",
        "script_unit_id": "unit-1",
        "type": "visual",
        "claim_refs": ["kc-1"],
        "evidence_refs": ["ke-1"],
        "acceptance_criteria": ["preserve provenance"],
        "visual_intent": "documentary birds in flight",
    }]})

    payload = {
        "photos": [{
            "id": 123,
            "url": "https://www.pexels.com/photo/birds-123/",
            "photographer": "Example Photographer",
            "photographer_url": "https://www.pexels.com/@example",
            "alt": "Birds in flight",
            "width": 1200,
            "height": 1800,
            "src": {"original": "https://images.example.test/birds.jpg"},
        }]
    }

    class FakeResponse:
        def __init__(self, body): self.body = body
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False
        def read(self, _limit=None): return self.body

    calls = iter([
        FakeResponse(json.dumps(payload).encode()),
        FakeResponse(b"fake-jpeg-bytes"),
    ])
    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: next(calls))

    result = AssetExecutor(jobs, tmp_path).execute_run("run-pexels-photo")
    job = result[0]
    assert job.status == "COMPLETED"
    assert job.result["provider"] == "pexels"
    assert Path(job.result["path"]).suffix == ".jpg"
    assert Path(job.result["path"]).read_bytes() == b"fake-jpeg-bytes"
    assert job.result["metadata"]["attribution_text"] == "Photo by Example Photographer on Pexels"
    assert job.result["metadata"]["attribution_url"] == "https://www.pexels.com/photo/birds-123/"
    jobs.close()


def test_pexels_executor_downloads_video_and_persists_attribution_metadata(tmp_path, monkeypatch):
    monkeypatch.setenv("FACTORY_ASSET_PROVIDER", "pexels")
    monkeypatch.setenv("PEXELS_API_KEY", "test-key")
    jobs = AssetJobStore(tmp_path / "jobs.sqlite3")
    jobs.create_from_plan("run-pexels-video", {"asset_requests": [{
        "asset_request_id": "video-1",
        "script_unit_id": "unit-1",
        "type": "video",
        "claim_refs": ["kc-1"],
        "evidence_refs": ["ke-1"],
        "acceptance_criteria": ["preserve provenance"],
        "visual_intent": "birds flying over a forest",
    }]})

    payload = {
        "videos": [{
            "id": 456,
            "url": "https://www.pexels.com/video/birds-456/",
            "user": {
                "name": "Example Videographer",
                "url": "https://www.pexels.com/@videographer",
            },
            "video_files": [
                {
                    "link": "https://videos.example.test/birds.mp4",
                    "file_type": "video/mp4",
                    "width": 1080,
                    "height": 1920,
                }
            ],
        }]
    }

    class FakeResponse:
        def __init__(self, body): self.body = body
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False
        def read(self, _limit=None): return self.body

    calls = iter([
        FakeResponse(json.dumps(payload).encode()),
        FakeResponse(b"fake-mp4-bytes"),
    ])
    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: next(calls))

    result = AssetExecutor(jobs, tmp_path).execute_run("run-pexels-video")
    job = result[0]
    assert job.status == "COMPLETED"
    assert job.result["provider"] == "pexels"
    assert Path(job.result["path"]).suffix == ".mp4"
    assert Path(job.result["path"]).read_bytes() == b"fake-mp4-bytes"
    assert job.result["metadata"]["attribution_text"] == "Video by Example Videographer on Pexels"
    jobs.close()
