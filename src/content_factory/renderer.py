from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class RenderError(ValueError):
    pass


@dataclass(frozen=True)
class RenderResult:
    renderer: str
    final_video: str
    manifest: str
    artifacts: dict[str, Any]


class Renderer(Protocol):
    def render(
        self,
        *,
        run_id: str,
        title: str,
        script: dict[str, Any],
        production: dict[str, Any],
    ) -> RenderResult: ...


class WhisperStudioRenderer:
    """Adapter for Whisper Studio's active local-pack renderer."""

    def __init__(
        self,
        *,
        root: str | Path,
        data_root: str | Path,
        python: str | None = None,
        script: str = "one_command.py",
    ) -> None:
        self.root = Path(root).resolve()
        self.data_root = Path(data_root).resolve()
        self.python = python or sys.executable
        self.script = self.root / script

    def render(
        self,
        *,
        run_id: str,
        title: str,
        script: dict[str, Any],
        production: dict[str, Any],
    ) -> RenderResult:
        units = script.get("units")
        output = production.get("output")
        if not isinstance(units, list) or not 4 <= len(units) <= 12:
            raise RenderError("Whisper Studio requires 4-12 script units")
        if not isinstance(output, dict):
            raise RenderError("assembled production output is required")
        sequence = output.get("sequence")
        if not isinstance(sequence, list) or len(sequence) != len(units):
            raise RenderError("assembled sequence does not match script units")
        if not self.script.is_file():
            raise RenderError(f"Whisper Studio entrypoint not found: {self.script}")

        pack_dir = self.data_root / "renderer_inputs" / run_id
        pack_dir.mkdir(parents=True, exist_ok=True)
        shots: list[dict[str, Any]] = []

        for index, (unit, item) in enumerate(zip(units, sequence), start=1):
            asset_uri = str(item.get("asset_uri") or "").strip()
            source = Path(asset_uri)
            if not source.is_file():
                raise RenderError(f"render asset does not exist: {asset_uri}")
            if source.suffix.lower() != ".png":
                raise RenderError("Whisper Studio currently requires PNG visual assets")

            voice_uri = str(item.get("voice_uri") or "").strip()
            if not voice_uri:
                raise RenderError("Whisper Studio requires voice_uri for every script unit")
            voice = Path(voice_uri)
            if not voice.is_file() or voice.suffix.lower() != ".wav":
                raise RenderError("Whisper Studio currently requires WAV voice assets")

            image_name = f"scene_{index:02d}.png"
            voice_name = f"voice_{index:02d}.wav"
            shutil.copy2(source, pack_dir / image_name)
            shutil.copy2(voice, pack_dir / voice_name)
            shots.append(
                {
                    "shot_id": f"shot_{index:02d}",
                    "narration": str(unit.get("text") or ""),
                    "visual_action": str(unit.get("visual_intent") or ""),
                    "composition": "Vertical 9:16 composition.",
                    "camera_motion": "static",
                    "mood": "controlled",
                    "image_prompt": str(unit.get("visual_intent") or ""),
                    "negative_prompt": "No logo, watermark or typography.",
                    "transition": "hard_cut",
                    "image_file": image_name,
                    "voice_file": voice_name,
                }
            )

        pack = {
            "title": title,
            "logline": str(output.get("format") or title),
            "style_bible": {
                "visual_style": "authored production assets",
                "palette": "preserve source assets",
                "lighting": "preserve source assets",
                "subject_continuity": "preserve source assets",
                "negative_constraints": "no new factual content",
            },
            "shots": shots,
        }
        pack_path = pack_dir / "pack.json"
        pack_path.write_text(
            json.dumps(pack, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        output_dir = self.data_root / "renderer_outputs" / run_id
        output_dir.mkdir(parents=True, exist_ok=True)
        command = [
            self.python,
            str(self.script),
            "--brief",
            title,
            "--language",
            "ru",
            "--duration",
            str(len(shots) * 2),
            "--shots",
            str(len(shots)),
            "--resolution",
            os.environ.get("WHISPER_STUDIO_RESOLUTION", "1080x1920"),
            "--local-pack",
            str(pack_path),
            "--output-dir",
            str(output_dir),
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=self.root,
                check=True,
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            detail = getattr(exc, "stderr", "") or getattr(exc, "stdout", "") or str(exc)
            raise RenderError(f"Whisper Studio render failed: {detail.strip()}") from exc

        manifests = sorted(
            output_dir.glob("*/manifest.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if not manifests:
            raise RenderError(
                "Whisper Studio completed without manifest. "
                f"Output: {completed.stdout[-1000:]}"
            )
        manifest_path = manifests[0]
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RenderError("Whisper Studio manifest is unreadable") from exc

        final_path = manifest_path.parent / str(
            manifest.get("final_video") or "render/final.mp4"
        )
        if not final_path.is_file():
            raise RenderError(
                f"Whisper Studio manifest points to missing final video: {final_path}"
            )

        media = self._probe_video(final_path)
        if not media["video"]:
            raise RenderError("Whisper Studio output contains no video stream")
        if not media["audio"]:
            raise RenderError("Whisper Studio output contains no audio stream")
        if media["duration"] <= 0:
            raise RenderError("Whisper Studio output has invalid duration")

        return RenderResult(
            renderer="whisper-studio",
            final_video=str(final_path),
            manifest=str(manifest_path),
            artifacts={
                **(manifest.get("artifacts", {}) if isinstance(manifest.get("artifacts", {}), dict) else {}),
                "media_probe": media,
            },
        )

    @staticmethod
    def _probe_video(path: Path) -> dict[str, Any]:
        command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ]
        try:
            completed = subprocess.run(
                command,
                check=True,
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            detail = getattr(exc, "stderr", "") or getattr(exc, "stdout", "") or str(exc)
            raise RenderError(f"ffprobe failed for rendered video: {detail.strip()}") from exc
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RenderError("ffprobe returned invalid JSON") from exc

        streams = payload.get("streams", [])
        stream_types = {
            str(stream.get("codec_type"))
            for stream in streams
            if isinstance(stream, dict)
        }
        try:
            duration = float(payload.get("format", {}).get("duration") or 0)
        except (TypeError, ValueError):
            duration = 0.0
        return {
            "video": "video" in stream_types,
            "audio": "audio" in stream_types,
            "duration": duration,
        }


class PackageRenderer:
    """Compatibility renderer for the pre-media package export path."""

    def render(
        self,
        *,
        run_id: str,
        title: str,
        script: dict[str, Any],
        production: dict[str, Any],
    ) -> RenderResult:
        output = production.get("output")
        if not isinstance(output, dict):
            raise RenderError("assembled production output is required")
        uri = str(output.get("uri") or "").strip()
        if not uri or not Path(uri).is_file():
            raise RenderError("assembled output file does not exist")
        return RenderResult(
            renderer="package",
            final_video=uri,
            manifest=uri,
            artifacts={},
        )


def build_renderer(data_root: str | Path) -> Renderer:
    name = os.environ.get("FACTORY_RENDERER", "package").strip().lower() or "package"
    if name == "package":
        return PackageRenderer()
    if name == "whisper_studio":
        root = os.environ.get("WHISPER_STUDIO_ROOT", "").strip()
        if not root:
            raise RenderError(
                "WHISPER_STUDIO_ROOT is required for FACTORY_RENDERER=whisper_studio"
            )
        return WhisperStudioRenderer(
            root=root,
            data_root=data_root,
            python=os.environ.get("WHISPER_STUDIO_PYTHON", "").strip() or None,
            script=os.environ.get("WHISPER_STUDIO_SCRIPT", "one_command.py").strip()
            or "one_command.py",
        )
    raise RenderError("FACTORY_RENDERER must be 'package' or 'whisper_studio'")
