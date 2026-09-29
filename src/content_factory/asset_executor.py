from __future__ import annotations

import hashlib
import json
import os
import struct
import wave
import zlib
import urllib.request
import urllib.parse
import subprocess
import textwrap
from io import BytesIO
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .asset_jobs import AssetJob, AssetJobStore


class AssetExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class AssetExecution:
    provider: str
    state: str
    result: dict[str, object]


class AssetExecutor:
    """Execute queued asset jobs through an explicit provider boundary.

    The default provider is a deterministic stub so the production graph can be
    exercised without paid external calls. External providers are opt-in.
    """

    def __init__(self, jobs: AssetJobStore, root: str | Path) -> None:
        self.jobs = jobs
        self.root = Path(root)

    def execute_run(self, run_id: str) -> list[AssetJob]:
        jobs = self.jobs.list_for_run(run_id)
        if not jobs:
            raise AssetExecutionError("no asset jobs found for run")
        output: list[AssetJob] = []
        for job in jobs:
            if job.status == "COMPLETED":
                output.append(job)
                continue
            if job.status not in {"QUEUED", "FAILED"}:
                output.append(job)
                continue
            running = self.jobs.mark_running(job.job_id)
            try:
                execution = self._execute(running)
                result = dict(execution.result)
                result.setdefault("provider", execution.provider)
                if execution.state == "SUBMITTED":
                    output.append(self.jobs.submit(job.job_id, result))
                else:
                    output.append(self.jobs.complete(job.job_id, result))
            except Exception as exc:
                output.append(self.jobs.fail(job.job_id, {"error": str(exc)}))
        return output

    def _execute(self, job: AssetJob) -> AssetExecution:
        provider = os.environ.get("FACTORY_ASSET_PROVIDER", "stub").strip().lower() or "stub"
        if provider == "stub":
            digest = hashlib.sha256(
                f"{job.run_id}:{job.asset_request_id}:{','.join(job.claim_refs)}".encode()
            ).hexdigest()[:16]
            directory = self.root / "asset_jobs" / job.run_id
            directory.mkdir(parents=True, exist_ok=True)
            extension = ".png" if job.asset_type == "visual" else ".wav" if job.asset_type == "voice" else ".json"
            path = directory / f"{job.asset_request_id}{extension}"
            if job.asset_type == "visual":
                self._write_stub_png(path, f"{job.run_id}:{job.asset_request_id}")
            elif job.asset_type == "voice":
                self._write_stub_voice(path, f"{job.run_id}:{job.asset_request_id}")
            else:
                path.write_text(
                    json.dumps(
                        {
                            "asset_id": f"asset-{digest}",
                            "job_id": job.job_id,
                            "type": job.asset_type,
                            "status": "DRAFT",
                            "claim_refs": list(job.claim_refs),
                            "evidence_refs": list(job.evidence_refs),
                            "acceptance_criteria": list(job.acceptance_criteria),
                            "provider": "stub",
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
            return AssetExecution(
                provider="stub",
                state="COMPLETED",
                result={
                    "asset_id": f"asset-{digest}",
                    "job_id": job.job_id,
                    "type": job.asset_type,
                    "status": "DRAFT",
                    "claim_refs": list(job.claim_refs),
                    "evidence_refs": list(job.evidence_refs),
                    "acceptance_criteria": list(job.acceptance_criteria),
                    "provider": "stub",
                    "path": str(path),
                },
            )
        if provider == "local_media":
            return self._execute_local_media(job)
        if provider == "openverse":
            return self._execute_openverse(job)
        if provider == "pexels":
            return self._execute_pexels(job)
        if provider == "higgsfield":
            return self._submit_higgsfield(job)
        raise AssetExecutionError(
            "FACTORY_ASSET_PROVIDER must be 'stub', 'local_media', 'openverse', 'pexels' or 'higgsfield'"
        )

    def _execute_local_media(self, job: AssetJob) -> AssetExecution:
        """Create useful local media without cloud credentials."""
        digest = hashlib.sha256(f"{job.run_id}:{job.asset_request_id}:{job.script_unit_id}".encode()).hexdigest()[:16]
        directory = self.root / "asset_jobs" / job.run_id
        directory.mkdir(parents=True, exist_ok=True)
        if job.asset_type == "visual":
            path = directory / f"{job.asset_request_id}.png"
            self._write_editorial_visual(path, job)
        elif job.asset_type == "voice":
            path = directory / f"{job.asset_request_id}.wav"
            self._write_sapi_voice(path, job)
        else:
            raise AssetExecutionError("local_media supports visual and voice assets only")
        return AssetExecution(provider="local_media", state="COMPLETED", result={"asset_id": f"asset-{digest}", "job_id": job.job_id, "type": job.asset_type, "status": "DRAFT", "claim_refs": list(job.claim_refs), "evidence_refs": list(job.evidence_refs), "acceptance_criteria": list(job.acceptance_criteria), "provider": "local_media", "path": str(path)})

    def _execute_openverse(self, job: AssetJob) -> AssetExecution:
        """Acquire an openly licensed image from Openverse without credentials."""
        if job.asset_type != "visual":
            raise AssetExecutionError("openverse provider currently supports visual jobs only")

        query = (job.visual_intent or job.input_text).strip()
        if not query:
            raise AssetExecutionError("openverse visual job requires visual_intent or input_text")

        from PIL import Image

        params = urllib.parse.urlencode(
            {
                "q": query[:300],
                "page_size": "10",
            }
        )
        api_url = f"https://api.openverse.org/v1/images/?{params}"
        request = urllib.request.Request(
            api_url,
            headers={"User-Agent": "ContentFactory/1.0 (+https://github.com/sebastiansayama-boop/content_factory)"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise AssetExecutionError(f"openverse search failed: {exc}") from exc

        results = payload.get("results") if isinstance(payload, dict) else None
        if not isinstance(results, list):
            raise AssetExecutionError("openverse returned an invalid results payload")

        selected = None
        for candidate in results:
            if not isinstance(candidate, dict):
                continue
            source_url = str(candidate.get("url") or "").strip()
            if source_url.startswith(("https://", "http://")):
                selected = candidate
                break
        if selected is None:
            raise AssetExecutionError("openverse returned no downloadable image")

        source_url = str(selected.get("url") or "").strip()
        try:
            image_request = urllib.request.Request(
                source_url,
                headers={
                    "User-Agent": "ContentFactory/1.0 (+https://github.com/sebastiansayama-boop/content_factory)",
                },
                method="GET",
            )
            with urllib.request.urlopen(image_request, timeout=20) as response:
                raw = response.read(12 * 1024 * 1024 + 1)
        except Exception as exc:
            raise AssetExecutionError(f"openverse image download failed: {exc}") from exc

        if len(raw) > 12 * 1024 * 1024:
            raise AssetExecutionError("openverse image exceeds 12 MiB limit")

        try:
            image = Image.open(BytesIO(raw))
            image.load()
            width, height = image.size
            if width < 256 or height < 256:
                raise AssetExecutionError("openverse image is too small")
            image = image.convert("RGB")
        except AssetExecutionError:
            raise
        except Exception as exc:
            raise AssetExecutionError(f"openverse returned invalid image data: {exc}") from exc

        source_id = str(selected.get("id") or selected.get("foreign_landing_url") or source_url)
        digest = hashlib.sha256(
            f"{job.run_id}:{job.asset_request_id}:{source_id}".encode("utf-8")
        ).hexdigest()[:16]
        directory = self.root / "asset_jobs" / job.run_id
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{job.asset_request_id}.png"
        image.save(path, format="PNG")

        metadata = {
            "source": "openverse",
            "source_id": source_id,
            "source_url": source_url,
            "foreign_landing_url": str(selected.get("foreign_landing_url") or ""),
            "title": str(selected.get("title") or ""),
            "creator": str(selected.get("creator") or ""),
            "license": str(selected.get("license") or ""),
            "license_version": str(selected.get("license_version") or ""),
            "license_url": str(selected.get("license_url") or ""),
            "thumbnail": str(selected.get("thumbnail") or ""),
            "width": width,
            "height": height,
            "query": query,
            "license_verification_required": True,
        }
        return AssetExecution(
            provider="openverse",
            state="COMPLETED",
            result={
                "asset_id": f"asset-{digest}",
                "job_id": job.job_id,
                "type": job.asset_type,
                "status": "DRAFT",
                "claim_refs": list(job.claim_refs),
                "evidence_refs": list(job.evidence_refs),
                "acceptance_criteria": list(job.acceptance_criteria),
                "provider": "openverse",
                "path": str(path),
                "metadata": metadata,
            },
        )

    @staticmethod
    def _write_editorial_visual(path: Path, job: AssetJob) -> None:
        from PIL import Image, ImageDraw, ImageFont
        width, height = 1080, 1920
        digest = hashlib.sha256(f"{job.run_id}:{job.asset_request_id}".encode()).digest()
        base = (18 + digest[0] % 18, 22 + digest[1] % 18, 30 + digest[2] % 18)
        accent = (80 + digest[3] % 80, 110 + digest[4] % 80, 150 + digest[5] % 70)
        image = Image.new("RGB", (width, height), base)
        draw = ImageDraw.Draw(image)
        for y in range(height):
            ratio = y / (height - 1)
            color = tuple(int(base[i] * (1 - ratio) + accent[i] * ratio) for i in range(3))
            draw.line((0, y, width, y), fill=color)
        draw.ellipse((700, 180, 1260, 740), fill=accent)
        draw.rectangle((70, 1450, 1010, 1510), fill=(235, 235, 235))
        font_path = Path("C:/Windows/Fonts/arial.ttf")
        font = ImageFont.truetype(str(font_path), 62) if font_path.is_file() else ImageFont.load_default()
        small = ImageFont.truetype(str(font_path), 38) if font_path.is_file() else ImageFont.load_default()
        scene = job.script_unit_id.replace("unit-", "") or "1"
        draw.text((70, 180), f"SCENE {scene}", font=font, fill=(250, 250, 250))
        caption = job.visual_intent or job.input_text or "evidence-grounded production"
        lines = textwrap.wrap(caption, width=32)
        y = 1580
        for line in lines[:4]:
            draw.text((70, y), line, font=small, fill=(245, 245, 245))
            y += 52
        image.save(path, format="PNG")

    @staticmethod
    def _write_sapi_voice(path: Path, job: AssetJob) -> None:
        if os.name != "nt":
            raise AssetExecutionError("local_media voice requires Windows SAPI")
        text_value = job.input_text or (
            f"Scene {job.script_unit_id.replace('unit-', '')}. Evidence-grounded narration. "
            "The story stays within the supplied evidence and its stated limits."
        )
        escaped = text_value.replace("'", "''")
        target = str(path.resolve()).replace("'", "''")
        script = textwrap.dedent(f"""
            Add-Type -AssemblyName System.Speech
            $s = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $s.SetOutputToWaveFile('{target}')
            $s.Speak('{escaped}')
            $s.Dispose()
        """).strip()
        completed = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if completed.returncode != 0 or not path.is_file() or path.stat().st_size == 0:
            detail = (completed.stderr or completed.stdout or "unknown SAPI error").strip()
            raise AssetExecutionError(f"Windows SAPI voice generation failed: {detail}")

    @staticmethod
    def _write_stub_png(path: Path, seed: str) -> None:
        width, height = 720, 1280
        digest = hashlib.sha256(seed.encode()).digest()
        pixel = bytes((digest[0], digest[1], digest[2]))
        raw = b"".join(b"\x00" + pixel * width for _ in range(height))

        def chunk(kind: bytes, data: bytes) -> bytes:
            return (
                struct.pack(">I", len(data))
                + kind
                + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            )

        png = (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b"")
        )
        path.write_bytes(png)

    @staticmethod
    def _write_stub_voice(path: Path, seed: str) -> None:
        digest = hashlib.sha256(seed.encode()).digest()
        frequency = 180 + digest[0]
        sample_rate = 48_000
        duration = 1.5
        frames = int(sample_rate * duration)
        amplitude = 2600
        import math

        with wave.open(str(path), "wb") as handle:
            handle.setnchannels(1)
            handle.setsampwidth(2)
            handle.setframerate(sample_rate)
            samples = bytearray()
            for index in range(frames):
                value = int(amplitude * math.sin(2 * math.pi * frequency * index / sample_rate))
                samples.extend(struct.pack("<h", value))
            handle.writeframes(samples)

    def _execute_pexels(self, job: AssetJob) -> AssetExecution:
        """Acquire a Pexels photo or video using the free API."""
        key = os.environ.get("PEXELS_API_KEY", "").strip()
        if not key:
            raise AssetExecutionError("PEXELS_API_KEY is required for FACTORY_ASSET_PROVIDER=pexels")

        query = (job.visual_intent or job.input_text).strip()
        if not query:
            raise AssetExecutionError("pexels media job requires visual_intent or input_text")

        if job.asset_type == "visual":
            endpoint = "https://api.pexels.com/v1/search"
            params = urllib.parse.urlencode(
                {
                    "query": query[:300],
                    "orientation": "portrait",
                    "per_page": "15",
                    "locale": "en-US",
                }
            )
            payload = self._pexels_get_json(f"{endpoint}?{params}", key)
            candidates = payload.get("photos") if isinstance(payload, dict) else None
            if not isinstance(candidates, list):
                raise AssetExecutionError("pexels returned an invalid photo search payload")

            selected = next(
                (
                    item for item in candidates
                    if isinstance(item, dict)
                    and isinstance(item.get("src"), dict)
                    and str(item["src"].get("original") or "").startswith(("https://", "http://"))
                ),
                None,
            )
            if selected is None:
                raise AssetExecutionError("pexels returned no downloadable photo")

            source_url = str(selected["src"].get("original") or "")
            media_kind = "photo"
            attribution_url = str(selected.get("url") or "")
            creator = str(selected.get("photographer") or "")
            creator_url = str(selected.get("photographer_url") or "")
            title = str(selected.get("alt") or "")
            width = int(selected.get("width") or 0)
            height = int(selected.get("height") or 0)
            source_id = str(selected.get("id") or source_url)
            extension = ".jpg"
        elif job.asset_type == "video":
            endpoint = "https://api.pexels.com/v1/videos/search"
            params = urllib.parse.urlencode(
                {
                    "query": query[:300],
                    "orientation": "portrait",
                    "per_page": "15",
                    "locale": "en-US",
                }
            )
            payload = self._pexels_get_json(f"{endpoint}?{params}", key)
            candidates = payload.get("videos") if isinstance(payload, dict) else None
            if not isinstance(candidates, list):
                raise AssetExecutionError("pexels returned an invalid video search payload")

            selected = None
            selected_file = None
            for item in candidates:
                if not isinstance(item, dict):
                    continue
                files = item.get("video_files")
                if not isinstance(files, list):
                    continue
                usable = [
                    f for f in files
                    if isinstance(f, dict)
                    and str(f.get("link") or "").startswith(("https://", "http://"))
                    and str(f.get("file_type") or "").lower() in {"video/mp4", "video/quicktime"}
                ]
                usable.sort(key=lambda f: (int(f.get("width") or 0), int(f.get("height") or 0)), reverse=True)
                if usable:
                    selected = item
                    selected_file = usable[0]
                    break

            if selected is None or selected_file is None:
                raise AssetExecutionError("pexels returned no downloadable video")

            source_url = str(selected_file.get("link") or "")
            media_kind = "video"
            attribution_url = str(selected.get("url") or "")
            creator = str(selected.get("user", {}).get("name") or "") if isinstance(selected.get("user"), dict) else ""
            creator_url = str(selected.get("user", {}).get("url") or "") if isinstance(selected.get("user"), dict) else ""
            title = f"Pexels video {selected.get('id', '')}".strip()
            width = int(selected_file.get("width") or selected.get("width") or 0)
            height = int(selected_file.get("height") or selected.get("height") or 0)
            source_id = str(selected.get("id") or source_url)
            extension = ".mp4"
        else:
            raise AssetExecutionError("pexels provider supports visual and video assets only")

        raw = self._download_bytes(source_url, key)
        if len(raw) > 50 * 1024 * 1024:
            raise AssetExecutionError("pexels media exceeds 50 MiB limit")

        digest = hashlib.sha256(
            f"{job.run_id}:{job.asset_request_id}:{source_id}".encode("utf-8")
        ).hexdigest()[:16]
        directory = self.root / "asset_jobs" / job.run_id
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{job.asset_request_id}{extension}"
        path.write_bytes(raw)

        metadata = {
            "source": "pexels",
            "source_id": source_id,
            "source_url": source_url,
            "attribution_url": attribution_url,
            "creator": creator,
            "creator_url": creator_url,
            "title": title,
            "width": width,
            "height": height,
            "query": query,
            "media_kind": media_kind,
            "attribution_required": True,
            "attribution_text": (
                f"Photo by {creator} on Pexels" if media_kind == "photo" and creator
                else f"Video by {creator} on Pexels" if media_kind == "video" and creator
                else "Media provided by Pexels"
            ),
        }
        if not source_url:
            raise AssetExecutionError("pexels returned an empty media URL")

        return AssetExecution(
            provider="pexels",
            state="COMPLETED",
            result={
                "asset_id": f"asset-{digest}",
                "job_id": job.job_id,
                "type": job.asset_type,
                "status": "DRAFT",
                "claim_refs": list(job.claim_refs),
                "evidence_refs": list(job.evidence_refs),
                "acceptance_criteria": list(job.acceptance_criteria),
                "provider": "pexels",
                "path": str(path),
                "metadata": metadata,
            },
        )

    @staticmethod
    def _pexels_get_json(url: str, key: str) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": key,
                "User-Agent": "ContentFactory/1.0 (+https://github.com/sebastiansayama-boop/content_factory)",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise AssetExecutionError(f"pexels search failed: {exc}") from exc
        if not isinstance(payload, dict):
            raise AssetExecutionError("pexels returned a non-object payload")
        return payload

    @staticmethod
    def _download_bytes(url: str, key: str) -> bytes:
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": key,
                "User-Agent": "ContentFactory/1.0 (+https://github.com/sebastiansayama-boop/content_factory)",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read(50 * 1024 * 1024 + 1)
        except Exception as exc:
            raise AssetExecutionError(f"pexels media download failed: {exc}") from exc

    @staticmethod
    def _submit_higgsfield(job: AssetJob) -> AssetExecution:
        key = os.environ.get("HF_KEY", "").strip()
        if not key:
            raise AssetExecutionError("HF_KEY is required for FACTORY_ASSET_PROVIDER=higgsfield")
        if job.asset_type != "visual":
            raise AssetExecutionError("higgsfield adapter currently supports visual jobs only")

        model = os.environ.get(
            "HF_IMAGE_MODEL",
            "recraft/v4.1/text-to-image",
        ).strip()
        prompt = (
            f"Create a production-ready visual for script unit {job.script_unit_id}. "
            "Preserve the supplied editorial provenance boundary. "
            f"Knowledge claims: {', '.join(job.claim_refs)}. "
            f"Evidence: {', '.join(job.evidence_refs)}."
        )
        body = json.dumps({
            "prompt": prompt,
            "resolution": os.environ.get("HF_IMAGE_RESOLUTION", "1k"),
            "aspect_ratio": os.environ.get("HF_IMAGE_ASPECT_RATIO", "9:16"),
            "output_format": "png",
        }).encode("utf-8")
        request = urllib.request.Request(
            f"https://api.higgsfield.ai/{model}",
            data=body,
            headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
                status = int(response.status)
        except Exception as exc:
            raise AssetExecutionError(f"higgsfield submission failed: {exc}") from exc
        if status < 200 or status >= 300:
            raise AssetExecutionError(f"higgsfield returned HTTP {status}")
        try:
            response_body: Any = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AssetExecutionError("higgsfield returned non-JSON response") from exc
        request_id = response_body.get("request_id") if isinstance(response_body, dict) else None
        if not request_id:
            raise AssetExecutionError("higgsfield response did not contain request_id")
        return AssetExecution(
            provider="higgsfield",
            state="SUBMITTED",
            result={
                "provider": "higgsfield",
                "provider_request_id": str(request_id),
                "status": "SUBMITTED",
                "claim_refs": list(job.claim_refs),
                "evidence_refs": list(job.evidence_refs),
            },
        )
