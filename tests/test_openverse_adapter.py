import json

from content_factory.openverse_adapter import OpenverseImageProvider


class _Response:
    status = 200

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


def test_openverse_normalizes_image_candidates():
    provider = OpenverseImageProvider(
        opener=lambda request, timeout: _Response({
            "results": [{
                "id": "123",
                "url": "https://example.test/image.jpg",
                "thumbnail": "https://example.test/thumb.jpg",
                "title": "Example",
                "creator": "Author",
                "license": "cc-by",
            }]
        })
    )
    result = provider.search("evolution", limit=1)
    assert len(result) == 1
    assert result[0].source == "openverse"
    assert result[0].url.endswith("image.jpg")
