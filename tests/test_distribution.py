from content_factory.distribution import FakeTelegramDistributionAdapter, TelegramDistributionAdapter


def test_fake_telegram_adapter_prepares_and_publishes_without_network():
    adapter = FakeTelegramDistributionAdapter("chat-123")
    payload = {
        "title": "Test title",
        "output": {
            "title": "Test title",
            "sequence": [{"text": "First claim."}, {"text": "Second claim."}],
        },
    }

    prepared = adapter.prepare(payload)
    assert prepared["destination"] == "chat-123"
    assert "First claim." in prepared["text"]

    result = adapter.publish(payload, publication_id="pub-1")
    assert result["external_id"] == "fake-message-1"
    assert result["external_url"] is None
    assert result["response"]["mode"] == "fake-telegram"
    assert len(adapter.calls) == 1


def test_telegram_adapter_rejects_empty_message():
    try:
        TelegramDistributionAdapter._text({})
    except Exception as exc:
        raise AssertionError(exc)
    assert TelegramDistributionAdapter._text({}) == ""


def test_telegram_message_url_for_public_channel():
    adapter = TelegramDistributionAdapter("token", "@AtlasOpenLab")
    assert adapter._message_url("42") == "https://t.me/AtlasOpenLab/42"


def test_telegram_message_url_for_private_supergroup_or_channel():
    adapter = TelegramDistributionAdapter("token", "-1001234567890")
    assert adapter._message_url("42") == "https://t.me/c/1234567890/42"
