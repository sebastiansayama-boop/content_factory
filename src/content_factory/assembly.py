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
            if visual_request is None or voice_request is None:
                raise AssemblyError(f"visual and voice asset requests are required for script unit {unit_id}")

            visual_id = str(visual_request.get("asset_request_id") or "")
            voice_id = str(voice_request.get("asset_request_id") or "")
            visual = by_request.get(visual_id) or by_unit_type.get((unit_id, "visual"))
            voice = by_request.get(voice_id) or by_unit_type.get((unit_id, "voice"))
            if visual is None or voice is None:
                raise AssemblyError(f"visual and voice assets are required for script unit {unit_id}")

            sequence.append({
                "position": index,
                "script_unit_id": unit_id,
                "kind": str(unit.get("kind") or ""),
                "text": str(unit.get("text") or ""),
                "visual_intent": str(unit.get("visual_intent") or ""),
                "asset_id": visual.asset_id,
                "asset_uri": visual.uri,
                "asset_type": visual.asset_type,
                "voice_asset_id": voice.asset_id,
                "voice_uri": voice.uri,
                "voice_asset_type": voice.asset_type,
                "claim_refs": list(dict.fromkeys(visual.claim_refs + voice.claim_refs)),
                "evidence_refs": list(dict.fromkeys(visual.evidence_refs + voice.evidence_refs)),
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
    """Deterministic QC over the assembled output graph and semantic lineage."""

    def evaluate(
        self,
        *,
        run_id: str,
        script: dict[str, Any],
        production_plan: dict[str, Any],
        assets: list[Any],
        output: dict[str, Any],
        information_flow: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []

        def check(
            name: str,
            passed: bool,
            detail: str,
            lineage_refs: list[str] | tuple[str, ...] = (),
        ) -> None:
            checks.append({
                "check": name,
                "passed": passed,
                "detail": detail,
                "lineage_refs": list(dict.fromkeys(str(ref) for ref in lineage_refs if str(ref).strip())),
            })

        units = script.get("units")
        requests = production_plan.get("asset_requests")
        check("script_units_present", isinstance(units, list) and bool(units), "script contains units")
        check("asset_requests_present", isinstance(requests, list) and bool(requests), "production plan contains requests")
        check(
            "asset_count_matches_script",
            isinstance(units, list) and len(assets) >= len(units),
            f"{len(assets)} registered assets for {len(units) if isinstance(units, list) else 0} script units",
            [str(item.get("unit_id")) for item in units if isinstance(item, dict)],
        )
        check("output_uri_present", bool(str(output.get("uri") or "").strip()), "sequence manifest exists", [str(output.get("output_id") or "")])

        if isinstance(units, list):
            asset_units = {asset.script_unit_id for asset in assets}
            for unit in units:
                unit_id = str(unit.get("unit_id") or "") if isinstance(unit, dict) else ""
                check(
                    f"asset_for_{unit_id}",
                    bool(unit_id) and unit_id in asset_units,
                    f"registered asset exists for {unit_id}",
                    [unit_id],
                )

        request_by_unit = {
            str(item.get("script_unit_id")): item
            for item in requests or []
            if isinstance(item, dict) and str(item.get("script_unit_id") or "").strip()
        }
        for asset in assets:
            refs = [asset.asset_id, asset.script_unit_id, *asset.claim_refs, *asset.evidence_refs]
            check(
                f"provenance_{asset.asset_id}",
                bool(asset.claim_refs) and bool(asset.evidence_refs),
                "asset retains claim and evidence provenance",
                refs,
            )
            check(
                f"uri_{asset.asset_id}",
                bool(asset.uri.strip()),
                "asset has a non-empty URI/path",
                [asset.asset_id],
            )
            request = request_by_unit.get(asset.script_unit_id)
            check(
                f"artifact_production_{asset.asset_id}",
                request is not None
                and set(asset.claim_refs).issubset(set(request.get("claim_refs") or []))
                and set(asset.evidence_refs).issubset(set(request.get("evidence_refs") or [])),
                "artifact preserves the production request provenance",
                refs + ([str(request.get("asset_request_id"))] if request else []),
            )

        flow = information_flow if isinstance(information_flow, dict) else None
        flow_claims = {
            str(item.get("claim_id")): item
            for item in (flow or {}).get("claims", [])
            if isinstance(item, dict) and str(item.get("claim_id") or "").strip()
        }
        flow_evidence = {
            str(item.get("evidence_id")): item
            for item in (flow or {}).get("evidence", [])
            if isinstance(item, dict) and str(item.get("evidence_id") or "").strip()
        }
        flow_points = (flow or {}).get("editorial_points", [])
        flow_elements = (flow or {}).get("content_elements", [])
        flow_artifacts = (flow or {}).get("artifacts", [])

        if flow is not None:
            claim_evidence_ok = bool(flow_claims) and bool(flow_evidence) and all(
                isinstance(claim.get("evidence_ids"), list | tuple) and bool(claim.get("evidence_ids"))
                and set(claim.get("evidence_ids")).issubset(flow_evidence)
                for claim in flow_claims.values()
            )
            check(
                "claim_evidence",
                claim_evidence_ok,
                "every lineage claim has resolvable evidence",
                [ref for claim_id, claim in flow_claims.items() for ref in (claim_id, *(claim.get("evidence_ids") or []))],
            )

            script_claim_refs = {
                ref
                for unit in units or []
                if isinstance(unit, dict)
                for ref in unit.get("claim_refs", [])
                if isinstance(ref, str) and ref.strip()
            }
            check(
                "content_claim",
                script_claim_refs.issubset(flow_claims) if script_claim_refs else False,
                "script claims resolve to lineage claims",
                sorted(script_claim_refs),
            )

            editorial_claims = {
                ref
                for point in flow_points
                if isinstance(point, dict)
                for ref in point.get("claim_ids", [])
                if isinstance(ref, str) and ref.strip()
            }
            spec_claims = {
                ref for ref in production_plan.get("claim_refs", [])
                if isinstance(ref, str) and ref.strip()
            }
            check(
                "content_editorial",
                bool(flow_points) and (
                    not spec_claims or spec_claims.issubset(editorial_claims)
                ),
                "editorial points retain the content claim lineage",
                [str(point.get("point_id")) for point in flow_points if isinstance(point, dict)] + sorted(spec_claims),
            )

            check(
                "lineage_artifacts",
                bool(flow_elements) and bool(flow_artifacts)
                and all(
                    isinstance(item, dict)
                    and item.get("content_element_ids")
                    and set(item.get("content_element_ids") or []).issubset(
                        {str(element.get("element_id")) for element in flow_elements if isinstance(element, dict)}
                    )
                    for item in flow_artifacts
                ),
                "every lineage artifact resolves to a content element",
                [str(item.get("artifact_id")) for item in flow_artifacts if isinstance(item, dict)]
                + [str(item.get("element_id")) for item in flow_elements if isinstance(item, dict)],
            )
        else:
            check("lineage_present", False, "information flow is required for lineage-aware QC")

        expected_format = str(production_plan.get("format") or "").strip()
        check(
            "format",
            bool(expected_format) and str(output.get("format") or "").strip() == expected_format,
            "assembled output format matches production plan",
            [str(output.get("output_id") or ""), expected_format],
        )
        check(
            "consistency",
            isinstance(units, list)
            and isinstance(output.get("sequence"), list)
            and len(output["sequence"]) == len(units),
            "assembled sequence matches script unit count",
            [str(item.get("unit_id")) for item in units or [] if isinstance(item, dict)],
        )

        semantic_guard = production_plan.get("semantic_guard")
        if semantic_guard is None:
            check("semantic_guard", True, "no semantic guard is configured for this production plan")
        else:
            check(
                "semantic_guard",
                isinstance(semantic_guard, dict) and semantic_guard.get("status") == "PASSED",
                "configured semantic guard must explicitly pass",
                [str(semantic_guard.get("id") or "semantic-guard") if isinstance(semantic_guard, dict) else "semantic-guard"],
            )

        passed = all(item["passed"] for item in checks)
        return {
            "qc_id": f"qc-{run_id}",
            "run_id": run_id,
            "status": "PASSED" if passed else "FAILED",
            "passed": passed,
            "checks": checks,
            "output_id": output.get("output_id"),
            "lineage": {
                "information_flow_present": flow is not None,
                "claim_ids": sorted(flow_claims),
                "evidence_ids": sorted(flow_evidence),
                "editorial_point_ids": [
                    str(item.get("point_id"))
                    for item in flow_points
                    if isinstance(item, dict)
                ],
                "content_element_ids": [
                    str(item.get("element_id"))
                    for item in flow_elements
                    if isinstance(item, dict)
                ],
                "artifact_ids": [
                    str(item.get("artifact_id"))
                    for item in flow_artifacts
                    if isinstance(item, dict)
                ],
            },
        }
