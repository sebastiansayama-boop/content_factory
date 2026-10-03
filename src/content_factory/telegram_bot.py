from __future__ import annotations

import json
import mimetypes
import os
import threading
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any


class TelegramApi:
    """Small Bot API client used by the Content Factory webhook gateway."""

    def __init__(self, token: str, chat_id: str, *, timeout: float = 30.0) -> None:
        if not token.strip():
            raise ValueError("Telegram bot token is required")
        if not str(chat_id).strip():
            raise ValueError("Telegram chat id is required")
        self.token = token.strip()
        self.chat_id = str(chat_id).strip()
        self.timeout = timeout
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def _call(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self.base_url}/{method}",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        if not body.get("ok"):
            raise RuntimeError(f"Telegram {method} failed: {body}")
        return body.get("result") or {}

    def send_message(self, text: str, reply_markup: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"chat_id": self.chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self._call("sendMessage", payload)

    def edit_message_text(
        self,
        message_id: int,
        text: str,
        reply_markup: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "chat_id": self.chat_id,
            "message_id": int(message_id),
            "text": text,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        return self._call("editMessageText", payload)

    def answer_callback(self, callback_id: str, text: str = "") -> dict[str, Any]:
        return self._call(
            "answerCallbackQuery",
            {"callback_query_id": callback_id, "text": text},
        )

    def send_photo(
        self,
        path: Path,
        caption: str = "",
        reply_markup: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not path.is_file():
            raise ValueError(f"Telegram media file not found: {path}")
        boundary = f"----ContentFactory{uuid.uuid4().hex}"
        body = bytearray()

        def field(name: str, value: str) -> None:
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
            )
            body.extend(value.encode("utf-8"))
            body.extend(b"\r\n")

        field("chat_id", self.chat_id)
        if caption:
            field("caption", caption[:1024])
        if reply_markup is not None:
            field("reply_markup", json.dumps(reply_markup, ensure_ascii=False))
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(
            f'Content-Disposition: form-data; name="photo"; filename="{path.name}"\r\n'.encode()
        )
        body.extend(
            f"Content-Type: {mimetypes.guess_type(path.name)[0] or 'application/octet-stream'}\r\n\r\n".encode()
        )
        body.extend(path.read_bytes())
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode())

        request = urllib.request.Request(
            f"{self.base_url}/sendPhoto",
            data=bytes(body),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
        if not result.get("ok"):
            raise RuntimeError(f"Telegram sendPhoto failed: {result}")
        return result.get("result") or {}


class FactoryHttpClient:
    """Call the existing Product HTTP lifecycle; no duplicate business logic."""

    def __init__(self, base_url: str, api_token: str, *, timeout: float = 180.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token.strip()
        self.timeout = timeout

    def request(self, method: str, path: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                status = int(response.status)
                body = json.loads(response.read().decode("utf-8"))
                return status, body
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            try:
                body = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                body = {"error": raw.decode("utf-8", errors="replace")}
            return int(exc.code), body

    def create_run(self, topic: str) -> tuple[int, dict[str, Any]]:
        title = topic.splitlines()[0].strip()[:120] or "Telegram content"
        return self.request(
            "POST",
            "/api/runs",
            {
                "title": title,
                "brief": topic,
                "audience": "general audience",
                "goal": "evidence-grounded Telegram post",
                "formats": ["social_post"],
                "constraints": [
                    "platform: telegram",
                    "short",
                    "plain text",
                    "language: Русский",
                ],
            },
        )

    def factory(self, run_id: str) -> tuple[int, dict[str, Any]]:
        return self.request("POST", f"/api/runs/{run_id}/factory", {})

    def promote_claim(self, claim_id: str, decision_ref: str) -> tuple[int, dict[str, Any]]:
        return self.request(
            "POST",
            f"/api/knowledge/{claim_id}/promote",
            {"decision_ref": decision_ref},
        )

    def regenerate(
        self,
        run_id: str,
        instruction: str,
        *,
        visual_decision_id: str | None = None,
        visual_reason: str = "",
    ) -> tuple[int, dict[str, Any]]:
        payload: dict[str, Any] = {"instruction": instruction}
        if visual_decision_id:
            payload["visual_decision_id"] = visual_decision_id
        if visual_reason:
            payload["visual_reason"] = visual_reason
        return self.request(
            "POST",
            f"/api/runs/{run_id}/regenerate",
            payload,
        )

    def visual_feedback(
        self,
        decision_id: str,
        action: str,
        *,
        reason: str = "",
    ) -> tuple[int, dict[str, Any]]:
        return self.request(
            "POST",
            "/api/learning/visual/feedback",
            {
                "decision_id": decision_id,
                "action": action,
                "reason": reason,
                "source": "telegram",
            },
        )

    def approve(self, run_id: str, decision_ref: str) -> tuple[int, dict[str, Any]]:
        return self.request(
            "POST",
            f"/api/runs/{run_id}/approve",
            {"decision_ref": decision_ref, "channel": "telegram"},
        )

    def publish(self, run_id: str, publication_id: str) -> tuple[int, dict[str, Any]]:
        return self.request(
            "POST",
            f"/api/runs/{run_id}/publish",
            {"publication_id": publication_id},
        )


class TelegramFactoryBot:
    """Human-review UI for the main Content Factory lifecycle."""

    def __init__(
        self,
        *,
        telegram: TelegramApi,
        factory: FactoryHttpClient,
        allowed_chat_id: str,
    ) -> None:
        self.telegram = telegram
        self.factory = factory
        self.allowed_chat_id = str(allowed_chat_id).strip()
        self._lock = threading.RLock()
        self._preview_runs: dict[int, str] = {}
        self._knowledge_runs: dict[int, str] = {}
        self._pending_edit: dict[str, str] = {}
        self._seen_updates: set[int] = set()

    @staticmethod
    def _keyboard(rows: list[list[dict[str, str]]]) -> dict[str, Any]:
        for row in rows:
            for button in row:
                data = button.get("callback_data")
                if data and len(data.encode("utf-8")) > 64:
                    raise ValueError("Telegram callback_data exceeds 64 bytes")
        return {"inline_keyboard": rows}

    def handle_update(self, update: dict[str, Any]) -> None:
        update_id = update.get("update_id")
        if isinstance(update_id, int):
            with self._lock:
                if update_id in self._seen_updates:
                    return
                self._seen_updates.add(update_id)
                if len(self._seen_updates) > 2048:
                    self._seen_updates = set(sorted(self._seen_updates)[-1024:])

        callback = update.get("callback_query")
        if isinstance(callback, dict):
            self._handle_callback(callback)
            return

        message = update.get("message")
        if isinstance(message, dict):
            self._handle_message(message)

    def _chat_allowed(self, chat_id: Any) -> bool:
        return str(chat_id) == self.allowed_chat_id

    def _handle_message(self, message: dict[str, Any]) -> None:
        chat = message.get("chat") if isinstance(message.get("chat"), dict) else {}
        chat_id = str(chat.get("id") or "")
        if not self._chat_allowed(chat_id):
            return
        text = str(message.get("text") or "").strip()
        if not text:
            return

        if text in {"/start", "/help"}:
            self.telegram.send_message(
                "Content Factory.\n\n"
                "Напиши тему одним сообщением. Я подготовлю материал, покажу проверку знаний, "
                "затем дам preview с кнопками публикации, редактирования и перегенерации."
            )
            return

        with self._lock:
            pending_run_id = self._pending_edit.pop(chat_id, None)
        if pending_run_id:
            self._run_regeneration(
                pending_run_id,
                text,
                status_message="Обновляю материал по правке…",
            )
            return

        if text.startswith("/factory "):
            text = text[len("/factory ") :].strip()
        if not text:
            self.telegram.send_message("Напиши тему после /factory или просто отправь тему сообщением.")
            return

        self.telegram.send_message("Принял тему. Запускаю исследование и подготовку материала…")
        try:
            status, created = self.factory.create_run(text)
            if status != 201:
                raise RuntimeError(created.get("error") or f"create run returned HTTP {status}")
            run_id = str(created["run_id"])
            self._run_factory(run_id)
        except Exception as exc:
            self.telegram.send_message(f"Ошибка запуска: {str(exc)[:900]}")

    def _run_factory(self, run_id: str) -> None:
        status, result = self.factory.factory(run_id)
        if status == 409:
            candidates = result.get("candidates") or []
            if not candidates:
                raise RuntimeError("factory requested knowledge review but returned no candidates")
            lines = ["ПРОВЕРКА ЗНАНИЙ\n"]
            rows: list[list[dict[str, str]]] = []
            for index, candidate in enumerate(candidates[:5], 1):
                claim_id = str(candidate.get("claim_id") or "")
                claim_text = str(candidate.get("text") or "").strip()
                if not claim_id or not claim_text:
                    continue
                lines.append(f"{index}. {claim_text}")
                confidence = str(candidate.get("confidence") or "").strip()
                if confidence:
                    lines.append(f"   Уверенность: {confidence}")
                rows.append([{"text": f"Принять {index}", "callback_data": f"k:{claim_id}"}])
            lines.append("\nПрими утверждение, которое должно войти в финальный материал.")
            sent = self.telegram.send_message(
                "\n".join(lines),
                self._keyboard(rows),
            )
            message_id = int(sent.get("message_id") or 0)
            if message_id:
                with self._lock:
                    self._knowledge_runs[message_id] = run_id
            return
        if status != 200:
            raise RuntimeError(result.get("error") or f"factory returned HTTP {status}")
        self._send_preview(run_id, result.get("run") or {})

    def _send_preview(self, run_id: str, run: dict[str, Any]) -> None:
        payload = run.get("result") if isinstance(run.get("result"), dict) else {}
        package = payload.get("package") if isinstance(payload.get("package"), dict) else {}
        title = str(package.get("title") or run.get("title") or "").strip()
        text = str(package.get("text") or "").strip()
        media = package.get("media") if isinstance(package.get("media"), list) else []
        qc = package.get("qc") if isinstance(package.get("qc"), dict) else {}
        claims = package.get("claims") if isinstance(package.get("claims"), list) else []
        evidence = package.get("evidence") if isinstance(package.get("evidence"), list) else []

        preview = (
            "ГОТОВО К ПРОВЕРКЕ\n\n"
            f"{title}\n\n"
            f"{text}\n\n"
            f"Источники: {len(evidence)}\n"
            f"Проверенных утверждений: {len(claims)}\n"
            f"Изображений: {len(media)}\n"
            f"QC: {str(qc.get('status') or 'UNKNOWN')}."
        )
        sent = self.telegram.send_message(
            preview[:4096],
            self._keyboard(
                [
                    [{"text": "✓ Опубликовать", "callback_data": f"p:{run_id}"}],
                    [
                        {"text": "✎ Редактировать", "callback_data": f"e:{run_id}"},
                        {"text": "↻ Перегенерировать", "callback_data": f"g:{run_id}"},
                    ],
                ]
            ),
        )
        message_id = int(sent.get("message_id") or 0)
        if message_id:
            with self._lock:
                self._preview_runs[message_id] = run_id

        for index, item in enumerate(media[:10], 1):
            if not isinstance(item, dict):
                continue
            uri = str(item.get("uri") or "").strip()
            if not uri:
                continue
            decision_id = str(item.get("visual_decision_id") or "").strip()
            caption = f"Изображение {index}"
            reply_markup = None
            if decision_id:
                reply_markup = self._keyboard(
                    [[
                        {
                            "text": "✓ Подходит",
                            "callback_data": f"va:{decision_id}:A",
                        },
                        {
                            "text": "✕ Не подходит",
                            "callback_data": f"va:{decision_id}:R",
                        },
                    ]]
                )
            try:
                self.telegram.send_photo(
                    Path(uri),
                    caption=caption,
                    reply_markup=reply_markup,
                )
            except Exception:
                self.telegram.send_message(
                    f"Не удалось отправить изображение {index} preview."
                )

    def _handle_callback(self, callback: dict[str, Any]) -> None:
        message = callback.get("message") if isinstance(callback.get("message"), dict) else {}
        chat = message.get("chat") if isinstance(message.get("chat"), dict) else {}
        chat_id = str(chat.get("id") or "")
        if not self._chat_allowed(chat_id):
            return

        callback_id = str(callback.get("id") or "")
        data = str(callback.get("data") or "")
        message_id = int(message.get("message_id") or 0)

        try:
            self.telegram.answer_callback(callback_id)
        except Exception:
            pass

        try:
            action, _, value = data.partition(":")
            if action == "va":
                parts = data.split(":", 2)
                if len(parts) != 3:
                    raise ValueError("visual feedback callback is malformed")
                decision_id = parts[1].strip()
                visual_action = {"A": "ACCEPT", "R": "REJECT"}.get(parts[2].strip().upper())
                if not decision_id or visual_action is None:
                    raise ValueError("visual feedback callback is invalid")
                self._handle_visual_feedback(
                    decision_id,
                    visual_action,
                    run_id_hint=self._preview_runs.get(message_id),
                )
            elif action == "k":
                run_id = self._knowledge_run(message_id)
                self._accept_claim(run_id, value)
            elif action == "p":
                self._publish(value, message_id)
            elif action == "e":
                with self._lock:
                    self._pending_edit[chat_id] = value
                self.telegram.send_message(
                    "Напиши правку одним сообщением. Например: «Сделай короче и менее академично»."
                )
            elif action == "g":
                self._run_regeneration(
                    value,
                    "Создай новую версию с другим углом, сохранив полезные проверенные факты.",
                    status_message="Перегенерирую материал…",
                )
            else:
                self.telegram.send_message("Неизвестное действие.")
        except Exception as exc:
            self.telegram.send_message(f"Действие не выполнено: {str(exc)[:900]}")

    def _handle_visual_feedback(
        self,
        decision_id: str,
        action: str,
        *,
        run_id_hint: str | None = None,
    ) -> None:
        reason = (
            "human accepted visual candidate in Telegram"
            if action == "ACCEPT"
            else "human rejected visual candidate in Telegram"
        )
        status, feedback = self.factory.visual_feedback(
            decision_id,
            action,
            reason=reason,
        )
        if status != 201:
            raise RuntimeError(
                feedback.get("error")
                or f"visual feedback returned HTTP {status}"
            )
        run_id = str(feedback.get("run_id") or run_id_hint or "").strip()
        if not run_id:
            raise RuntimeError("visual feedback returned no source run id")

        if action == "ACCEPT":
            self.telegram.send_message("Изображение принято.")
            return

        self.telegram.send_message("Изображение отклонено. Заменяю его и запускаю повторную проверку…")
        instruction = (
            "Замени отклонённое изображение новым визуально релевантным вариантом. "
            "Сохрани текст и проверенные факты. Не возвращай прежнее изображение. "
            f"Предыдущее визуальное решение: {decision_id}."
        )
        status, regenerated = self.factory.regenerate(
            run_id,
            instruction,
            visual_decision_id=decision_id,
            visual_reason=reason,
        )
        if status != 201:
            raise RuntimeError(
                regenerated.get("error")
                or f"regenerate returned HTTP {status}"
            )
        new_run_id = str((regenerated.get("run") or {}).get("run_id") or "").strip()
        if not new_run_id:
            raise RuntimeError("visual regeneration returned no new run id")
        self.telegram.send_message("Новый вариант готов. Проверяй изображение повторно.")
        self._run_factory(new_run_id)

    def _knowledge_run(self, message_id: int) -> str:
        with self._lock:
            run_id = self._knowledge_runs.get(message_id)
        if not run_id:
            raise RuntimeError("review message is no longer associated with a run")
        return run_id

    def _accept_claim(self, run_id: str, claim_id: str) -> None:
        if not claim_id:
            raise ValueError("claim id is missing")
        status, promoted = self.factory.promote_claim(
            claim_id,
            decision_ref=f"telegram:{self.allowed_chat_id}:{run_id}",
        )
        if status != 200 or promoted.get("status") != "ACCEPTED":
            raise RuntimeError(promoted.get("error") or f"claim promotion returned HTTP {status}")
        self.telegram.send_message("Утверждение принято. Продолжаю производство…")
        self._run_factory(run_id)

    def _run_regeneration(self, run_id: str, instruction: str, *, status_message: str) -> None:
        self.telegram.send_message(status_message)
        status, result = self.factory.regenerate(run_id, instruction)
        if status != 201:
            raise RuntimeError(result.get("error") or f"regenerate returned HTTP {status}")
        new_run_id = str((result.get("run") or {}).get("run_id") or "")
        if not new_run_id:
            raise RuntimeError("regenerate returned no new run id")
        self._run_factory(new_run_id)

    def _publish(self, run_id: str, message_id: int) -> None:
        decision_ref = f"telegram:{self.allowed_chat_id}:{message_id}"
        status, approved = self.factory.approve(run_id, decision_ref)
        if status != 200:
            raise RuntimeError(approved.get("error") or f"approve returned HTTP {status}")
        publication = approved.get("result", {}).get("publication")
        if not isinstance(publication, dict):
            raise RuntimeError("approve returned no publication")
        publication_id = str(publication.get("publication_id") or "")
        if not publication_id:
            raise RuntimeError("approved publication has no publication id")
        status, published = self.factory.publish(run_id, publication_id)
        if status != 200:
            raise RuntimeError(published.get("error") or f"publish returned HTTP {status}")
        external_url = str(published.get("external_url") or "").strip()
        confirmation = "Опубликовано."
        if external_url:
            confirmation += f"\n{external_url}"
        self.telegram.edit_message_text(message_id, confirmation)
        with self._lock:
            self._preview_runs.pop(message_id, None)
            self._pending_edit.pop(self.allowed_chat_id, None)
