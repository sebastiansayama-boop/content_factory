from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import os


class IntegrationError(Exception):
    """Expected failure while communicating with an external integration."""


@dataclass(frozen=True)
class IntegrationConfig:
    integration_id: str
    endpoint: str
    secret_env: str | None = None

    def validate(self) -> None:
        if not self.endpoint.startswith(("https://", "http://")):
            raise IntegrationError("integration endpoint must be HTTP(S)")
        if self.secret_env and not os.getenv(self.secret_env):
            raise IntegrationError(f"missing integration secret: {self.secret_env}")


@dataclass(frozen=True)
class ExternalCallResult:
    integration_id: str
    status_code: int
    response_id: str | None
    payload: Any


class ExternalAdapter(Protocol):
    def call(self, payload: dict[str, Any]) -> ExternalCallResult:
        ...


class HttpJsonAdapter:
    """Minimal provider-neutral HTTP JSON adapter.

    Authentication is read from an environment variable and is never included
    in the normalized result. The caller must decide whether the response is
    sufficient evidence of an external effect.
    """

    def __init__(self, config: IntegrationConfig) -> None:
        self.config = config
        self.config.validate()

    def call(self, payload: dict[str, Any]) -> ExternalCallResult:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.config.secret_env:
            headers["Authorization"] = f"Bearer {os.environ[self.config.secret_env]}"

        request = Request(
            self.config.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
                try:
                    body = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    body = {"raw_response": raw}
                response_id = None
                if isinstance(body, dict):
                    response_id = body.get("id") or body.get("execution_id") or body.get("publication_id")
                return ExternalCallResult(
                    integration_id=self.config.integration_id,
                    status_code=response.status,
                    response_id=response_id,
                    payload=body,
                )
        except HTTPError as exc:
            raise IntegrationError(f"provider HTTP error: {exc.code}") from exc
        except URLError as exc:
            raise IntegrationError("provider connectivity error") from exc
