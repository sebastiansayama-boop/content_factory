import io
import json

from content_factory.product_http import ProductHandler


class FakeBot:
    def __init__(self):
        self.updates = []

    def handle_update(self, update):
        self.updates.append(update)


class WebhookHandler(ProductHandler):
    def __init__(self, body, secret):
        self.rfile = io.BytesIO(body)
        self.headers = {
            "Content-Length": str(len(body)),
            "X-Telegram-Bot-Api-Secret-Token": secret,
        }
        self.status = None
        self.response = None

    def _json(self, status, body, retry_after=None):
        self.status = status
        self.response = body


def test_telegram_webhook_requires_secret(monkeypatch):
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "secret")
    bot = FakeBot()
    ProductHandler.telegram_bot = bot
    handler = WebhookHandler(b'{}', "wrong")

    handler._handle_telegram_webhook()

    assert handler.status == 401
    assert bot.updates == []


def test_telegram_webhook_accepts_update_and_dispatches(monkeypatch):
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "secret")
    bot = FakeBot()
    ProductHandler.telegram_bot = bot
    payload = {"update_id": 7, "message": {"chat": {"id": "123"}, "text": "topic"}}
    body = json.dumps(payload).encode("utf-8")
    handler = WebhookHandler(body, "secret")

    handler._handle_telegram_webhook()

    assert handler.status == 200
    assert handler.response == {"ok": True}

    # The webhook dispatch is intentionally asynchronous; make the handler thread visible
    # without introducing a production sleep into the implementation.
    import time
    deadline = time.time() + 1.0
    while time.time() < deadline and not bot.updates:
        time.sleep(0.01)
    assert bot.updates == [payload]
