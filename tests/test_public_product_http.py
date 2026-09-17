from content_factory.product_http import ProductHandler


class DummyProductHandler(ProductHandler):
    def __init__(self):
        self.headers = {}
        self.client_address = ("127.0.0.1", 12345)


def test_public_beta_access_is_explicit(monkeypatch):
    handler = DummyProductHandler()
    monkeypatch.setenv("FACTORY_PUBLIC_BETA", "true")
    assert handler._product_access_allowed() is True


def test_private_product_still_requires_token(monkeypatch):
    handler = DummyProductHandler()
    monkeypatch.delenv("FACTORY_PUBLIC_BETA", raising=False)
    monkeypatch.delenv("FACTORY_API_TOKEN", raising=False)
    assert handler._product_access_allowed() is False
