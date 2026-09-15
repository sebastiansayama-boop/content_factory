import io
import os

import pytest

from content_factory.service import Handler


class DummyService:
    def health(self):
        return {"status": "ok"}

    def run(self, payload):
        return {"state": "OBSERVED", "payload": payload}


class DummyHandler(Handler):
    def __init__(self, headers=None, body=b"{}", client_ip="127.0.0.1"):
        self.headers = headers or {}
        self.rfile = io.BytesIO(body)
        self.wfile = io.BytesIO()
        self.client_address = (client_ip, 12345)
        self.path = "/run"
        self.status = None
        self.response_headers = {}

    def send_response(self, status):
        self.status = status

    def send_header(self, name, value):
        self.response_headers[name] = value

    def end_headers(self):
        pass

    def _json(self, status, body, retry_after=None):
        self.status = status
        self.response_headers = {"Content-Type": "application/json"}
        if retry_after is not None:
            self.response_headers["Retry-After"] = str(retry_after)
        self.wfile.write(str(body).encode())


@pytest.fixture(autouse=True)
def reset_handler_state(monkeypatch):
    Handler._authorized_requests.clear()
    Handler._auth_failures.clear()
    monkeypatch.setenv("FACTORY_API_TOKEN", "a" * 32)
    monkeypatch.setenv("FACTORY_ACCEPTANCE_AUTHORITY", "accept-authority")
    monkeypatch.setenv("FACTORY_RELEASE_AUTHORITY", "release-authority")


def test_authorization_uses_constant_time_compare(monkeypatch):
    handler = DummyHandler({"Authorization": "Bearer " + "a" * 32})
    assert handler._authorized() is True

    handler.headers = {"Authorization": "Bearer " + "a" * 31 + "b"}
    assert handler._authorized() is False


def test_run_rejects_oversized_body():
    body = b"{" + b"a" * (64 * 1024) + b"}"
    handler = DummyHandler({"Authorization": "Bearer " + "a" * 32}, body=body)
    handler.service = DummyService()
    handler.do_POST()
    assert handler.status == 400


def test_run_rate_limits_authorized_requests():
    headers = {"Authorization": "Bearer " + "a" * 32}
    for _ in range(10):
        handler = DummyHandler(headers)
        handler.service = DummyService()
        handler.do_POST()
        assert handler.status == 200

    handler = DummyHandler(headers)
    handler.service = DummyService()
    handler.do_POST()
    assert handler.status == 429
    assert handler.response_headers["Retry-After"] == "60"


def test_auth_failures_are_rate_limited():
    headers = {"Authorization": "Bearer wrong"}
    for _ in range(20):
        handler = DummyHandler(headers)
        handler.service = DummyService()
        handler.do_POST()
        assert handler.status == 401

    handler = DummyHandler(headers)
    handler.service = DummyService()
    handler.do_POST()
    assert handler.status == 429


def test_authority_policy_is_server_configured(monkeypatch):
    from content_factory.service import FactoryService

    service = object.__new__(FactoryService)
    service._acceptance_authority = "accept-authority"
    service._release_authority = "release-authority"
    service._capability = type("Capability", (), {"capability_id": "test.capability"})()

    payload = {
        "requested_outcome": "hello",
        "acceptance_authority": "attacker-supplied",
        "release_authority": "release-authority",
    }
    with pytest.raises(ValueError, match="acceptance authority denied"):
        FactoryService.run(service, payload)
