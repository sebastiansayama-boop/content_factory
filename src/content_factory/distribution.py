from __future__ import annotations

import json
import mimetypes
import os
import urllib.request
import uuid
from datetime import datetime, timezone
from typing import Any
from pathlib import Path


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
        media = payload.get("media")
        if isinstance(media, list):
            media = [item for item in media if isinstance(item, dict) and str(item.get("uri") or "").strip()]
        else:
            media = []
        if media:
            return self._publish_with_media(prepared, media, publication_id)
        body = self._api_json("sendMessage", {
            "chat_id": prepared["destination"],
            "text": prepared["text"],
        })
        message = body.get("result") or {}
        if message.get("message_id") is None and isinstance(message, list) and message:
            message = message[0]
        message_id = str(message.get("message_id") or "").strip()
        if not message_id:
            raise ValueError("Telegram response has no message_id")
        return {
            "external_id": message_id,
            "external_url": self._message_url(message_id),
            "published_at": datetime.now(timezone.utc).isoformat(),
            "response": {
                "mode": "telegram",
                "chat_id": prepared["destination"],
                "message_id": int(message_id),
                "telegram_ok": True,
                "text": str(message.get("text") or prepared["text"]),
                "publication_id": publication_id,
                "media_count": 0,
            },
        }

    def _publish_with_media(self, prepared: dict[str, Any], media: list[dict[str, Any]], publication_id: str) -> dict[str, Any]:
        first = media[0]
        first_path = Path(str(first["uri"]))
        if not first_path.is_file():
            raise ValueError(f"Telegram media file not found: {first_path}")
        def photo_file(path: Path) -> tuple[str, bytes, str]:
            return (path.name, path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        if len(media) > 1:
            if len(prepared["text"]) <= 1024:
                self._send_album(
                    prepared["destination"],
                    media[:10],
                    caption=prepared["text"],
                )
                message = {
                    "message_id": None,
                    "caption": prepared["text"],
                }
            else:
                text_body = self._api_json("sendMessage", {"chat_id": prepared["destination"], "text": prepared["text"]})
                self._send_album(prepared["destination"], media[:10])
                message = text_body.get("result") or {}
        elif len(prepared["text"]) <= 1024:
            body = self._multipart("sendPhoto", {"chat_id": prepared["destination"], "caption": prepared["text"]}, {"photo": photo_file(first_path)})
            message = body.get("result") or {}
        else:
            text_body = self._api_json("sendMessage", {"chat_id": prepared["destination"], "text": prepared["text"]})
            self._multipart("sendPhoto", {"chat_id": prepared["destination"]}, {"photo": photo_file(first_path)})
            message = text_body.get("result") or {}
        message_id = str(message.get("message_id") or "").strip()
        if not message_id:
            raise ValueError("Telegram media publication returned no message_id")
        return {
            "external_id": message_id,
            "external_url": self._message_url(message_id),
            "published_at": datetime.now(timezone.utc).isoformat(),
            "response": {
                "mode": "telegram",
                "chat_id": prepared["destination"],
                "message_id": int(message_id),
                "telegram_ok": True,
                "text": str(message.get("caption") or message.get("text") or prepared["text"]),
                "publication_id": publication_id,
                "media_count": len(media),
                "media": [
                    {
                        "media_id": str(item.get("media_id") or ""),
                        "origin": str(item.get("origin") or ""),
                        "source": item.get("source"),
                        "license": item.get("license"),
                        "uri": str(item.get("uri") or ""),
                    }
                    for item in media[:10]
                ],
            },
        }

    def _send_album(self, destination: str, media: list[dict[str, Any]], *, caption: str | None = None) -> dict[str, Any]:
        files: dict[str, tuple[str, bytes, str]] = {}
        items = []
        for index, item in enumerate(media[:10]):
            path = Path(str(item["uri"]))
            if not path.is_file():
                raise ValueError(f"Telegram media file not found: {path}")
            field = f"photo{index}"
            files[field] = (path.name, path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            item_payload = {"type": "photo", "media": f"attach://{field}"}
            if index == 0 and caption:
                item_payload["caption"] = caption
            items.append(item_payload)
        return self._multipart("sendMediaGroup", {
            "chat_id": destination,
            "media": json.dumps(items, ensure_ascii=False),
        }, files)

    def _api_json(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self.base_url}/{method}",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        if not body.get("ok"):
            raise ValueError(f"Telegram {method} failed: {body}")
        return body

    def _multipart(self, method: str, fields: dict[str, str], files: dict[str, tuple[str, bytes, str]]) -> dict[str, Any]:
        boundary = f"----ContentFactory{uuid.uuid4().hex}"
        chunks: list[bytes] = []
        for name, value in fields.items():
            chunks.extend([
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                str(value).encode("utf-8"),
                b"\r\n",
            ])
        for name, (filename, data, content_type) in files.items():
            chunks.extend([
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode(),
                f"Content-Type: {content_type}\r\n\r\n".encode(),
                data,
                b"\r\n",
            ])
        chunks.append(f"--{boundary}--\r\n".encode())
        request = urllib.request.Request(
            f"{self.base_url}/{method}",
            data=b"".join(chunks),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        if not body.get("ok"):
            raise ValueError(f"Telegram {method} failed: {body}")
        return body

    def _message_url(self, message_id: str) -> str | None:
        chat = self.chat_id.strip()
        if chat.startswith("@") and len(chat) > 1:
            return f"https://t.me/{chat[1:]}/{message_id}"
        if chat.startswith("https://t.me/"):
            username = chat.removeprefix("https://t.me/").strip("/").split("/", 1)[0]
            if username:
                return f"https://t.me/{username}/{message_id}"
        if chat.startswith("-100"):
            return f"https://t.me/c/{chat[4:]}/{message_id}"
        return None

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
