from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from .content_run import ContentRunStore
from .content_run_planner import ContentRunPlanner
from .service import FactoryService, Handler
from .workspace import ContentWorkspace


class ProductHandler(Handler):
    workspace: ContentWorkspace
    content_runs: ContentRunStore
    content_run_planner: ContentRunPlanner

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length < 0 or length > 64 * 1024:
            raise ValueError("request body exceeds maximum size")
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def _protect_product_api(self) -> bool:
        now = time.monotonic()
        client_ip = self.client_address[0]
        if self._auth_failure_limited(client_ip, now):
            self._json(429, {"error": "too many authentication failures"}, retry_after=60)
            return False
        if not self._authorized():
            self._json(401, {"error": "missing or invalid API token"})
            return False
        if self._rate_limited(self._authorized_requests, 10, now, 60.0):
            self._json(429, {"error": "product rate limit exceeded"}, retry_after=60)
            return False
        return True

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            raw = (Path(__file__).parent / "static" / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        if self.path == "/api/runs" or self.path.startswith("/api/runs/"):
            if not self._protect_product_api():
                return
            if self.path == "/api/runs":
                self._json(200, {"runs": [run.to_dict() for run in self.content_runs.list()]})
                return
            run_id = self.path.removeprefix("/api/runs/").strip("/")
            if run_id.endswith("/plan"):
                run_id = run_id.removesuffix("/plan").strip("/")
            run = self.content_runs.get(run_id)
            if run is None:
                self._json(404, {"error": "content run not found"})
                return
            self._json(200, run.to_dict())
            return

        super().do_GET()

    def do_POST(self) -> None:
        is_run_plan = self.path.startswith("/api/runs/") and self.path.endswith("/plan")
        if self.path not in {"/api/analyze", "/api/produce", "/api/regenerate", "/api/runs"} and not is_run_plan:
            super().do_POST()
            return

        if not self._protect_product_api():
            return

        try:
            if is_run_plan:
                run_id = self.path.removeprefix("/api/runs/").removesuffix("/plan").strip("/")
                if not run_id:
                    raise ValueError("content run id is required")
                run = self.content_runs.get(run_id)
                if run is None:
                    self._json(404, {"error": "content run not found"})
                    return
                self.content_runs.start_planning(run_id)
                try:
                    plan = self.content_run_planner.plan(
                        run_id=run.run_id,
                        title=run.title,
                        brief=run.brief,
                        audience=run.audience,
                        goal=run.goal,
                        formats=list(run.formats),
                        constraints=list(run.constraints),
                    )
                except Exception:
                    self.content_runs.mark_failed(run_id)
                    raise
                updated = self.content_runs.save_plan(run_id, plan)
                self._json(200, updated.to_dict())
                return

            payload = self._body()
            if self.path == "/api/runs":
                title = str(payload.get("title", "")).strip()
                brief = str(payload.get("brief", "")).strip()
                audience = str(payload.get("audience", "")).strip()
                goal = str(payload.get("goal", "")).strip()
                formats = payload.get("formats", [])
                constraints = payload.get("constraints", [])
                if not title:
                    raise ValueError("title is required")
                if not brief:
                    raise ValueError("brief is required")
                if len(title) > 200:
                    raise ValueError("title exceeds maximum length")
                if len(brief) > 16_000:
                    raise ValueError("brief exceeds maximum length")
                if not isinstance(formats, list) or not all(isinstance(value, str) for value in formats):
                    raise ValueError("formats must be an array of strings")
                if not isinstance(constraints, list) or not all(isinstance(value, str) for value in constraints):
                    raise ValueError("constraints must be an array of strings")
                run = self.content_runs.create(
                    title=title,
                    brief=brief,
                    audience=audience,
                    goal=goal,
                    formats=tuple(value.strip() for value in formats if value.strip()),
                    constraints=tuple(value.strip() for value in constraints if value.strip()),
                )
                self._json(201, run.to_dict())
                return
            if self.path == "/api/analyze":
                result = self.workspace.analyze(
                    source=str(payload.get("source", "")),
                    title=str(payload.get("title", "Untitled source")),
                )
            else:
                formats = payload.get("formats", [])
                if not isinstance(formats, list):
                    raise ValueError("formats must be an array")
                result = self.workspace.produce(
                    source=str(payload.get("source", "")),
                    story=payload.get("story") if isinstance(payload.get("story"), dict) else {},
                    formats=[str(value) for value in formats],
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
    ProductHandler.content_runs = service.content_runs
    ProductHandler.content_run_planner = ContentRunPlanner(ProductHandler.workspace)
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
