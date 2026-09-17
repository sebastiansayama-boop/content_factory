from content_factory.product_http import ProductHandler


class DummyProductHandler(ProductHandler):
    def __init__(self, path="/"):
        self.path = path
        self.headers = {}
        self.status = None
        self.response_headers = {}
        self.wfile = type("Writer", (), {"write": lambda self, data: setattr(self, "data", data)})()

    def send_response(self, status):
        self.status = status

    def send_header(self, name, value):
        self.response_headers[name] = value

    def end_headers(self):
        pass

    def _json(self, status, body, retry_after=None):
        self.status = status


def test_product_root_serves_index_html():
    handler = DummyProductHandler("/")
    ProductHandler.do_GET(handler)

    assert handler.status == 200
    assert handler.response_headers["Content-Type"] == "text/html; charset=utf-8"
    assert int(handler.response_headers["Content-Length"]) > 0
    assert b"Content Factory" in handler.wfile.data


def test_product_index_alias_serves_index_html():
    handler = DummyProductHandler("/index.html")
    ProductHandler.do_GET(handler)

    assert handler.status == 200
    assert b"Content Factory" in handler.wfile.data
