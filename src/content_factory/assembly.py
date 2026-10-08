from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .asset_registry import AssetRegistry
from .claim_strength_qc import assess_claims
from .scope_expansion_qc import assess_scopes


class AssemblyError(ValueError):
    pass


class ContentAssembler:
    """Build a deterministic sequence/output manifest from script units and assets."""

    def __init__(self, registry: AssetRegistry, root: str | Path) -> None:
        self.registry = registry
        self.root = Path(root)

    def assemble(self, *, run_id: str, script: dict[str, Any], production_plan: dict[str, Any], assets: list[Any] | None = None) -> dict[str, Any]:
        units = script.get("units")
        requests = production_plan.get("asset_requests")
        if not isinstance(units, list) or not units:
            raise AssemblyError("script must contain units")
        if not isinstance(requests, list) or not requests:
            raise AssemblyError("production plan must contain asset_requests")

        resolved_assets = assets if assets is not None else self.registry.list_for_run(run_id)
        by_request = {asset.asset_request_id: asset for asset in resolved_assets}
        by_unit_type = {(asset.script_unit_id, asset.asset_type): asset for asset in resolved_assets}
        image_text = production_plan.get("media_mode") == "image_text"
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
            if image_text:
                visual_request = next((item for item in requests if item.get("type") == "visual"), None)
                visual = by_request.get(str((visual_request or {}).get("asset_request_id")))
                if visual is None:
                    raise AssemblyError("photo publication requires its planned visual asset")
                sequence.append({"position": index, "script_unit_id": unit_id,
                                 "kind": str(unit.get("kind") or ""), "text": str(unit.get("text") or ""),
                                 "visual_intent": str(unit.get("visual_intent") or ""),
                                 "asset_id": visual.asset_id, "asset_uri": visual.uri, "asset_type": visual.asset_type,
                                 "claim_refs": list(unit.get("claim_refs") or []), "evidence_refs": list(unit.get("evidence_refs") or [])})
                continue
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


_HIGH_RISK_EPISTEMIC_OUTPUT_PATTERNS = (
    "доказывает, что",
    "доказывает",
    "опровергнуто",
    "опровергает",
    "строгим закономерностям",
    "исключительно случайност",
    "исключительно хаот",
    "proves that",
    "proves",
    "refutes",
    "strict laws",
    "entirely random",
    "purely random",
    "fundamentally not random",
)


def _epistemic_output_violations(output: dict[str, Any]) -> list[str]:
    """Find high-certainty formulations in the assembled user-facing text."""
    texts = [str(output.get("title") or "")]
    sequence = output.get("sequence")
    if isinstance(sequence, list):
        texts.extend(
            str(item.get("text") or "")
            for item in sequence
            if isinstance(item, dict)
        )
    violations: list[str] = []
    for text in texts:
        folded = text.casefold()
        for pattern in _HIGH_RISK_EPISTEMIC_OUTPUT_PATTERNS:
            if pattern in folded:
                violations.append(pattern)
    return list(dict.fromkeys(violations))


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
            isinstance(units, list) and len(assets) >= (len(requests or []) if production_plan.get("media_mode") == "image_text" else len(units)),
            f"{len(assets)} registered assets for {len(units) if isinstance(units, list) else 0} script units",
            [str(item.get("unit_id")) for item in units if isinstance(item, dict)],
        )
        check("output_uri_present", bool(str(output.get("uri") or "").strip()), "sequence manifest exists", [str(output.get("output_id") or "")])

        epistemic_violations = _epistemic_output_violations(output)
        check(
            "epistemic_scope",
            not epistemic_violations,
            "assembled output does not contain unsupported high-certainty formulations"
            if not epistemic_violations
            else "assembled output contains high-certainty formulations: " + ", ".join(epistemic_violations),
            [str(output.get("output_id") or ""), *epistemic_violations],
        )

        if isinstance(units, list):
            asset_units = {asset.script_unit_id for asset in assets}
            for unit in units:
                unit_id = str(unit.get("unit_id") or "") if isinstance(unit, dict) else ""
                check(
                    f"asset_for_{unit_id}",
                    bool(unit_id) and (unit_id in asset_units or (production_plan.get("media_mode") == "image_text" and bool(assets))),
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

        claim_assessments = []
        scope_assessments = []

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

            claim_assessments = assess_claims(
                list(flow_claims.values()),
                evidence_items=list(flow_evidence.values()),
                source_items=[
                    item for item in (flow or {}).get("sources", [])
                    if isinstance(item, dict)
                ],
            ) if (flow or {}).get("sources") else []
            blocked_claims = [
                item for item in claim_assessments
                if item.verdict != "PASS"
            ]
            check(
                "claim_evidence_strength",
                not blocked_claims,
                "claim strength does not exceed evidence strength"
                if not blocked_claims
                else "claims require editorial repair: " + ", ".join(
                    f"{item.claim_id}:{item.verdict}:{item.repair_action}"
                    for item in blocked_claims
                ),
                [item.claim_id for item in claim_assessments if item.claim_id],
            )

            scope_assessments = assess_scopes(
                list(flow_claims.values()),
                evidence_items=list(flow_evidence.values()),
            )
            blocked_scope = [
                item for item in scope_assessments
                if item.verdict != "PASS"
            ]
            check(
                "claim_scope_expansion",
                not blocked_scope,
                "claim scope does not expand beyond evidence scope"
                if not blocked_scope
                else "claims require scope repair: " + ", ".join(
                    f"{item.claim_id}:{item.verdict}:{item.repair_action}"
                    for item in blocked_scope
                ),
                [item.claim_id for item in scope_assessments if item.claim_id],
            )

            script_claim_refs = {
                ref
                for unit in units or []
                if isinstance(unit, dict)
                for ref in unit.get("claim_refs", [])
                if isinstance(ref, str) and ref.strip()
            }
            spec_claim_refs = {
                ref
                for ref in (script.get("claim_refs") or [])
                if isinstance(ref, str) and ref.strip()
            }
            if not spec_claim_refs:
                spec_claim_refs = {
                    ref
                    for request in (production_plan.get("asset_requests") or [])
                    if isinstance(request, dict)
                    for ref in request.get("claim_refs", [])
                    if isinstance(ref, str) and ref.strip()
                }
            check(
                "content_claim",
                bool(script_claim_refs)
                and bool(spec_claim_refs)
                and script_claim_refs.issubset(spec_claim_refs),
                "script claims are retained from the content specification",
                sorted(script_claim_refs | spec_claim_refs),
            )

            editorial_claims = {
                ref
                for point in flow_points
                if isinstance(point, dict)
                for ref in point.get("claim_ids", [])
                if isinstance(ref, str) and ref.strip()
            }
            check(
                "content_editorial",
                bool(flow_points)
                and bool(editorial_claims)
                and all(
                    isinstance(point, dict)
                    and bool(point.get("claim_ids"))
                    and bool(point.get("evidence_ids"))
                    for point in flow_points
                ),
                "editorial points retain claims and evidence in the information-flow graph",
                [str(point.get("point_id")) for point in flow_points if isinstance(point, dict)]
                + sorted(editorial_claims),
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

        character = production_plan.get("character")
        if character:
            from .character import image_info
            visuals = [asset for asset in assets if asset.asset_type == "visual"]
            valid_images = bool(visuals)
            hashes = {}
            for asset in visuals:
                try:
                    info = image_info(Path(asset.uri))
                    hashes[asset.asset_id] = info["sha256"]
                    valid_images = valid_images and min(info["width"], info["height"]) >= 512
                    valid_images = valid_images and asset.provider != "stub" and info["sha256"] == asset.metadata.get("sha256")
                    valid_images = valid_images and asset.metadata.get("character_revision_id") == character["revision_id"]
                except (ValueError, OSError):
                    valid_images = False
            check("character_images", valid_images, "full-resolution image bytes and character revision verified")
            review = production_plan.get("character_review") or {}
            check("character_identity_and_naturalism", bool(review.get("decision_ref"))
                  and review.get("approved") is True
                  and review.get("character_revision_id") == character["revision_id"]
                  and review.get("asset_hashes") == hashes,
                  "explicit human identity/naturalism review of these exact image bytes is required")

        passed = all(item["passed"] for item in checks)
        return {
            "qc_id": f"qc-{run_id}",
            "run_id": run_id,
            "status": "PASSED" if passed else "FAILED",
            "passed": passed,
            "checks": checks,
            "output_id": output.get("output_id"),
            "claim_strength_assessments": [
                item.to_dict()
                for item in claim_assessments
            ],
            "scope_assessments": [
                item.to_dict()
                for item in scope_assessments
            ],
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
