from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

from content_factory.asset_generator import (
    AssetGenerationError,
    AssetGenerationConfig,
    OpenAIAssetGenerator,
    materialize_shot_pack_assets,
)


class FakeHeaders:
    def get(self, name: str):
        return "req_test_media_001" if name == "x-request-id" else None


class FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload
        self.headers = FakeHeaders()
        self.status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def test_generate_image_writes_real_provider_bytes(monkeypatch, tmp_path: Path) -> None:
    image_bytes = b"PNG-provider-bytes"
    payload = json.dumps({"data": [{"b64_json": base64.b64encode(image_bytes).decode()}]}).encode()
    monkeypatch.setattr("content_factory.asset_generator.urlopen", lambda *args, **kwargs: FakeResponse(payload))
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    generator = OpenAIAssetGenerator()
    asset = generator.generate_image("A concrete scene", tmp_path / "scene_01.png")

    assert asset.path.read_bytes() == image_bytes
    assert asset.model == "gpt-image-2"
    assert asset.request_id == "req_test_media_001"


def test_generate_speech_writes_wav_bytes(monkeypatch, tmp_path: Path) -> None:
    wav_bytes = b"RIFF-provider-wav"
    monkeypatch.setattr("content_factory.asset_generator.urlopen", lambda *args, **kwargs: FakeResponse(wav_bytes))
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    generator = OpenAIAssetGenerator()
    asset = generator.generate_speech("Привет", tmp_path / "voice_01.wav")

    assert asset.path.read_bytes() == wav_bytes
    assert asset.model == "gpt-4o-mini-tts"
    assert asset.request_id == "req_test_media_001"


def test_missing_key_fails_closed(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(AssetGenerationError, match="missing integration secret"):
        OpenAIAssetGenerator()


def test_pack_generation_does_not_fabricate_missing_assets(monkeypatch, tmp_path: Path) -> None:
    class FailingGenerator:
        def generate_image(self, prompt, output_path):
            raise AssetGenerationError("provider failed")

        def generate_speech(self, text, output_path, language="ru"):
            raise AssertionError("speech must not run after image failure")

    pack = {
        "language": "ru",
        "shots": [
            {
                "shot_id": "shot_01",
                "image_prompt": "A real scene",
                "narration": "Реальная речь",
                "image_file": "scene_01.png",
                "voice_file": "voice_01.wav",
            }
        ],
    }

    with pytest.raises(AssetGenerationError, match="provider failed"):
        materialize_shot_pack_assets(pack, tmp_path, generator=FailingGenerator())
    assert not (tmp_path / "scene_01.png").exists()
    assert not (tmp_path / "voice_01.wav").exists()
