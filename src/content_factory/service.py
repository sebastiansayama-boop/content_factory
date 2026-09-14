from __future__ import annotations

import json
import os
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from uuid import uuid4

from .artifacts import ArtifactStore
from .gemini_adapter import GeminiOpenAICompatibleAdapter
from .openai_capability import openai_text_capability
from .runtime import (
    AcceptanceDecision,
    Capability,
    FactoryRuntime,
    PublicationResult,
    VerificationResult,
    WorkItem,
)
from .runtime_store import RuntimeStore
from .text_capability import text_generation_capability


class WebhookPublisher:
    """Deliver an accepted output to a configured HTTPS webhook."""

    def __init__(self, url: str, token: str | None = None, timeout: float = 30.0) -> None:
        if not url.startswith("https://"):
            raise ValueError("PUBLISH_URL must use https://")
        self.url = url
        self.token = token
        self.timeout = timeout

    def publish(self, work_item: WorkItem, execution, publication_id: str | None = None) -> PublicationResult:
        publication_id = publication_id or str(uuid4())
        body = json.dumps(
            {
                "publication_id": publication_id,
                "operation_id": work_item.operation_id,
                "work_item_id": work_item.work_item_id,
                "work_item_revision_id": work_item.revision_id,
                "output_revision_id": execution.output_revision_id,
                "execution_id": execution.execution_id,
                "content": execution.payload,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        headers = {"Content-Type": "application/json", "Idempotency-Key": publication_id}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(self.url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                status = int(response.status)
                response.read()
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"publisher returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"publisher connection failed: {exc.reason}") from exc
        if status < 200 or status >= 300:
            raise RuntimeError(f"publisher returned HTTP {status}")
        return PublicationResult(
            publication_id=publication_id,
            output_revision_id=execution.output_revision_id,
            target=self.url,
            externally_observable=True,
            evidence_refs=(f"http:{status}", publication_id),
        )


class FactoryService:
    def __init__(self) -> None:
        root = Path(os.environ.get("FACTORY_DATA_DIR", "./data"))
        root.mkdir(parents=True, exist_ok=True)
        self._store = RuntimeStore(root / "runtime.sqlite3")
        self._artifacts = ArtifactStore(root / "artifacts")
        publisher_url = os.environ.get("PUBLISH_URL", "").strip()
        publisher = (
            WebhookPublisher(publisher_url, os.environ.get("PUBLISH_AUTH_TOKEN"))
            if publisher_url
            else None
        )
        self._publisher = publisher
        self._provider, self._capability = self._build_provider()
        self._lock = threading.Lock()

    @staticmethod
    def _build_provider() -> tuple[str, Capability]:
        configured = os.environ.get("FACTORY_PROVIDER", "").strip().lower()
        provider = configured or ("gemini" if os.environ.get("GEMINI_API_KEY", "").strip() else "openai")
        if provider == "gemini":
            adapter = GeminiOpenAICompatibleAdapter()
            capability = text_generation_capability(
                capability_id="gemini.text.generate",
                provider=adapter,
                generate=adapter.generate,
                response_text=adapter.response_text,
            )
            return provider, capability
        if provider == "openai":
            return provider, openai_text_capability()
        raise ValueError("FACTORY_PROVIDER must be 'gemini' or 'openai'")

    def close(self) -> None:
        self._store.close()

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "provider": self._provider,
            "provider_key_configured": bool(
                os.environ.get("GEMINI_API_KEY")
                if self._provider == "gemini"
                else os.environ.get("OPENAI_API_KEY")
            ),
            "gemini_key_configured": bool(os.environ.get("GEMINI_API_KEY")),
            "openai_key_configured": bool(os.environ.get("OPENAI_API_KEY")),
            "publisher_configured": self._publisher is not None,
            "api_auth_configured": bool(os.environ.get("FACTORY_API_TOKEN")),
        }

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        work_item_id = str(payload.get("work_item_id") or f"wi-{uuid4()}")
        revision_id = str(payload.get("revision_id") or "request-r1")
        operation_id = str(payload.get("operation_id") or f"op-{uuid4()}")
        requested_outcome = str(payload.get("requested_outcome") or "").strip()
        if not requested_outcome:
            raise ValueError("requested_outcome is required")
        acceptance_authority = str(payload.get("acceptance_authority") or "").strip()
        release_authority = str(payload.get("release_authority") or "").strip()
        if not acceptance_authority:
            raise ValueError("acceptance_authority is required")
        if not release_authority:
            raise ValueError("release_authority is required")

        capability_id = self._capability.capability_id
        item = WorkItem(
            work_item_id=work_item_id,
            revision_id=revision_id,
            objective=str(payload.get("objective") or requested_outcome),
            requested_outcome=requested_outcome,
            inputs=tuple(map(str, payload.get("inputs", []))),
            knowledge_basis=tuple(map(str, payload.get("knowledge_basis", []))),
            required_capabilities=(capability_id,),
            owner=str(payload.get("owner") or "api"),
            acceptance_criteria=tuple(map(str, payload.get("acceptance_criteria", ["non-empty provider output"]))),
            release_requirements=tuple(map(str, payload.get("release_requirements", ["explicit release authority"]))),
            constraints=tuple(map(str, payload.get("constraints", []))),
            dependencies=tuple(map(str, payload.get("dependencies", []))),
            success_signals=tuple(map(str, payload.get("success_signals", []))),
            operation_id=operation_id,
        )

        with self._lock:
            runtime = FactoryRuntime(
                publisher=self._publisher,
                artifact_store=self._artifacts,
                runtime_store=self._store,
            )
            runtime.register_capability(self._capability)
            if work_item_id not in runtime.states:
                runtime.submit(item, actor="api")
            else:
                if runtime.operation_ids.get(work_item_id) != operation_id:
                    raise ValueError("operation_id conflicts with existing work item")
            publication = runtime.run(
                item,
                verification=self._verify,
                acceptance=lambda _, verified: AcceptanceDecision(
                    output_revision_id=verified.output_revision_id,
                    accepted=True,
                    authority=acceptance_authority,
                    reason="explicit API acceptance authority",
                ),
                release_authority=release_authority,
                actor="api",
            )
            state = runtime.states[item.work_item_id].value
            result = {
                "work_item_id": work_item_id,
                "operation_id": operation_id,
                "provider": self._provider,
                "state": state,
                "events": [event.__dict__ for event in runtime.provenance(work_item_id)],
            }
            if publication is not None:
                result["publication"] = publication.__dict__
            execution = runtime.executions.get(work_item_id)
            if execution is not None:
                result["execution"] = {
                    "execution_id": execution.execution_id,
                    "output_revision_id": execution.output_revision_id,
                    "capability_id": execution.capability_id,
                    "evidence_refs": execution.evidence_refs,
                    "output": execution.payload,
                }
            result["attempts"] = runtime.attempts.get(work_item_id, [])
            return result

    @staticmethod
    def _verify(_, execution) -> VerificationResult:
        passed = isinstance(execution.payload, str) and bool(execution.payload.strip())
        return VerificationResult(
            output_revision_id=execution.output_revision_id,
            passed=passed,
            evidence_refs=("service.non_empty_text_check",),
            reason="provider output is non-empty text" if passed else "provider output is empty",
        )


class Handler(BaseHTTPRequestHandler):
    service: FactoryService

    def _json(self, status: int, body: dict[str, Any]) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _authorized(self) -> bool:
        expected = os.environ.get("FACTORY_API_TOKEN", "").strip()
        if not expected:
            return False
        return self.headers.get("Authorization", "") == f"Bearer {expected}"

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json(200, self.service.health())
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/run":
            self._json(404, {"error": "not found"})
            return
        if not self._authorized():
            self._json(401, {"error": "missing or invalid API token"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object")
            result = self.service.run(payload)
            status = 200 if result["state"] in {"OBSERVED", "DELIVERED"} else 422
            self._json(status, result)
        except Exception as exc:
            self._json(400, {"error": str(exc)})

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    service = FactoryService()
    Handler.service = service
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer((host, port), Handler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        service.close()


if __name__ == "__main__":
    main()
