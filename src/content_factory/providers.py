from __future__ import annotations

from typing import Any, Protocol, Sequence, runtime_checkable

from .integrations import ExternalCallResult


@runtime_checkable
class LLMProvider(Protocol):
    """Minimal text/structured generation boundary."""

    def generate(self, prompt: str) -> ExternalCallResult:
        ...


@runtime_checkable
class ResearchProvider(Protocol):
    """Research boundary: provider returns normalized external call data."""

    def research(self, prompt: str) -> ExternalCallResult:
        ...

    @staticmethod
    def text(result: ExternalCallResult) -> str:
        ...

    @staticmethod
    def sources(result: ExternalCallResult) -> list[dict[str, str]]:
        ...


@runtime_checkable
class ImageProvider(Protocol):
    """Read-only image discovery boundary."""

    provider: str

    def search(self, query: str, limit: int = 8) -> Sequence[Any]:
        ...


@runtime_checkable
class QCProvider(Protocol):
    """Deterministic quality-check boundary."""

    def evaluate(self, **kwargs: Any) -> dict[str, Any]:
        ...
