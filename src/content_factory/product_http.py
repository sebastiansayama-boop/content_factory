from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from .service import FactoryService, Handler, MAX_REQUEST_BYTES, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS
from .workspace import ContentWorkspace


class ProductHandler(Handler):
    workspace: ContentWorkspace

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length < 0 or length > MAX_REQUEST_BYTES:
            raise ValueError("request body exceeds maximum size")
        raw = self.rfile.read(length)
        if len(raw) != length:
            raise ValueError("incomplete request body")
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    @staticmethod
    def _public_beta() -> bool:
        return os.environ.get("FACTORY_PUBLIC_BETA", "").strip().lower() in {"1", "true", "yes"}

    def _product_access_allowed(self) -> bool:
        return self._public_beta() or self._authorized()

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/index.html"}:
            raw = (Path(__file__).parent / "static" / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in {"/api/analyze", "/api/produce"}:
            super().do_POST()
            return
        now = time.monotonic()
        if not self._product_access_allowed():
            self._json(401, {"error": "missing or invalid API token"})
            return
        if self._rate_limited(self._authorized_requests, RATE_LIMIT_REQUESTS, now, RATE_LIMIT_WINDOW_SECONDS):
            self._json(429, {"error": "product rate limit exceeded"}, retry_after=60)
            return
        try:
            payload = self._body()
            if self.path == "/api/analyze":
                result = self.workspace.analyze(
                    source=str(payload.get("source", "")),
                    title=str(payload.get("title", "Untitled source")),
                )
            else:
                result = self.workspace.produce(
                    source=str(payload.get("source", "")),
                    story=payload.get("story") if isinstance(payload.get("story"), dict) else {},
                    formats=[str(value) for value in payload.get("formats", [])],
                )
            self._json(200, result)
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid JSON body"})
        except UnicodeDecodeError:
            self._json(400, {"error": "request body must be UTF-8"})
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
        except Exception as exc:
            self._json(400, {"error": str(exc)})


def main() -> None:
    service = FactoryService()
    ProductHandler.service = service
    ProductHandler.workspace = ContentWorkspace(service)
    from http.server import ThreadingHTTPServer

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer((host, port), ProductHandler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        service.close()


if __name__ == "__main__":
    main()
