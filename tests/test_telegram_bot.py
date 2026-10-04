import json
from pathlib import Path

from content_factory.telegram_bot import TelegramFactoryBot


class FakeTelegram:
    def __init__(self):
        self.sent = []
        self.edited = []
        self.answered = []

    def send_message(self, text, reply_markup=None):
        message_id = len(self.sent) + 1
        self.sent.append({"message_id": message_id, "text": text, "reply_markup": reply_markup})
        return {"message_id": message_id}

    def edit_message_text(self, message_id, text, reply_markup=None):
        self.edited.append({"message_id": message_id, "text": text, "reply_markup": reply_markup})
        return {"message_id": message_id, "text": text}

    def answer_callback(self, callback_id, text=""):
        self.answered.append({"id": callback_id, "text": text})
        return {}

    def send_photo(self, path: Path, caption=""):
        self.sent.append({"photo": str(path), "caption": caption})
        return {"message_id": len(self.sent)}


class FakeFactory:
    def __init__(self):
        self.promoted = []
        self.approved = []
        self.published = []
        self.regenerated = []
        self.phase = {}

    def create_run(self, topic):
        return 201, {"run_id": "run-1", "title": topic}

    def factory(self, run_id):
        if self.phase.get(run_id) != "ready":
            self.phase[run_id] = "ready"
            return 409, {
                "candidates": [
                    {
                        "claim_id": "claim-1",
                        "text": "Проверенное утверждение.",
                        "confidence": "high",
                    }
                ]
            }
        return 200, {
            "run": {
                "run_id": run_id,
                "title": "Тестовый материал",
                "result": {
                    "package": {
                        "title": "Тестовый материал",
                        "text": "Готовый текст.",
                        "media": [],
                        "claims": [{"claim_id": "claim-1"}],
                        "evidence": [{"source_id": "source-1"}],
                        "qc": {"status": "PASSED"},
                    }
                },
            }
        }

    def promote_claim(self, claim_id, decision_ref):
        self.promoted.append((claim_id, decision_ref))
        return 200, {"claim_id": claim_id, "status": "ACCEPTED"}

    def regenerate(self, run_id, instruction):
        self.regenerated.append((run_id, instruction))
        return 201, {"run": {"run_id": "run-2"}}

    def approve(self, run_id, decision_ref):
        self.approved.append((run_id, decision_ref))
        return 200, {
            "result": {
                "publication": {
                    "publication_id": "pub-1",
                    "status": "PREPARED",
                    "channel": "telegram",
                }
            }
        }

    def publish(self, run_id, publication_id, actor_id):
        self.published.append((run_id, publication_id))
        return 200, {
            "external_url": "https://t.me/example/1",
            "status": "PUBLISHED",
        }


def _update_message(text, update_id=1, message_id=1):
    return {
        "update_id": update_id,
        "message": {
            "message_id": message_id,
            "chat": {"id": "123"},
            "text": text,
        },
    }


def _callback(data, update_id=2, message_id=1):
    return {
        "update_id": update_id,
        "callback_query": {
            "id": f"cb-{update_id}",
            "data": data,
            "message": {
                "message_id": message_id,
                "chat": {"id": "123"},
            },
        },
    }


def test_bot_routes_topic_through_knowledge_review_to_preview():
    telegram = FakeTelegram()
    factory = FakeFactory()
    bot = TelegramFactoryBot(
        telegram=telegram,
        factory=factory,
        allowed_chat_id="123",
    )

    bot.handle_update(_update_message("Как люди представляли будущее?"))
    review = telegram.sent[-1]

    assert "ПРОВЕРКА ЗНАНИЙ" in review["text"]
    assert review["reply_markup"]["inline_keyboard"][0][0]["callback_data"] == "k:claim-1"

    bot.handle_update(_callback("k:claim-1", update_id=2, message_id=review["message_id"]))

    preview = telegram.sent[-1]
    assert "ГОТОВО К ПРОВЕРКЕ" in preview["text"]
    callback_data = {
        button["callback_data"]
        for row in preview["reply_markup"]["inline_keyboard"]
        for button in row
    }
    assert f"p:run-1" in callback_data
    assert f"e:run-1" in callback_data
    assert f"g:run-1" in callback_data


def test_edit_button_turns_next_message_into_regeneration():
    telegram = FakeTelegram()
    factory = FakeFactory()
    bot = TelegramFactoryBot(
        telegram=telegram,
        factory=factory,
        allowed_chat_id="123",
    )

    bot.handle_update(_update_message("Тема", update_id=10))
    review = telegram.sent[-1]
    bot.handle_update(_callback("k:claim-1", update_id=11, message_id=review["message_id"]))
    preview = telegram.sent[-1]

    bot.handle_update(_callback("e:run-1", update_id=12, message_id=preview["message_id"]))
    bot.handle_update(_update_message("Сделай текст короче.", update_id=13))

    assert factory.regenerated == [("run-1", "Сделай текст короче.")]
    assert any("ГОТОВО К ПРОВЕРКЕ" in item["text"] for item in telegram.sent if "text" in item)


def test_publish_button_uses_main_approval_and_publication_lifecycle():
    telegram = FakeTelegram()
    factory = FakeFactory()
    bot = TelegramFactoryBot(
        telegram=telegram,
        factory=factory,
        allowed_chat_id="123",
    )

    bot.handle_update(_update_message("Тема", update_id=20))
    review = telegram.sent[-1]
    bot.handle_update(_callback("k:claim-1", update_id=21, message_id=review["message_id"]))
    preview = telegram.sent[-1]

    bot.handle_update(_callback("p:run-1", update_id=22, message_id=preview["message_id"]))

    assert factory.approved == [("run-1", f"telegram:123:{preview['message_id']}")]
    assert factory.published == [("run-1", "pub-1")]
    assert telegram.edited[-1]["text"].startswith("Опубликовано.")


def test_callback_data_stays_within_telegram_limit():
    telegram = FakeTelegram()
    factory = FakeFactory()
    bot = TelegramFactoryBot(
        telegram=telegram,
        factory=factory,
        allowed_chat_id="123",
    )
    keyboard = bot._keyboard(
        [[{"text": "Publish", "callback_data": "p:" + "x" * 50}]]
    )
    raw = keyboard["inline_keyboard"][0][0]["callback_data"]
    assert len(raw.encode("utf-8")) <= 64
