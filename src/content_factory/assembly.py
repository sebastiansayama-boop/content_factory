from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .asset_registry import AssetRegistry


class AssemblyError(ValueError):
    pass


class ContentAssembler:
    """Build a deterministic sequence/output manifest from script units and assets."""

    def __init__(self, registry: AssetRegistry, root: str | Path) -> None:
        self.registry = registry
        self.root = Path(root)

    def assemble(self, *, run_id: str, script: dict[str, Any], production_plan: dict[str, Any]) -> dict[str, Any]:
        units = script.get("units")
        requests = production_plan.get("asset_requests")
        if not isinstance(units, list) or not units:
            raise AssemblyError("script must contain units")
        if not isinstance(requests, list) or not requests:
            raise AssemblyError("production plan must contain asset_requests")

        assets = self.registry.list_for_run(run_id)
        by_request = {asset.asset_request_id: asset for asset in assets}
        by_unit = {asset.script_unit_id: asset for asset in assets}
        sequence = []
        for index, unit in enumerate(units, start=1):
            if not isinstance(unit, dict):
                raise AssemblyError("script unit must be an object")
            unit_id = str(unit.get("unit_id") or "").strip()
            if not unit_id:
                raise AssemblyError("script unit requires unit_id")
            request = next(
                (item for item in requests
                 if isinstance(item, dict) and str(item.get("script_unit_id") or "") == unit_id),
                None,
            )
            if request is None:
                raise AssemblyError(f"no asset request for script unit {unit_id}")
            request_id = str(request.get("asset_request_id") or "")
            asset = by_request.get(request_id) or by_unit.get(unit_id)
            if asset is None:
                raise AssemblyError(f"no registered asset for script unit {unit_id}")
            sequence.append({
                "position": index,
                "script_unit_id": unit_id,
                "kind": str(unit.get("kind") or ""),
                "text": str(unit.get("text") or ""),
                "visual_intent": str(unit.get("visual_intent") or ""),
                "asset_id": asset.asset_id,
                "asset_uri": asset.uri,
                "asset_type": asset.asset_type,
                "voice_uri": str(asset.metadata.get("voice_uri") or ""),
                "claim_refs": list(dict.fromkeys(asset.claim_refs)),
                "evidence_refs": list(dict.fromkeys(asset.evidence_refs)),
            })

        output_dir = self.root / "outputs" / run_id
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = output_dir / "sequence.json"
        manifest = {
            "output_id": f"output-{run_id}",
            "run_id": run_id,
            "title": str(script.get("title") or ""),
            "format": str(production_plan.get("format") or ""),
            "sequence": sequence,
            "status": "ASSEMBLED",
        }
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return manifest | {"uri": str(manifest_path)}


class QualityGate:
    """Deterministic QC over the assembled output graph."""

    def evaluate(self, *, run_id: str, script: dict[str, Any], production_plan: dict[str, Any],
                 assets: list[Any], output: dict[str, Any]) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []

        def check(name: str, passed: bool, detail: str) -> None:
            checks.append({"check": name, "passed": passed, "detail": detail})

        units = script.get("units")
        requests = production_plan.get("asset_requests")
        check("script_units_present", isinstance(units, list) and bool(units), "script contains units")
        check("asset_requests_present", isinstance(requests, list) and bool(requests), "production plan contains requests")
        check("asset_count_matches_script", isinstance(units, list) and len(assets) >= len(units),
              f"{len(assets)} registered assets for {len(units) if isinstance(units, list) else 0} script units")
        check("output_uri_present", bool(str(output.get("uri") or "").strip()), "sequence manifest exists")

        if isinstance(units, list):
            asset_units = {asset.script_unit_id for asset in assets}
            for unit in units:
                unit_id = str(unit.get("unit_id") or "") if isinstance(unit, dict) else ""
                check(
                    f"asset_for_{unit_id}",
                    bool(unit_id) and unit_id in asset_units,
                    f"registered asset exists for {unit_id}",
                )

        for asset in assets:
            check(
                f"provenance_{asset.asset_id}",
                bool(asset.claim_refs) and bool(asset.evidence_refs),
                "asset retains claim and evidence provenance",
            )
            check(
                f"uri_{asset.asset_id}",
                bool(asset.uri.strip()),
                "asset has a non-empty URI/path",
            )

        passed = all(item["passed"] for item in checks)
        return {
            "qc_id": f"qc-{run_id}",
            "run_id": run_id,
            "status": "PASSED" if passed else "FAILED",
            "passed": passed,
            "checks": checks,
            "output_id": output.get("output_id"),
        }
