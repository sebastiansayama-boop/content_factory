"""Executable Content Factory v0."""

from .artifacts import ArtifactStore
from .content_demand import ContentDemand
from .external_source import Claim, Evidence, OpenAlexAdapter, Source
from .openalex_demand import build_content_demand
from .openai_capability import openai_text_capability
from .production import Artifact, ProductionJob, ProductionJobStatus, ProductionRegistry
from .runtime import (
    AcceptanceDecision,
    Capability,
    ExecutionResult,
    ExecutionUnknown,
    FactoryRuntime,
    FactoryState,
    PublicationResult,
    RuntimePolicy,
    VerificationResult,
    WorkItem,
)
from .runtime_store import RuntimeStore

__all__ = [
    "AcceptanceDecision",
    "Artifact",
    "Capability",
    "ContentDemand",
    "ArtifactStore",
    "Evidence",
    "ExecutionResult",
    "ExecutionUnknown",
    "FactoryRuntime",
    "FactoryState",
    "OpenAlexAdapter",
    "ProductionJob",
    "ProductionJobStatus",
    "ProductionRegistry",
    "PublicationResult",
    "RuntimePolicy",
    "RuntimeStore",
    "Source",
    "VerificationResult",
    "WorkItem",
    "build_content_demand",
    "openai_text_capability",
]
