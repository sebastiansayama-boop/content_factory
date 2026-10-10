from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class AssetGenerationError(RuntimeError):
    """Expected failure while generating a real media asset."""


@dataclass(frozen=True)
class GeneratedAsset:
    path: Path
    sha256: str
    size_bytes: int
    provider: str
    model: str
    request_id: str | None


@dataclass(frozen=True)
class AssetGenerationConfig:
    api_key_env: str = "OPENAI_API_KEY"
    image_model: str = "gpt-image-2"
    image_endpoint: str = "https://api.openai.com/v1/images/generations"
    image_size: str = "1024x1536"
    image_quality: str = "medium"
    speech_model: str = "gpt-4o-mini-tts"
    speech_endpoint: str = "https://api.openai.com/v1/audio/speech"
    speech_voice: str = "alloy"
    speech_speed: float = 1.0


class OpenAIAssetGenerator:
    """Generate real PNG/WAV assets through OpenAI's media endpoints."""

    def __init__(self, config: AssetGenerationConfig | None = None) -> None:
        self.config = config or AssetGenerationConfig()
        self.api_key = os.getenv(self.config.api_key_env)
        if not self.api_key:
            raise AssetGenerationError(
                f"missing integration secret: {self.config.api_key_env}"
            )

    def _request_json(self, endpoint: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=120) as response:
                raw = response.read().decode("utf-8")
                body = json.loads(raw)
                if not isinstance(body, dict):
                    raise AssetGenerationError("OpenAI media response must be an object")
                return body, response.headers.get("x-request-id")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise AssetGenerationError(
                f"OpenAI media HTTP error {exc.code}: {detail[:1000]}"
            ) from exc
        except URLError as exc:
            raise AssetGenerationError(
                f"OpenAI media connectivity error: {exc.reason}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise AssetGenerationError("OpenAI media response was not valid JSON") from exc

    def _request_binary(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> tuple[bytes, str | None]:
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "audio/wav",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=120) as response:
                return response.read(), response.headers.get("x-request-id")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise AssetGenerationError(
                f"OpenAI speech HTTP error {exc.code}: {detail[:1000]}"
            ) from exc
        except URLError as exc:
            raise AssetGenerationError(
                f"OpenAI speech connectivity error: {exc.reason}"
            ) from exc

    @staticmethod
    def _write_asset(path: Path, data: bytes) -> GeneratedAsset:
        if not data:
            raise AssetGenerationError(f"provider returned empty asset: {path.name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        return GeneratedAsset(
            path=path,
            sha256=digest,
            size_bytes=len(data),
            provider="openai",
            model="",
            request_id=None,
        )

    def generate_image(self, prompt: str, output_path: Path) -> GeneratedAsset:
        if not prompt.strip():
            raise ValueError("image prompt must not be empty")
        body, request_id = self._request_json(
            self.config.image_endpoint,
            {
                "model": self.config.image_model,
                "prompt": prompt,
                "size": self.config.image_size,
                "quality": self.config.image_quality,
                "output_format": "png",
            },
        )
        data = body.get("data")
        if not isinstance(data, list) or not data or not isinstance(data[0], dict):
            raise AssetGenerationError("OpenAI image response contains no image data")
        encoded = data[0].get("b64_json")
        if not isinstance(encoded, str) or not encoded:
            raise AssetGenerationError("OpenAI image response contains no b64_json")
        try:
            raw = base64.b64decode(encoded, validate=True)
        except ValueError as exc:
            raise AssetGenerationError("OpenAI image b64_json is invalid") from exc
        asset = self._write_asset(output_path, raw)
        return GeneratedAsset(
            **{**asset.__dict__, "model": self.config.image_model, "request_id": request_id}
        )

    def generate_speech(
        self,
        text: str,
        output_path: Path,
        language: str = "ru",
    ) -> GeneratedAsset:
        if not text.strip():
            raise ValueError("speech text must not be empty")
        raw, request_id = self._request_binary(
            self.config.speech_endpoint,
            {
                "model": self.config.speech_model,
                "voice": self.config.speech_voice,
                "input": text,
                "response_format": "wav",
                "speed": self.config.speech_speed,
                "instructions": f"Speak naturally in {language}. Clear short-form narration. No music or sound effects.",
            },
        )
        asset = self._write_asset(output_path, raw)
        return GeneratedAsset(
            **{**asset.__dict__, "model": self.config.speech_model, "request_id": request_id}
        )


def materialize_shot_pack_assets(
    pack: dict[str, Any],
    output_dir: Path,
    generator: OpenAIAssetGenerator | None = None,
) -> dict[str, Any]:
    """Generate every declared PNG/WAV asset and return a manifest-ready record.

    This function never creates demo fixtures. A provider failure aborts the pack
    instead of producing a synthetic replacement asset.
    """
    shots = pack.get("shots")
    if not isinstance(shots, list) or not shots:
        raise ValueError("pack must contain shots")
    provider = generator or OpenAIAssetGenerator()
    generated: list[dict[str, Any]] = []

    for shot in shots:
        if not isinstance(shot, dict):
            raise ValueError("every shot must be an object")
        image_path = output_dir / str(shot["image_file"])
        voice_path = output_dir / str(shot["voice_file"])
        image = provider.generate_image(
            str(shot["image_prompt"]),
            image_path,
        )
        voice = provider.generate_speech(
            str(shot["narration"]),
            voice_path,
            language=str(pack.get("language", "ru")),
        )
        generated.extend(
            [
                {
                    "shot_id": shot["shot_id"],
                    "kind": "image",
                    "path": str(image.path),
                    "sha256": image.sha256,
                    "size_bytes": image.size_bytes,
                    "provider": image.provider,
                    "model": image.model,
                    "request_id": image.request_id,
                },
                {
                    "shot_id": shot["shot_id"],
                    "kind": "speech",
                    "path": str(voice.path),
                    "sha256": voice.sha256,
                    "size_bytes": voice.size_bytes,
                    "provider": voice.provider,
                    "model": voice.model,
                    "request_id": voice.request_id,
                },
            ]
        )

    return {"assets": generated, "asset_count": len(generated)}
