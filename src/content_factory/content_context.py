from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ProviderKind = Literal["research", "text", "image", "video", "audio"]


@dataclass(frozen=True)
class ContentContext:
    """Canonical semantic context shared across provider boundaries.

    This is the product-level context. Providers receive a translated,
    task-specific view rather than this object wholesale.
    """

    run_id: str
    task_id: str
    purpose: str
    claims: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    editorial_units: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    source_asset_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProviderContext:
    """Minimal provider-facing context for one production task."""

    run_id: str
    task_id: str
    purpose: str
    claims: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    editorial_units: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    source_asset_ids: tuple[str, ...] = ()
    provider: ProviderKind = "text"
    metadata: dict[str, str] = field(default_factory=dict)


class ContextError(ValueError):
    pass


def to_provider_context(
    context: ContentContext,
    *,
    provider: ProviderKind,
) -> ProviderContext:
    """Translate canonical context into a provider-specific view.

    The canonical context is deliberately richer than any single provider
    request. Translation prevents accidental forwarding of irrelevant data
    while preserving the stable run/task identity and semantic dependencies.
    """

    if not context.run_id or not context.task_id:
        raise ContextError("run_id and task_id are required")
    if not context.purpose:
        raise ContextError("purpose is required")

    if provider == "research":
        return ProviderContext(
            run_id=context.run_id,
            task_id=context.task_id,
            purpose=context.purpose,
            claims=context.claims,
            evidence=context.evidence,
            editorial_units=context.editorial_units,
            constraints=context.constraints,
            provider=provider,
        )

    if provider == "text":
        return ProviderContext(
            run_id=context.run_id,
            task_id=context.task_id,
            purpose=context.purpose,
            claims=context.claims,
            editorial_units=context.editorial_units,
            constraints=context.constraints,
            provider=provider,
        )

    return ProviderContext(
        run_id=context.run_id,
        task_id=context.task_id,
        purpose=context.purpose,
        claims=context.claims,
        editorial_units=context.editorial_units,
        constraints=context.constraints,
        source_asset_ids=context.source_asset_ids,
        provider=provider,
    )
