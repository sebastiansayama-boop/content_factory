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
        by_unit_type = {(asset.script_unit_id, asset.asset_type): asset for asset in assets}
        sequence = []
        requires_voice = bool(production_plan.get("requires_voice", True))
        for index, unit in enumerate(units, start=1):
            if not isinstance(unit, dict):
                raise AssemblyError("script unit must be an object")
            unit_id = str(unit.get("unit_id") or "").strip()
            if not unit_id:
                raise AssemblyError("script unit requires unit_id")

            visual_request = next(
                (
                    item
                    for item in requests
                    if isinstance(item, dict)
                    and str(item.get("script_unit_id") or "") == unit_id
                    and str(item.get("type") or "") == "visual"
                ),
                None,
            )
            voice_request = next(
                (
                    item
                    for item in requests
                    if isinstance(item, dict)
                    and str(item.get("script_unit_id") or "") == unit_id
                    and str(item.get("type") or "") == "voice"
                ),
                None,
            )
            if visual_request is None or (requires_voice and voice_request is None):
                raise AssemblyError(f"visual asset request is required for script unit {unit_id}" if not requires_voice else f"visual and voice asset requests are required for script unit {unit_id}")

            visual_id = str(visual_request.get("asset_request_id") or "")
            voice_id = str(voice_request.get("asset_request_id") or "") if voice_request else ""
            visual = by_request.get(visual_id) or by_unit_type.get((unit_id, "visual"))
            voice = (by_request.get(voice_id) or by_unit_type.get((unit_id, "voice"))) if requires_voice else None
            if visual is None or (requires_voice and voice is None):
                raise AssemblyError(f"visual asset is required for script unit {unit_id}" if not requires_voice else f"visual and voice assets are required for script unit {unit_id}")

            item = {
                "position": index,
                "script_unit_id": unit_id,
                "kind": str(unit.get("kind") or ""),
                "text": str(unit.get("text") or ""),
                "visual_intent": str(unit.get("visual_intent") or ""),
                "asset_id": visual.asset_id,
                "asset_uri": visual.uri,
                "asset_type": visual.asset_type,
                "claim_refs": list(dict.fromkeys(visual.claim_refs + (voice.claim_refs if voice else ()))),
                "evidence_refs": list(dict.fromkeys(visual.evidence_refs + (voice.evidence_refs if voice else ()))),
            }
            if voice is not None:
                item.update({
                    "voice_asset_id": voice.asset_id,
                    "voice_uri": voice.uri,
                    "voice_asset_type": voice.asset_type,
                })
            sequence.append(item)

        output_dir = self.root / "outputs" / run_id
        output_dir.mkdir(parents=True, exist_ok=True)

        title = str(script.get("title") or "")
        text = "\n\n".join(item["text"] for item in sequence if item["text"])
        images = [
            {
                "position": item["position"],
                "script_unit_id": item["script_unit_id"],
                "asset_id": item["asset_id"],
                "uri": item["asset_uri"],
                "visual_intent": item["visual_intent"],
                "claim_refs": item["claim_refs"],
                "evidence_refs": item["evidence_refs"],
                "provider": visual.provider,
                "metadata": dict(visual.metadata),
            }
            for item in sequence
        ]
        package = {
            "package_id": f"package-{run_id}",
            "run_id": run_id,
            "title": title,
            "text": text,
            "images": images,
            "sequence": sequence,
            "status": "READY",
        }
        package_path = output_dir / "content-package.json"
        package_path.write_text(
            json.dumps(package, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        manifest_path = output_dir / "sequence.json"
        manifest = {
            "output_id": f"output-{run_id}",
            "run_id": run_id,
            "title": title,
            "format": str(production_plan.get("format") or ""),
            "sequence": sequence,
            "content_package": {
                "package_id": package["package_id"],
                "uri": str(package_path),
                "text": text,
                "images": images,
                "image_count": len(images),
            },
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
        package = output.get("content_package")
        check("content_package_present", isinstance(package, dict), "Content Package is present")
        check("content_package_text_present", isinstance(package, dict) and bool(str(package.get("text") or "").strip()), "Content Package contains text")
        package_images = package.get("images") if isinstance(package, dict) else None
        expected_images = len(units) if isinstance(units, list) else 0
        check(
            "content_package_images_present",
            isinstance(package_images, list) and len(package_images) == expected_images,
            "Content Package contains one image per script unit",
        )

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
