from __future__ import annotations

import hashlib
import mimetypes
import json
import os
import re
import struct
import wave
import zlib
import urllib.request
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .asset_jobs import AssetJob, AssetJobStore
from .openverse_adapter import OpenverseImageProvider
from .visual_relevance import OpenAIVisualRelevanceVerifier
from .visual_policy import VisualPolicyStore


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
            return self._execute_stub(job)
        if provider == "openverse":
            if job.asset_type == "visual":
                return self._execute_openverse_image(job)
            return self._execute_stub(job)
        if provider == "higgsfield":
            if job.asset_type == "visual":
                return self._execute_higgsfield_image(job)
            # Higgsfield is currently a visual provider; keep voice deterministic.
            return self._execute_stub(job)
        raise AssetExecutionError("FACTORY_ASSET_PROVIDER must be 'stub', 'openverse' or 'higgsfield'")

    def _execute_stub(self, job: AssetJob) -> AssetExecution:
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

    def _execute_openverse_image(self, job: AssetJob) -> AssetExecution:
        query = job.visual_intent.strip()
        if not query:
            raise AssetExecutionError("Openverse visual job requires visual_intent")
        provider = OpenverseImageProvider()
        candidates = provider.search(query, limit=20)
        ranked = self._rank_relevant_openverse_candidates(query, candidates)
        if not ranked:
            raise AssetExecutionError(
                f"Openverse returned no metadata-relevant candidates for: {query}"
            )

        verify_limit = max(2, min(int(os.environ.get("FACTORY_VISUAL_VERIFY_CANDIDATES", "6")), 8))
        verification_candidates = ranked[:verify_limit]
        preview_parts: list[tuple[str, bytes, str]] = []
        preview_errors: list[str] = []
        for candidate in verification_candidates:
            if not candidate.preview_url:
                preview_errors.append(f"{candidate.id}: missing preview")
                continue
            try:
                image_bytes = self._download_openverse_bytes(candidate.preview_url, max_bytes=2 * 1024 * 1024)
                mime_type = mimetypes.guess_type(candidate.preview_url)[0] or "image/jpeg"
                preview_parts.append((candidate.id, image_bytes, mime_type))
            except Exception as exc:
                preview_errors.append(f"{candidate.id}: {type(exc).__name__}")

        if not preview_parts:
            raise AssetExecutionError(
                f"Openverse candidates could not be prepared for visual verification: {', '.join(preview_errors)}"
            )

        verifier = OpenAIVisualRelevanceVerifier()
        verifications = verifier.verify_candidates(query, verification_candidates, preview_parts)
        accepted = [item for item in verifications if item.accepted]
        if not accepted:
            reasons = [f"{item.candidate_id}: {item.reason or item.decision}" for item in verifications]
            raise AssetExecutionError(
                f"visual relevance verification rejected all Openverse candidates for: {query}; "
                f"details={'; '.join(reasons[:8])}"
            )
        best_verification = max(accepted, key=lambda item: item.score)
        candidate = next(item for item in verification_candidates if item.id == best_verification.candidate_id)

        directory = self.root / "asset_jobs" / job.run_id
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{job.asset_request_id}.jpg"
        try:
            image_data = self._download_openverse_bytes(candidate.url, max_bytes=10 * 1024 * 1024)
        except Exception as exc:
            if candidate.preview_url and candidate.preview_url != candidate.url:
                image_data = self._download_openverse_bytes(candidate.preview_url, max_bytes=10 * 1024 * 1024)
            else:
                raise AssetExecutionError(f"Openverse image download failed: {exc}") from exc
        if not image_data:
            raise AssetExecutionError("Openverse returned an empty image")
        path.write_bytes(image_data)
        digest_full = hashlib.sha256(image_data).hexdigest()
        return AssetExecution(
            provider="openverse",
            state="COMPLETED",
            result={
                "asset_id": f"asset-{digest_full[:16]}",
                "job_id": job.job_id,
                "type": job.asset_type,
                "status": "READY",
                "claim_refs": list(job.claim_refs),
                "evidence_refs": list(job.evidence_refs),
                "acceptance_criteria": list(job.acceptance_criteria),
                "provider": "openverse",
                "path": str(path),
                "metadata": {
                    **candidate.to_dict(),
                    "query": query,
                    "source_url": candidate.foreign_landing_url,
                    "license_url": candidate.license_url,
                    "content_sha256": digest_full,
                    "visual_verification": {
                        "candidate_id": best_verification.candidate_id,
                        "decision": best_verification.decision,
                        "score": best_verification.score,
                        "subject_present": best_verification.subject_present,
                        "scene_present": best_verification.scene_present,
                        "forbidden_present": best_verification.forbidden_present,
                        "image_type_match": best_verification.image_type_match,
                        "reason": best_verification.reason,
                    },
                },
            },
        )

    @staticmethod
    def _download_openverse_bytes(url: str, *, max_bytes: int) -> bytes:
        if not url.strip():
            raise AssetExecutionError("Openverse download URL must not be empty")
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "content-factory/1.0"},
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise AssetExecutionError(f"Openverse image exceeds {max_bytes} byte limit")
        return data

    @staticmethod
    def _select_relevant_openverse_candidate(query: str, candidates: list[Any]) -> Any | None:
        ranked = AssetExecutor._rank_relevant_openverse_candidates(query, candidates)
        return ranked[0] if ranked else None

    @staticmethod
    def _rank_relevant_openverse_candidates(query: str, candidates: list[Any]) -> list[Any]:
        if not candidates:
            return []
        stopwords = {
            "a", "an", "and", "at", "for", "from", "in", "of", "on", "or", "the",
            "to", "with", "near", "over", "under", "into", "image", "photo",
            "picture", "photograph", "wildlife", "scene",
        }
        tokens = [
            token for token in re.findall(r"[a-z0-9]+", query.lower())
            if len(token) >= 3 and token not in stopwords
        ]
        if not tokens:
            return []
        ranked: list[tuple[int, int, Any]] = []
        for candidate in candidates:
            title = str(getattr(candidate, "title", "") or "").lower()
            landing = str(getattr(candidate, "foreign_landing_url", "") or "").lower()
            searchable = re.sub(r"[^a-z0-9]+", " ", f"{title} {landing}").strip()
            searchable_tokens = set(searchable.split())
            overlap = sum(1 for token in tokens if token in searchable_tokens)
            phrase_bonus = 6 if " ".join(tokens) in searchable else 0
            score = overlap * 3 + phrase_bonus
            if overlap:
                ranked.append((score, overlap, candidate))
        ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [candidate for _, _, candidate in ranked]

    def _execute_higgsfield_image(self, job: AssetJob) -> AssetExecution:
        key = os.environ.get("HF_KEY", "").strip()
        if not key:
            raise AssetExecutionError("HF_KEY is required for FACTORY_ASSET_PROVIDER=higgsfield")

        model = os.environ.get("HF_IMAGE_MODEL", "recraft/v4.1/text-to-image").strip()
        status_template = os.environ.get(
            "HF_STATUS_URL",
            "https://api.higgsfield.ai/requests/{request_id}/status",
        ).strip()
        output_format = os.environ.get("HF_IMAGE_OUTPUT_FORMAT", "png").strip().lower() or "png"
        if output_format not in {"png", "jpg", "jpeg", "webp"}:
            raise AssetExecutionError("HF_IMAGE_OUTPUT_FORMAT must be png, jpg, jpeg, or webp")

        prompt = (
            f"Create a production-ready visual for script unit {job.script_unit_id}. "
            "Preserve the supplied editorial provenance boundary. "
            f"Knowledge claims: {', '.join(job.claim_refs)}. "
            f"Evidence: {', '.join(job.evidence_refs)}."
        )
        body = json.dumps(
            {
                "prompt": prompt,
                "resolution": os.environ.get("HF_IMAGE_RESOLUTION", "1k"),
                "aspect_ratio": os.environ.get("HF_IMAGE_ASPECT_RATIO", "9:16"),
                "output_format": output_format,
            }
        ).encode("utf-8")
        response_body = self._higgsfield_json(
            urllib.request.Request(
                f"https://api.higgsfield.ai/{model}",
                data=body,
                headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
                method="POST",
            ),
            "submission",
        )
        request_id = str(response_body.get("request_id") or "").strip()
        if not request_id:
            raise AssetExecutionError("higgsfield response did not contain request_id")

        status_url = str(response_body.get("status_url") or "").strip()
        if not status_url:
            status_url = status_template.format(request_id=request_id)

        timeout_seconds = max(5, int(os.environ.get("HF_POLL_TIMEOUT_SECONDS", "90")))
        interval_seconds = max(0.1, float(os.environ.get("HF_POLL_INTERVAL_SECONDS", "2")))
        deadline = time.monotonic() + timeout_seconds
        result_body = response_body

        while True:
            state = str(result_body.get("status") or "").upper()
            if state in {"COMPLETED", "COMPLETE", "SUCCEEDED", "SUCCESS"}:
                break
            if state in {"FAILED", "ERROR", "CANCELLED"}:
                raise AssetExecutionError(
                    f"higgsfield generation failed: {json.dumps(result_body, ensure_ascii=False)[:1000]}"
                )
            if time.monotonic() >= deadline:
                raise AssetExecutionError(
                    f"higgsfield generation timed out after {timeout_seconds}s"
                )
            time.sleep(interval_seconds)
            result_body = self._higgsfield_json(
                urllib.request.Request(
                    status_url,
                    headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
                    method="GET",
                ),
                "status",
            )

        image_url = self._extract_higgsfield_image_url(result_body)
        if not image_url:
            raise AssetExecutionError("higgsfield completed without an image URL")

        suffix = "." + ("jpg" if output_format == "jpeg" else output_format)
        directory = self.root / "asset_jobs" / job.run_id
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{job.asset_request_id}{suffix}"
        try:
            with urllib.request.urlopen(
                urllib.request.Request(
                    image_url,
                    headers={"User-Agent": "content-factory/1.0"},
                    method="GET",
                ),
                timeout=30,
            ) as response:
                image_data = response.read()
        except Exception as exc:
            raise AssetExecutionError(f"higgsfield image download failed: {exc}") from exc
        if not image_data:
            raise AssetExecutionError("higgsfield returned an empty image")
        path.write_bytes(image_data)

        digest = hashlib.sha256(image_data).hexdigest()[:16]
        return AssetExecution(
            provider="higgsfield",
            state="COMPLETED",
            result={
                "asset_id": f"asset-{digest}",
                "job_id": job.job_id,
                "type": job.asset_type,
                "status": "READY",
                "claim_refs": list(job.claim_refs),
                "evidence_refs": list(job.evidence_refs),
                "acceptance_criteria": list(job.acceptance_criteria),
                "provider": "higgsfield",
                "path": str(path),
                "metadata": {
                    "provider_request_id": request_id,
                    "status_url": status_url,
                    "model": model,
                    "source_url": image_url,
                    "output_format": output_format,
                },
            },
        )

    @staticmethod
    def _higgsfield_json(request: urllib.request.Request, operation: str) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = int(response.status)
                raw = response.read().decode("utf-8")
        except Exception as exc:
            raise AssetExecutionError(f"higgsfield {operation} request failed: {exc}") from exc
        if status < 200 or status >= 300:
            raise AssetExecutionError(f"higgsfield {operation} returned HTTP {status}")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AssetExecutionError(f"higgsfield {operation} returned non-JSON") from exc
        if not isinstance(value, dict):
            raise AssetExecutionError(f"higgsfield {operation} response must be an object")
        return value

    @staticmethod
    def _extract_higgsfield_image_url(payload: dict[str, Any]) -> str | None:
        images = payload.get("images")
        if isinstance(images, list):
            for item in images:
                if isinstance(item, str) and item.startswith(("http://", "https://")):
                    return item
                if isinstance(item, dict):
                    for key in ("url", "image_url", "uri"):
                        value = str(item.get(key) or "").strip()
                        if value.startswith(("http://", "https://")):
                            return value
        output = payload.get("output")
        if isinstance(output, dict):
            nested = AssetExecutor._extract_higgsfield_image_url(output)
            if nested:
                return nested
        if isinstance(output, list):
            nested = AssetExecutor._extract_higgsfield_image_url({"images": output})
            if nested:
                return nested
        return None

