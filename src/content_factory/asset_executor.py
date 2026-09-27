from __future__ import annotations

import hashlib
import json
import os
import struct
import wave
import zlib
import urllib.request
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
                if execution.state == "SUBMITTED":
                    output.append(self.jobs.submit(job.job_id, execution.result))
                else:
                    output.append(self.jobs.complete(job.job_id, execution.result))
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
        if provider == "higgsfield":
            return self._submit_higgsfield(job)
        raise AssetExecutionError("FACTORY_ASSET_PROVIDER must be 'stub' or 'higgsfield'")

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
