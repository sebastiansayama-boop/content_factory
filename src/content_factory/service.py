from __future__ import annotations

import hmac
import json
import os
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from uuid import uuid4

from .artifacts import ArtifactStore
from .content_run import ContentRunStore
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

MAX_REQUEST_BYTES = 64 * 1024
RATE_LIMIT_WINDOW_SECONDS = 60.0
RATE_LIMIT_REQUESTS = 10
AUTH_FAILURE_WINDOW_SECONDS = 60.0
AUTH_FAILURE_REQUESTS = 20


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


class LocalReleasePublisher:
    """Record a release locally without claiming an external effect."""

    def publish(self, work_item: WorkItem, execution, publication_id: str | None = None) -> PublicationResult:
        return PublicationResult(
            publication_id=publication_id or str(uuid4()),
            output_revision_id=execution.output_revision_id,
            target="internal://content-factory/release",
            externally_observable=False,
            evidence_refs=("local-release",),
        )


class FactoryService:
    def __init__(self) -> None:
        root = Path(os.environ.get("FACTORY_DATA_DIR", "./data"))
        root.mkdir(parents=True, exist_ok=True)
        self._store = RuntimeStore(root / "runtime.sqlite3")
        self._artifacts = ArtifactStore(root / "artifacts")
        self._content_runs = ContentRunStore(root / "content_runs.sqlite3")
        publisher_url = os.environ.get("PUBLISH_URL", "").strip()
        self._external_publisher_configured = bool(publisher_url)
        publisher = WebhookPublisher(publisher_url, os.environ.get("PUBLISH_AUTH_TOKEN")) if publisher_url else LocalReleasePublisher()
        self._publisher = publisher
        self._provider, self._capability = self._build_provider()
        self._acceptance_authority = os.environ.get("FACTORY_ACCEPTANCE_AUTHORITY", "").strip()
        self._release_authority = os.environ.get("FACTORY_RELEASE_AUTHORITY", "").strip()
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

    @property
    def content_runs(self) -> ContentRunStore:
        return self._content_runs

    def close(self) -> None:
        self._content_runs.close()
        self._store.close()

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "provider": self._provider,
            "publisher_configured": self._external_publisher_configured,
            "authorization_policy_configured": bool(
                self._acceptance_authority and self._release_authority
            ),
        }

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        work_item_id = str(payload.get("work_item_id") or f"wi-{uuid4()}")
        revision_id = str(payload.get("revision_id") or "request-r1")
        operation_id = str(payload.get("operation_id") or f"op-{uuid4()}")
        requested_outcome = str(payload.get("requested_outcome") or "").strip()
        if not requested_outcome:
            raise ValueError("requested_outcome is required")
        if len(requested_outcome) > 16_000:
            raise ValueError("requested_outcome exceeds maximum length")

        acceptance_authority = str(payload.get("acceptance_authority") or "").strip()
        release_authority = str(payload.get("release_authority") or "").strip()
        if not acceptance_authority:
            raise ValueError("acceptance_authority is required")
        if not release_authority:
            raise ValueError("release_authority is required")
        if not self._acceptance_authority or not self._release_authority:
            raise ValueError("factory authority policy is not configured")
        if not hmac.compare_digest(acceptance_authority, self._acceptance_authority):
            raise ValueError("acceptance authority denied")
        if not hmac.compare_digest(release_authority, self._release_authority):
            raise ValueError("release authority denied")

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
                    authority=self._acceptance_authority,
                    reason="server-configured acceptance authority",
                ),
                release_authority=self._release_authority,
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
    _rate_lock = threading.Lock()
    _authorized_requests: deque[float] = deque()
    _auth_failures: dict[str, deque[float]] = {}

    @staticmethod
    def _prune(bucket: deque[float], now: float, window: float) -> None:
        cutoff = now - window
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()

    @classmethod
    def _rate_limited(cls, bucket: deque[float], limit: int, now: float, window: float) -> bool:
        with cls._rate_lock:
            cls._prune(bucket, now, window)
            if len(bucket) >= limit:
                return True
            bucket.append(now)
            return False

    @classmethod
    def _auth_failure_limited(cls, client_ip: str, now: float) -> bool:
        with cls._rate_lock:
            bucket = cls._auth_failures.setdefault(client_ip, deque())
            cls._prune(bucket, now, AUTH_FAILURE_WINDOW_SECONDS)
            if len(bucket) >= AUTH_FAILURE_REQUESTS:
                return True
            bucket.append(now)
            if len(cls._auth_failures) > 1024:
                stale = [key for key, value in cls._auth_failures.items() if not value]
                for key in stale[:256]:
                    cls._auth_failures.pop(key, None)
            return False

    def _json(self, status: int, body: dict[str, Any], retry_after: int | None = None) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        if retry_after is not None:
            self.send_header("Retry-After", str(retry_after))
        self.end_headers()
        self.wfile.write(raw)

    def _authorized(self) -> bool:
        expected = os.environ.get("FACTORY_API_TOKEN", "").strip()
        presented = self.headers.get("Authorization", "")
        expected_header = f"Bearer {expected}" if expected else ""
        return bool(expected) and hmac.compare_digest(presented, expected_header)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json(200, self.service.health())
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/run":
            self._json(404, {"error": "not found"})
            return

        now = time.monotonic()
        client_ip = self.client_address[0]
        if self._auth_failure_limited(client_ip, now):
            self._json(429, {"error": "too many authentication failures"}, retry_after=60)
            return
        if not self._authorized():
            self._json(401, {"error": "missing or invalid API token"})
            return
        if self._rate_limited(self._authorized_requests, RATE_LIMIT_REQUESTS, now, RATE_LIMIT_WINDOW_SECONDS):
            self._json(429, {"error": "run rate limit exceeded"}, retry_after=60)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length < 0 or content_length > MAX_REQUEST_BYTES:
                raise ValueError("request body exceeds maximum size")
            raw_body = self.rfile.read(content_length)
            if len(raw_body) != content_length:
                raise ValueError("incomplete request body")
            payload = json.loads(raw_body.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object")
            result = self.service.run(payload)
            status = 200 if result["state"] in {"OBSERVED", "DELIVERED"} else 422
            self._json(status, result)
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid JSON body"})
        except UnicodeDecodeError:
            self._json(400, {"error": "request body must be UTF-8"})
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
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
