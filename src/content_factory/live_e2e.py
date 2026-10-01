"""One-shot live Gemini/API E2E probe for the hosted runtime.

The probe is intentionally isolated in a temporary data directory. It uses the
real runtime environment (including GEMINI_API_KEY and FACTORY_API_TOKEN) but
does not publish externally.
"""

from __future__ import annotations

import json
import os
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

from .content_run_planner import ContentRunPlanner
from .product_http import ProductHandler
from .service import FactoryService
from .workspace import ContentWorkspace


def _request(base_url: str, method: str, path: str, token: str, payload: dict | None = None) -> tuple[int, dict]:
    parts = urlsplit(base_url)
    connection = HTTPConnection(parts.hostname, parts.port, timeout=240)
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    raw = response.read()
    status = response.status
    connection.close()
    return status, json.loads(raw.decode("utf-8")) if raw else {}


def run() -> None:
    token = os.environ.get("FACTORY_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("FACTORY_API_TOKEN is required for live E2E probe")
    if not os.environ.get("GEMINI_API_KEY", "").strip():
        raise RuntimeError("GEMINI_API_KEY is required for live E2E probe")

    with TemporaryDirectory(prefix="content-factory-live-e2e-") as data_dir:
        previous_data_dir = os.environ.get("FACTORY_DATA_DIR")
        previous_provider = os.environ.get("FACTORY_PROVIDER")
        os.environ["FACTORY_DATA_DIR"] = data_dir
        os.environ["FACTORY_PROVIDER"] = "gemini"

        service = FactoryService()
        server = None
        thread = None
        try:
            # Seed unrelated ACCEPTED knowledge so the first factory call tests
            # relevance routing, not merely an empty knowledge store.
            service.knowledge.capture(
                run_id="live-e2e-seed",
                research={
                    "claims": [{
                        "id": "live-e2e-seed-claim",
                        "text": "Automobiles changed expectations about urban mobility.",
                        "confidence": "high",
                        "source_ids": ["live-e2e-seed-source"],
                        "evidence_ids": ["live-e2e-seed-evidence"],
                        "scope": "urban mobility",
                        "known_unknowns": [],
                    }],
                    "sources": [{
                        "id": "live-e2e-seed-source",
                        "title": "Live E2E seed source",
                        "url": "https://example.com/live-e2e-seed",
                    }],
                    "evidence": [{
                        "id": "live-e2e-seed-evidence",
                        "source_id": "live-e2e-seed-source",
                        "excerpt": "Automobiles changed expectations about urban mobility.",
                        "locator": "paragraph 1",
                        "provenance": "live-e2e-seed",
                    }],
                    "editorial_angles": [],
                },
            )
            seeded = service.knowledge.search(
                "Automobiles changed expectations about urban mobility.",
                include_candidates=True,
            )["claims"]
            if not seeded:
                raise RuntimeError("live E2E seed claim was not captured")
            seed_claim_id = str(seeded[0]["claim_id"])
            service.knowledge.promote_claim(
                seed_claim_id,
                decision_ref="LIVE-E2E-SEED",
            )

            ProductHandler.service = service
            ProductHandler.workspace = ContentWorkspace(service)
            ProductHandler.content_runs = service.content_runs
            ProductHandler.content_run_planner = ContentRunPlanner(ProductHandler.workspace)

            server = ThreadingHTTPServer(("127.0.0.1", 0), ProductHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_port}"

            title = "LIVE E2E — volcanic lightning research"
            brief = (
                "Explain how volcanic lightning forms during explosive eruptions. "
                "Use retrieved evidence, distinguish established observations from "
                "remaining uncertainty, and produce an evidence-grounded article."
            )

            status, created = _request(
                base_url,
                "POST",
                "/api/runs",
                token,
                {
                    "title": title,
                    "brief": brief,
                    "audience": "general readers",
                    "goal": "evidence-grounded article",
                    "formats": ["article", "social_post", "visual_card"],
                    "constraints": ["clear", "concise"],
                },
            )
            assert status == 201, created
            run_id = created["run_id"]

            status, researched = _request(
                base_url,
                "POST",
                f"/api/runs/{run_id}/factory",
                token,
                {},
            )
            assert status == 409, researched
            assert researched["run"]["status"] == "RESEARCH_READY", researched
            candidates = researched.get("candidates") or []
            assert candidates, researched
            candidate_id = str(candidates[0]["claim_id"])
            candidate_text = str(candidates[0]["text"]).strip()
            assert candidate_text, candidates[0]
            assert researched["next"].startswith("promote accepted claims"), researched

            status, promoted = _request(
                base_url,
                "POST",
                f"/api/knowledge/{candidate_id}/promote",
                token,
                {"decision_ref": "LIVE-E2E-HUMAN-REVIEW"},
            )
            assert status == 200, promoted
            assert promoted["status"] == "ACCEPTED", promoted

            status, built = _request(
                base_url,
                "POST",
                f"/api/runs/{run_id}/factory",
                token,
                {},
            )
            assert status == 200, built
            assert built["qc"]["status"] == "PASSED", built
            result = built["run"]["result"]

            status, trace = _request(
                base_url,
                "GET",
                f"/api/runs/{run_id}/execution-trace",
                token,
            )
            assert status == 200, trace
            stages = [
                event["data"]["stage"]
                for event in trace.get("events", [])
                if event.get("operation") == "trace"
            ]
            for required in ("RESEARCH", "EDITORIAL", "PRODUCTION", "QC"):
                assert required in stages, stages

            script_units = result["script"]["units"]
            assert script_units, result["script"]
            assert all(candidate_id in list(unit.get("claim_refs") or []) for unit in script_units), script_units

            content_spec = result["content_spec"]
            assert content_spec["claim_refs"] == [candidate_id], content_spec
            assert content_spec["evidence_refs"], content_spec

            production = result["production"]
            assert production["status"] == "READY_FOR_REVIEW", production
            assert production["output"]["status"] == "ASSEMBLED", production
            assert production["assets"], production

            print(json.dumps({
                "status": "PASS",
                "provider": "gemini",
                "run_id": run_id,
                "research_status": researched["run"]["status"],
                "candidate_id": candidate_id,
                "candidate_promoted": promoted["status"],
                "qc": built["qc"]["status"],
                "production_status": production["status"],
                "trace_stages": stages,
                "claim_refs": content_spec["claim_refs"],
                "evidence_ref_count": len(content_spec["evidence_refs"]),
                "asset_count": len(production["assets"]),
                "seed_knowledge_was_irrelevant": True,
            }, sort_keys=True))
        finally:
            if server is not None:
                server.shutdown()
                server.server_close()
            if thread is not None:
                thread.join(timeout=5)
            service.close()
            if previous_data_dir is None:
                os.environ.pop("FACTORY_DATA_DIR", None)
            else:
                os.environ["FACTORY_DATA_DIR"] = previous_data_dir
            if previous_provider is None:
                os.environ.pop("FACTORY_PROVIDER", None)
            else:
                os.environ["FACTORY_PROVIDER"] = previous_provider


if __name__ == "__main__":
    run()
