from __future__ import annotations

from copy import deepcopy
from typing import Any


PLATFORM_VALUES = {"telegram", "instagram", "threads", "x", "article", "youtube"}
MEDIA_TYPES = {"image", "video"}


def platform_from_constraints(constraints: tuple[str, ...] | list[str], default: str = "telegram") -> str:
    for item in constraints:
        value = str(item).strip()
        if value.lower().startswith("platform:"):
            candidate = value.split(":", 1)[1].strip().lower()
            if candidate in PLATFORM_VALUES:
                return candidate
    return default
def build_content_package(*, run_id: str, result: dict[str, Any], platform: str) -> dict[str, Any]:
    """Build the platform-neutral review package from the current durable run result."""
    platform = platform.strip().lower()
    if platform not in PLATFORM_VALUES:
        raise ValueError(f"unsupported platform: {platform}")

    production = result.get("production") if isinstance(result.get("production"), dict) else {}
    output = production.get("output") if isinstance(production.get("output"), dict) else {}
    script = result.get("script") if isinstance(result.get("script"), dict) else {}
    content_brief = result.get("content_brief") if isinstance(result.get("content_brief"), dict) else {}
    information_flow = result.get("information_flow") if isinstance(result.get("information_flow"), dict) else {}
    research = information_flow.get("research") if isinstance(information_flow.get("research"), dict) else {}

    units = script.get("units") if isinstance(script.get("units"), list) else []
    text = "\n\n".join(
        str(unit.get("text") or "").strip()
        for unit in units
        if isinstance(unit, dict) and str(unit.get("text") or "").strip()
    )
    title = str(content_brief.get("title") or result.get("title") or "").strip()

    assets = production.get("assets") if isinstance(production.get("assets"), list) else []
    media = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        asset_type = str(asset.get("asset_type") or "").strip().lower()
        media_type = "video" if asset_type in {"video", "visual_video"} else "image" if asset_type in {"visual", "image"} else None
        if media_type is None:
            continue
        metadata = asset.get("metadata") if isinstance(asset.get("metadata"), dict) else {}
        media.append({
            "media_id": str(asset.get("asset_id") or ""),
            "type": media_type,
            "origin": str(asset.get("origin") or asset.get("provider") or metadata.get("source") or "generated"),
            "uri": str(asset.get("uri") or ""),
            "source": asset.get("source") or metadata.get("foreign_landing_url") or metadata.get("source_url"),
            "license": asset.get("license") or metadata.get("license"),
            "license_url": asset.get("license_url") or metadata.get("license_url"),
            "creator": asset.get("creator") or metadata.get("creator"),
            "prompt": asset.get("prompt"),
            "visual_decision_id": metadata.get("decision_id"),
            "visual_policy_version": metadata.get("policy_version"),
            "claim_refs": list(asset.get("claim_refs") or []),
            "evidence_refs": list(asset.get("evidence_refs") or []),
        })

    claims = research.get("claims") if isinstance(research.get("claims"), list) else []
    evidence = research.get("evidence") if isinstance(research.get("evidence"), list) else []
    qc = production.get("qc") if isinstance(production.get("qc"), dict) else {}
    approval = result.get("approval") if isinstance(result.get("approval"), dict) else {}

    return {
        "package_version": 1,
        "package_id": f"{run_id}:package",
        "run_id": run_id,
        "platform": platform,
        "title": title,
        "text": text,
        "media": media,
        "claims": deepcopy(claims),
        "evidence": deepcopy(evidence),
        "provenance": {
            "content_brief_revision_id": content_brief.get("revision_id"),
            "output_id": output.get("output_id"),
            "information_flow_present": bool(information_flow),
        },
        "qc": deepcopy(qc),
        "approval": deepcopy(approval),
        "revision": {
            "revision_id": str(result.get("package_revision_id") or "r1"),
            "edited": bool(result.get("package_edited")),
        },
    }


def apply_package_edit(
    *,
    result: dict[str, Any],
    package: dict[str, Any],
    patch: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply deterministic user edits and invalidate QC/approval for the edited package."""
    if not isinstance(patch, dict):
        raise ValueError("package patch must be an object")

    editable = {"title", "text", "media", "platform"}
    unknown = set(patch) - editable
    if unknown:
        raise ValueError(f"unsupported package fields: {sorted(unknown)}")

    updated = deepcopy(package)
    for key, value in patch.items():
        if key in {"title", "text", "platform"} and not isinstance(value, str):
            raise ValueError(f"{key} must be a string")
        if key == "media" and not isinstance(value, list):
            raise ValueError("media must be an array")
        updated[key] = deepcopy(value)

    platform = str(updated.get("platform") or "").lower().strip()
    if platform not in PLATFORM_VALUES:
        raise ValueError(f"unsupported platform: {platform}")

    for item in updated.get("media") or []:
        if not isinstance(item, dict):
            raise ValueError("each media item must be an object")
        if str(item.get("type") or "") not in MEDIA_TYPES:
            raise ValueError("media.type must be image or video")

    revision = int(str(result.get("package_revision_id") or "r1").removeprefix("r")) + 1
    result = deepcopy(result)
    result["package_revision_id"] = f"r{revision}"
    result["package_edited"] = True
    result["package"] = updated
    result["production"] = {
        **(result.get("production") if isinstance(result.get("production"), dict) else {}),
        "qc": {
            "status": "NEEDS_RECHECK",
            "passed": False,
            "reason": "content package edited after production",
            "checks": [],
        },
    }
    result.pop("approval", None)
    updated["qc"] = result["production"]["qc"]
    updated["approval"] = {}
    updated["revision"] = {"revision_id": f"r{revision}", "edited": True}
    return result, updated
