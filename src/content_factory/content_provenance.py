from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ProvenanceLink:
    source_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    claim_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class EditorialUnit:
    unit_id: str
    run_id: str
    kind: str
    text: str
    provenance: ProvenanceLink = field(default_factory=ProvenanceLink)
    created_at: str = field(default_factory=_now)


@dataclass(frozen=True)
class ContentAsset:
    asset_id: str
    run_id: str
    format: str
    provider: str
    provider_job_id: str
    editorial_unit_ids: tuple[str, ...] = ()
    provenance: ProvenanceLink = field(default_factory=ProvenanceLink)
    status: str = "GENERATED"
    created_at: str = field(default_factory=_now)


class ProvenanceError(ValueError):
    pass


@dataclass(frozen=True)
class RegenerationPlan:
    changed_claim_ids: tuple[str, ...]
    regenerate_asset_ids: tuple[str, ...]
    retain_asset_ids: tuple[str, ...]


class ProvenanceGraph:
    """Small cross-provider provenance graph.

    This is intentionally not a workflow engine. It records semantic
    relationships that provider-specific systems do not share with one
    another. Provider execution remains outside this module.
    """

    def __init__(self) -> None:
        self.editorial_units: dict[str, EditorialUnit] = {}
        self.assets: dict[str, ContentAsset] = {}

    def add_editorial_unit(self, unit: EditorialUnit) -> EditorialUnit:
        if unit.unit_id in self.editorial_units:
            raise ProvenanceError(f"editorial unit already exists: {unit.unit_id}")
        self.editorial_units[unit.unit_id] = unit
        return unit

    def add_asset(self, asset: ContentAsset) -> ContentAsset:
        if asset.asset_id in self.assets:
            raise ProvenanceError(f"asset already exists: {asset.asset_id}")
        missing = [
            unit_id
            for unit_id in asset.editorial_unit_ids
            if unit_id not in self.editorial_units
        ]
        if missing:
            raise ProvenanceError(
                f"asset references unknown editorial units: {', '.join(missing)}"
            )
        self.assets[asset.asset_id] = asset
        return asset

    @classmethod
    def from_package(
        cls,
        package: dict[str, Any],
        *,
        run_id: str,
        provider: str = "workspace",
    ) -> "ProvenanceGraph":
        """Build the graph directly from a normalized production package."""
        graph = cls()
        for item in package.get("package", []):
            if not isinstance(item, dict):
                raise ProvenanceError("package assets must be objects")
            asset_id = item.get("id")
            asset_format = item.get("format")
            if not isinstance(asset_id, str) or not asset_id:
                raise ProvenanceError("every package asset requires an id")
            if not isinstance(asset_format, str) or not asset_format:
                raise ProvenanceError(f"asset {asset_id} requires a format")
            claim_refs = item.get("claim_refs", [])
            if not isinstance(claim_refs, list) or not all(
                isinstance(ref, str) and ref for ref in claim_refs
            ):
                raise ProvenanceError(
                    f"asset {asset_id} claim_refs must contain non-empty strings"
                )
            graph.add_asset(
                ContentAsset(
                    asset_id=asset_id,
                    run_id=run_id,
                    format=asset_format,
                    provider=provider,
                    provider_job_id=asset_id,
                    provenance=ProvenanceLink(claim_ids=tuple(claim_refs)),
                )
            )
        return graph

    def affected_assets(self, *, claim_id: str) -> list[ContentAsset]:
        return [
            asset
            for asset in self.assets.values()
            if claim_id in asset.provenance.claim_ids
            or any(
                claim_id in self.editorial_units[unit_id].provenance.claim_ids
                for unit_id in asset.editorial_unit_ids
            )
        ]

    def affected_asset_ids(self, *, claim_id: str) -> list[str]:
        return [asset.asset_id for asset in self.affected_assets(claim_id=claim_id)]

    def regeneration_plan(
        self, *, changed_claim_ids: tuple[str, ...] | list[str]
    ) -> RegenerationPlan:
        changed = tuple(dict.fromkeys(changed_claim_ids))
        if not all(isinstance(claim_id, str) and claim_id for claim_id in changed):
            raise ProvenanceError("changed_claim_ids must contain non-empty strings")

        affected: list[str] = []
        for claim_id in changed:
            for asset_id in self.affected_asset_ids(claim_id=claim_id):
                if asset_id not in affected:
                    affected.append(asset_id)

        affected_set = set(affected)
        retained = [
            asset_id for asset_id in self.assets if asset_id not in affected_set
        ]
        return RegenerationPlan(
            changed_claim_ids=changed,
            regenerate_asset_ids=tuple(affected),
            retain_asset_ids=tuple(retained),
        )
