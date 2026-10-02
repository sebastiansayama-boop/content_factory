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


def test_telegram_adapter_can_publish_a_local_photo(monkeypatch, tmp_path):
    image = tmp_path / "hero.jpg"
    image.write_bytes(b"fake-jpeg")
    calls = []

    class Response:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return b'{"ok":true,"result":{"message_id":42,"caption":"Caption"}}'

    def fake_urlopen(request, timeout=30):
        calls.append(request)
        return Response()

    monkeypatch.setattr("content_factory.distribution.urllib.request.urlopen", fake_urlopen)
    adapter = TelegramDistributionAdapter("token", "@example")
    result = adapter.publish(
        {
            "text": "Caption",
            "media": [{"media_id": "asset-1", "type": "image", "origin": "openverse", "uri": str(image), "license": "cc-by"}],
        },
        publication_id="pub-media-1",
    )
    assert result["external_id"] == "42"
    assert result["response"]["media_count"] == 1
    assert result["response"]["media"][0]["origin"] == "openverse"
    assert calls and b"fake-jpeg" in calls[0].data
    assert b"sendPhoto" not in calls[0].data


def test_telegram_adapter_publishes_multiple_photos_as_one_album(monkeypatch, tmp_path):
    images = []
    for index in range(4):
        path = tmp_path / f"image-{index}.jpg"
        path.write_bytes(f"fake-jpeg-{index}".encode())
        images.append({"media_id": f"asset-{index}", "type": "image", "origin": "openverse", "uri": str(path), "license": "cc-by"})
    calls = []

    class Response:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return b'{"ok":true,"result":[{"message_id":42,"caption":"Caption"},{"message_id":43},{"message_id":44},{"message_id":45}]}'

    def fake_urlopen(request, timeout=30):
        calls.append(request)
        return Response()

    monkeypatch.setattr("content_factory.distribution.urllib.request.urlopen", fake_urlopen)
    adapter = TelegramDistributionAdapter("token", "@example")
    result = adapter.publish({"text": "Caption", "media": images}, publication_id="pub-album-1")

    assert result["external_id"] == "42"
    assert result["response"]["media_count"] == 4
    assert len(calls) == 1
    assert b'"caption": "Caption"' in calls[0].data
    assert b"image-0.jpg" in calls[0].data
    assert b"image-3.jpg" in calls[0].data
