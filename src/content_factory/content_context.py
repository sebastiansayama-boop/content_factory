from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


ProviderKind = Literal["research", "text", "image", "video", "audio"]


@dataclass(frozen=True)
class ContentContext:
    """Canonical semantic context shared across provider boundaries.

    This is the product-level context. Providers should receive a translated,
    task-specific view rather than this object wholesale.
    """

    run_id: str
    task_id: str
    purpose: str
    claim_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    editorial_unit_ids: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    source_asset_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProviderContext:
    """Minimal provider-facing context for one production task."""

    run_id: str
    task_id: str
    purpose: str
    claim_ids: tuple[str, ...] = ()
    editorial_unit_ids: tuple[str, ...] = ()
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

    Research/evidence identifiers are retained only for providers that may
    need factual grounding. Media providers receive claims and constraints,
    plus source assets when a downstream transformation depends on them.
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
            claim_ids=context.claim_ids,
            editorial_unit_ids=context.editorial_unit_ids,
            constraints=context.constraints,
            provider=provider,
        )

    if provider == "text":
        return ProviderContext(
            run_id=context.run_id,
            task_id=context.task_id,
            purpose=context.purpose,
            claim_ids=context.claim_ids,
            editorial_unit_ids=context.editorial_unit_ids,
            constraints=context.constraints,
            provider=provider,
        )

    return ProviderContext(
        run_id=context.run_id,
        task_id=context.task_id,
        purpose=context.purpose,
        claim_ids=context.claim_ids,
        editorial_unit_ids=context.editorial_unit_ids,
        constraints=context.constraints,
        source_asset_ids=context.source_asset_ids,
        provider=provider,
    )
