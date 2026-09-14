from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

from .pilot001 import Draft, OllamaClient, ResearchEngine, load_draft, render_carousel, save_draft


class TelegramBot:
    def __init__(self, token: str, chat_id: str, *, timeout: float = 30.0) -> None:
        self.token = token
        self.chat_id = str(chat_id)
        self.timeout = timeout
        self.base = f"https://api.telegram.org/bot{token}"

    def _call(self, method: str, payload: dict) -> dict:
        request = urllib.request.Request(
            f"{self.base}/{method}",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        if not body.get("ok"):
            raise RuntimeError(f"Telegram {method} failed: {body}")
        return body["result"]

    def send_message(self, text: str, reply_markup: dict | None = None) -> dict:
        payload = {"chat_id": self.chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self._call("sendMessage", payload)

    def send_photo(self, path: Path, caption: str = "") -> dict:
        boundary = f"----ContentFactory{int(time.time() * 1000)}"
        body = bytearray()

        def field(name: str, value: str) -> None:
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
            body.extend(value.encode("utf-8"))
            body.extend(b"\r\n")

        field("chat_id", self.chat_id)
        if caption:
            field("caption", caption[:1024])
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="photo"; filename="{path.name}"\r\n'.encode())
        body.extend(b"Content-Type: image/png\r\n\r\n")
        body.extend(path.read_bytes())
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode())

        request = urllib.request.Request(
            f"{self.base}/sendPhoto",
            data=bytes(body),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
        if not result.get("ok"):
            raise RuntimeError(f"Telegram sendPhoto failed: {result}")
        return result["result"]

    def answer_callback(self, callback_id: str, text: str = "") -> None:
        self._call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text})

    def get_updates(self, offset: int | None = None) -> list[dict]:
        payload = {"timeout": 25, "allowed_updates": ["message", "callback_query"]}
        if offset is not None:
            payload["offset"] = offset
        return self._call("getUpdates", payload)


class Pilot001Controller:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(os.getenv("FACTORY_DATA_DIR", "./data")) / "pilot001"
        self.draft_root = self.root / "drafts"
        self.asset_root = self.root / "assets"
        self.research = ResearchEngine()
        self.model = OllamaClient()

    def create(self, direction: str, *, revision: int = 1, edit_instruction: str = "") -> tuple[Draft, Path, list[Path]]:
        research = self.research.collect(direction)
        if not research:
            raise RuntimeError("research returned no usable items")
        draft = self.model.generate(
            direction=direction,
            research=research,
            revision=revision,
            edit_instruction=edit_instruction,
        )
        draft_dir = self.asset_root / draft.draft_id
        images = render_carousel(draft, draft_dir)
        save_draft(self.draft_root, draft, research)
        return draft, draft_dir, images

    def regenerate(self, draft_id: str, instruction: str = "") -> tuple[Draft, Path, list[Path]]:
        previous, research = load_draft(self.draft_root, draft_id)
        draft = self.model.generate(
            direction=previous.direction,
            research=research,
            revision=previous.revision + 1,
            edit_instruction=instruction or "make a meaningfully different angle while preserving the useful signal",
        )
        draft_dir = self.asset_root / draft.draft_id
        images = render_carousel(draft, draft_dir)
        save_draft(self.draft_root, draft, research)
        return draft, draft_dir, images


def preview_text(draft: Draft, research: list | None = None) -> str:
    source_note = ""
    if research:
        used = [research[i].source for i in draft.research_used if 0 <= i < len(research)]
        source_note = "\nSources: " + ", ".join(dict.fromkeys(used))
    return (
        f"PILOT001 · {draft.status}\n\n"
        f"Direction: {draft.direction}\n"
        f"Angle: {draft.angle}\n"
        f"Why now: {draft.why_now}\n\n"
        f"POST\n{draft.post_text}\n\n"
        f"Carousel: {len(draft.carousel_slides)} slides\n"
        f"Draft: {draft.draft_id} · revision {draft.revision}"
        f"{source_note}"
    )


def keyboard(draft_id: str) -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "✓ Approve", "callback_data": f"approve:{draft_id}"},
                {"text": "↻ Regenerate", "callback_data": f"regen:{draft_id}"},
            ],
            [{"text": "✕ Reject", "callback_data": f"reject:{draft_id}"}],
        ]
    }
