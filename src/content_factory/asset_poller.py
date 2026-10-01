from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any

from .asset_jobs import AssetJob, AssetJobStore


class AssetProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderStatus:
    state: str
    result: dict[str, object]


class AssetProvider:
    name = "stub"

    def poll(self, job: AssetJob) -> ProviderStatus:
        raise NotImplementedError


class StubAssetProvider(AssetProvider):
    name = "stub"

    def poll(self, job: AssetJob) -> ProviderStatus:
        if job.result is None:
            raise AssetProviderError("stub job has no result")
        return ProviderStatus("COMPLETED", job.result)


class HiggsfieldAssetProvider(AssetProvider):
    name = "higgsfield"

    def poll(self, job: AssetJob) -> ProviderStatus:
        key = os.environ.get("HF_KEY", "").strip()
        request_id = str((job.result or {}).get("provider_request_id", "")).strip()
        if not key or not request_id:
            raise AssetProviderError("HF_KEY and provider_request_id are required")
        endpoint = os.environ.get("HF_STATUS_URL", "https://api.higgsfield.ai/requests/{request_id}/status").rstrip("/") + "/" + request_id
        request = urllib.request.Request(
            endpoint,
            headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = int(response.status)
                raw = response.read().decode("utf-8")
        except Exception as exc:
            raise AssetProviderError(f"higgsfield status request failed: {exc}") from exc
        if status < 200 or status >= 300:
            raise AssetProviderError(f"higgsfield returned HTTP {status}")
        try:
            body: Any = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AssetProviderError("higgsfield returned non-JSON status") from exc
        provider_state = str(body.get("status", "")).upper() if isinstance(body, dict) else ""
        if provider_state in {"QUEUED", "PENDING", "PROCESSING", "RUNNING"}:
            return ProviderStatus("SUBMITTED", {**(job.result or {}), "provider_status": provider_state})
        if provider_state in {"FAILED", "ERROR", "CANCELLED"}:
            return ProviderStatus("FAILED", {**(job.result or {}), "provider_status": provider_state, "provider_response": body})
        output = body.get("output") if isinstance(body, dict) else None
        if not output:
            raise AssetProviderError("higgsfield completed without output")
        return ProviderStatus("COMPLETED", {**(job.result or {}), "provider_status": provider_state or "COMPLETED", "output": output})


class AssetJobPoller:
    def __init__(self, jobs: AssetJobStore) -> None:
        self.jobs = jobs

    def poll_run(self, run_id: str) -> list[AssetJob]:
        result: list[AssetJob] = []
        providers = {"stub": StubAssetProvider(), "higgsfield": HiggsfieldAssetProvider()}
        for job in self.jobs.list_for_run(run_id):
            if job.status != "SUBMITTED":
                result.append(job)
                continue
            provider_name = str((job.result or {}).get("provider", "stub")).lower()
            provider = providers.get(provider_name)
            if provider is None:
                result.append(self.jobs.fail(job.job_id, {"error": f"unknown provider: {provider_name}"}))
                continue
            try:
                status = provider.poll(job)
                if status.state == "COMPLETED":
                    result.append(self.jobs.complete(job.job_id, status.result))
                elif status.state == "FAILED":
                    result.append(self.jobs.fail(job.job_id, status.result))
                else:
                    result.append(job)
            except Exception as exc:
                result.append(self.jobs.fail(job.job_id, {"error": str(exc), **(job.result or {})}))
        return result
