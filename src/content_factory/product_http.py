from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .service import FactoryService, Handler
from .workspace import ContentWorkspace


class ProductHandler(Handler):
    workspace: ContentWorkspace

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

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
        if not self._authorized():
            self._json(401, {"error": "missing or invalid API token"})
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
