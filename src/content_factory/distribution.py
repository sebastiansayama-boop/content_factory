from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from typing import Any


class TelegramDistributionAdapter:
    """Publish a prepared Content Factory payload to Telegram."""

    def __init__(self, token: str, chat_id: str, *, timeout: float = 30.0) -> None:
        if not token.strip():
            raise ValueError("Telegram bot token is required")
        if not str(chat_id).strip():
            raise ValueError("Telegram chat id is required")
        self.token = token.strip()
        self.chat_id = str(chat_id).strip()
        self.timeout = timeout
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    @classmethod
    def from_env(cls) -> "TelegramDistributionAdapter":
        return cls(
            os.environ.get("TELEGRAM_BOT_TOKEN", ""),
            os.environ.get("TELEGRAM_CHAT_ID", ""),
        )

    def prepare(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = self._text(payload)
        if not text:
            raise ValueError("Telegram publication requires non-empty text")
        return {
            "destination": self.chat_id,
            "text": text[:4096],
        }

    def publish(self, payload: dict[str, Any], *, publication_id: str) -> dict[str, Any]:
        prepared = self.prepare(payload)
        request = urllib.request.Request(
            f"{self.base_url}/sendMessage",
            data=json.dumps({
                "chat_id": prepared["destination"],
                "text": prepared["text"],
            }, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        if not body.get("ok"):
            raise ValueError(f"Telegram publish failed: {body}")
        message = body.get("result") or {}
        message_id = str(message.get("message_id") or "").strip()
        if not message_id:
            raise ValueError("Telegram response has no message_id")
        return {
            "external_id": message_id,
            "external_url": None,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "response": {
                "mode": "telegram",
                "chat_id": prepared["destination"],
                "message_id": message_id,
                "telegram_ok": True,
                "publication_id": publication_id,
            },
        }

    @staticmethod
    def _text(payload: dict[str, Any]) -> str:
        direct = str(payload.get("text") or "").strip()
        if direct:
            return direct
        output = payload.get("output") if isinstance(payload.get("output"), dict) else {}
        sequence = output.get("sequence") if isinstance(output.get("sequence"), list) else []
        parts = [str(item.get("text") or "").strip() for item in sequence if isinstance(item, dict)]
        title = str(output.get("title") or payload.get("title") or "").strip()
        return "\n\n".join([value for value in ([title] + parts) if value])


class FakeTelegramDistributionAdapter:
    """Deterministic adapter used by automated tests; never contacts Telegram."""

    def __init__(self, destination: str = "fake-chat") -> None:
        self.destination = destination
        self.calls: list[dict[str, Any]] = []

    def prepare(self, payload: dict[str, Any]) -> dict[str, Any]:
        prepared = {
            "destination": self.destination,
            "text": TelegramDistributionAdapter._text(payload),
        }
        if not prepared["text"]:
            raise ValueError("Telegram publication requires non-empty text")
        return prepared

    def publish(self, payload: dict[str, Any], *, publication_id: str) -> dict[str, Any]:
        prepared = self.prepare(payload)
        self.calls.append({"publication_id": publication_id, "payload": payload, "prepared": prepared})
        return {
            "external_id": f"fake-message-{len(self.calls)}",
            "external_url": None,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "response": {
                "mode": "fake-telegram",
                "chat_id": prepared["destination"],
                "message_id": f"fake-message-{len(self.calls)}",
            },
        }
