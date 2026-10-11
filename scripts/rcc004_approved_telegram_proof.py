from __future__ import annotations

import json
import os
import tempfile
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

from content_factory.content_run_planner import ContentRunPlanner
from content_factory.product_http import ProductHandler
from content_factory.service import FactoryService
from content_factory.workspace import ContentWorkspace
from scripts.publish_telegram_library import _prepare_run, _request

TITLE = "Content Factory — проверка публикации"
TEXT = (
    "**Content Factory — проверка публикации**\n\n"
    "Проверяем полный цикл работы Content Factory: подготовку материала, "
    "контроль качества, утверждение и отправку в Telegram.\n\n"
    "После публикации проверим идентификатор сообщения, сохранение результата "
    "и защиту от повторной отправки.\n\n"
    "Это техническая тестовая публикация, а не эпизод контент-серии."
)
DESTINATION = "@AtlasOpenLab"
DECISION = "rcc-004-user-approved-2026-10-11"


def main() -> None:
    if os.environ.get("RCC004_APPROVED") != "YES":
        raise RuntimeError("Explicit approved-publication gate missing")
    if os.environ.get("TELEGRAM_CHAT_ID") != DESTINATION:
        raise RuntimeError("Destination must be exactly @AtlasOpenLab")
    if not os.environ.get("TELEGRAM_BOT_TOKEN"):
        raise RuntimeError("Telegram token missing")
    if os.environ.get("FACTORY_TELEGRAM_FAKE") == "1":
        raise RuntimeError("Real Telegram transport required")

    with tempfile.TemporaryDirectory(prefix="rcc004-") as temporary:
        data_dir = Path(temporary)
        os.environ["FACTORY_DATA_DIR"] = str(data_dir)
        os.environ["FACTORY_API_TOKEN"] = "rcc004-local-only-token"
        service = FactoryService()
        ProductHandler.service = service
        ProductHandler.workspace = ContentWorkspace(service)
        ProductHandler.content_runs = service.content_runs
        ProductHandler.content_run_planner = ContentRunPlanner(ProductHandler.workspace)
        ProductHandler._rate_limited = staticmethod(lambda *args, **kwargs: False)
        server = ThreadingHTTPServer(("127.0.0.1", 0), ProductHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_port}"
        episode = {
            "title": TITLE, "text": TEXT, "episode": 1,
            "claims": [], "sources": [], "evidence": [],
            "story_state": {
                "series_id": "rcc-004-technical-proof", "title": TITLE,
                "central_question": "Verify one approved Telegram publication",
                "unresolved": [], "next_required_transition": "",
            },
        }
        try:
            run = _prepare_run(service, episode, data_dir, None)
            code, approved = _request(url, "POST", f"/api/runs/{run.run_id}/approve",
                                      {"decision_ref": DECISION, "channel": "telegram"},
                                      "rcc004-local-only-token")
            if code != 200:
                raise RuntimeError(f"Approval failed: {code} {approved}")
            publication_id = approved["result"]["publication"]["publication_id"]
            code, sent = _request(url, "POST", f"/api/runs/{run.run_id}/publish",
                                  {"publication_id": publication_id},
                                  "rcc004-local-only-token")
            if code != 200 or sent.get("status") != "PUBLISHED" or not sent.get("external_id"):
                raise RuntimeError(f"Publish failed: {code} {sent}")
            code, replay = _request(url, "POST", f"/api/runs/{run.run_id}/publish",
                                    {"publication_id": publication_id},
                                    "rcc004-local-only-token")
            replay_pass = (code == 200 and replay.get("idempotent") is True
                           and replay.get("external_id") == sent.get("external_id"))
            final = service.content_runs.get(run.run_id)
            result = {
                "run_id": run.run_id, "publication_id": publication_id,
                "message_id": sent["external_id"], "url": sent.get("external_url"),
                "destination": DESTINATION, "published": final.status == "PUBLISHED",
                "telegram_ok": sent.get("response", {}).get("telegram_ok"),
                "replay_idempotency_pass": replay_pass,
                "decision_ref": DECISION,
            }
            Path("rcc004-proof-result.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(result, ensure_ascii=False))
            if not result["published"] or not result["telegram_ok"] or not replay_pass:
                raise RuntimeError("Publication verification incomplete")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
            service.close()


if __name__ == "__main__":
    main()
