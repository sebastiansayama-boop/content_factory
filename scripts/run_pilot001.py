from __future__ import annotations

import json
import os
import time
from pathlib import Path

from content_factory.telegram_pilot import Pilot001Controller, TelegramBot, keyboard, preview_text


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    token = _required("TELEGRAM_BOT_TOKEN")
    chat_id = _required("TELEGRAM_CHAT_ID")
    controller = Pilot001Controller()
    bot = TelegramBot(token, chat_id)
    bot.send_message(
        "Content Factory Pilot001 online.\n\n"
        "Send /pilot <direction> to generate a researched post + carousel.\n"
        "Buttons: Approve / Regenerate / Reject.\n"
        "Approval stops at the human publication boundary: you publish manually."
    )

    offset: int | None = None
    while True:
        try:
            for update in bot.get_updates(offset):
                offset = int(update["update_id"]) + 1
                message = update.get("message")
                if message:
                    chat = message.get("chat", {})
                    if str(chat.get("id")) != chat_id:
                        continue
                    text = str(message.get("text") or "").strip()
                    if text.startswith("/pilot "):
                        direction = text[len("/pilot ") :].strip()
                        if not direction:
                            bot.send_message("Usage: /pilot <direction>")
                            continue
                        bot.send_message(f"Researching and producing: {direction}\nThis can take a while on a local model...")
                        try:
                            draft, _, images = controller.create(direction)
                            research_payload = json.loads(
                                (controller.draft_root / f"{draft.draft_id}.json").read_text(encoding="utf-8")
                            )["research"]
                            bot.send_message(preview_text(draft, research_payload), keyboard(draft.draft_id))
                            for index, image in enumerate(images, 1):
                                caption = f"Slide {index}/{len(images)}"
                                bot.send_photo(image, caption)
                        except Exception as exc:
                            bot.send_message(f"Pilot001 failed: {exc}")
                    elif text in {"/start", "/help"}:
                        bot.send_message("Use /pilot <direction>. Example: /pilot AI agents for small businesses")
                callback = update.get("callback_query")
                if callback:
                    callback_id = callback["id"]
                    data = str(callback.get("data") or "")
                    bot.answer_callback(callback_id)
                    action, _, draft_id = data.partition(":")
                    if not draft_id:
                        continue
                    try:
                        draft, research = controller._load_for_action(draft_id) if hasattr(controller, "_load_for_action") else (None, None)
                        if action == "approve":
                            path = controller.draft_root / f"{draft_id}.json"
                            payload = json.loads(path.read_text(encoding="utf-8"))
                            payload["draft"]["status"] = "APPROVED"
                            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                            bot.send_message(
                                f"APPROVED: {draft_id}\n\nManual publication boundary reached.\nPublish the approved post manually to Instagram / Threads."
                            )
                        elif action == "reject":
                            path = controller.draft_root / f"{draft_id}.json"
                            payload = json.loads(path.read_text(encoding="utf-8"))
                            payload["draft"]["status"] = "REJECTED"
                            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                            bot.send_message(f"REJECTED: {draft_id}")
                        elif action == "regen":
                            bot.send_message("Regenerating with a new angle...")
                            new_draft, _, images = controller.regenerate(draft_id)
                            research_payload = json.loads(
                                (controller.draft_root / f"{new_draft.draft_id}.json").read_text(encoding="utf-8")
                            )["research"]
                            bot.send_message(preview_text(new_draft, research_payload), keyboard(new_draft.draft_id))
                            for index, image in enumerate(images, 1):
                                bot.send_photo(image, f"Slide {index}/{len(images)}")
                    except Exception as exc:
                        bot.send_message(f"Action failed: {exc}")
        except KeyboardInterrupt:
            bot.send_message("Pilot001 stopped.")
            return 0
        except Exception as exc:
            print(f"Pilot001 loop error: {exc}")
            time.sleep(3)


if __name__ == "__main__":
    raise SystemExit(main())
