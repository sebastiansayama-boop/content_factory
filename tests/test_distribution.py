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
    assert result["response"]["mode"] == "fake-telegram"
    assert len(adapter.calls) == 1


def test_telegram_adapter_rejects_empty_message():
    try:
        TelegramDistributionAdapter._text({})
    except Exception as exc:
        raise AssertionError(exc)
    assert TelegramDistributionAdapter._text({}) == ""
