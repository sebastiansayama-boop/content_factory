from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


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
