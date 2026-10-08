"""Revision-bound character context and verified import of original images.

Profiles remain repository data. Runtime imports never approve a candidate or
replace a repository original with a preview.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from PIL import Image


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def image_info(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size > 50 * 1024 * 1024:
        raise ValueError("image is missing or exceeds 50 MiB")
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        if image.format not in {"PNG", "JPEG", "WEBP"}:
            raise ValueError("image must be PNG, JPEG or WebP")
        return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "width": image.width, "height": image.height, "format": image.format}


class CharacterCatalog:
    def __init__(self, profile_dir: Path, data_root: Path):
        self.profile_dir = profile_dir.resolve()
        self.data_root = data_root.resolve()

    def profiles(self) -> list[dict[str, Any]]:
        return [json.loads(path.read_text()) for path in sorted(self.profile_dir.rglob("character.json"))]

    def snapshot(self, character_id: str) -> dict[str, Any]:
        for path in sorted(self.profile_dir.rglob("character.json")):
            profile = json.loads(path.read_text())
            if character_id not in {profile.get("character_id"), profile.get("slug")}:
                continue
            if profile.get("identity", {}).get("adult") is not True:
                raise ValueError("character must be explicitly adult")
            references = []
            # Manifest paths are repository-relative, as in the existing Luka profile.
            repository = self.profile_dir.parents[1]
            for candidate in profile.get("identity", {}).get("reference_candidates", []):
                manifest_path = (repository / candidate["manifest_path"]).resolve()
                manifest_path.relative_to(repository)
                manifest = json.loads(manifest_path.read_text())
                entries = manifest.get("legacy_sources", [manifest])
                entry = next((e for e in entries if e.get("reference_id") == candidate["reference_id"]), None)
                if entry is None:
                    raise ValueError("character reference is absent from its manifest")
                references.append({"reference_id": entry["reference_id"],
                                   "status": entry.get("status", candidate.get("status")),
                                   "original": entry["original"]})
            value = {"profile": profile, "references": references}
            return {**value, "revision_id": digest(value), "character_id": profile["character_id"]}
        raise ValueError("character not found")

    def staging_path(self, path: str) -> Path:
        candidate = Path(path).resolve()
        try:
            candidate.relative_to(self.data_root / "imports")
        except ValueError as exc:
            raise ValueError("import source must be inside FACTORY_DATA_DIR/imports") from exc
        if not candidate.is_file():
            raise ValueError("staged import file not found")
        return candidate

    def reference_path(self, reference: dict[str, Any]) -> Path:
        original = reference["original"]
        suffix = Path(original.get("filename") or original.get("library_path", "image.png")).suffix
        return self.data_root / "character_references" / (original["sha256"] + suffix)

    def import_reference(self, character_id: str, reference_id: str, source: str) -> dict[str, Any]:
        snapshot = self.snapshot(character_id)
        reference = next((r for r in snapshot["references"] if r["reference_id"] == reference_id), None)
        if reference is None:
            raise ValueError("unknown character reference")
        source_path = self.staging_path(source)
        info = image_info(source_path)
        expected = reference["original"]
        if any(info[key] != expected[key] for key in ("sha256", "width", "height")):
            raise ValueError("original reference checksum or dimensions do not match manifest; previews are not originals")
        target = self.reference_path(reference)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target)
        return {**reference, "uri": str(target), "available": True, "verified": True}

    def inventory(self, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        result = []
        for reference in snapshot["references"]:
            path = self.reference_path(reference)
            valid = False
            if path.is_file():
                try:
                    info = image_info(path)
                    valid = all(info[k] == reference["original"][k] for k in ("sha256", "width", "height"))
                except (ValueError, OSError):
                    pass
            result.append({**reference, "uri": str(path), "available": path.is_file(), "verified": valid})
        return result

    def capture_context(self, snapshot: dict[str, Any], run_id: str, knowledge) -> None:
        """Use declared fiction as a candidate, never as empirical evidence."""
        profile = snapshot["profile"]
        text = (f"Вымышленный взрослый персонаж {profile.get('display_name', profile['character_id'])} "
                f"({profile['character_id']}, версия {snapshot['revision_id'][:12]}): повседневные фотографии; "
                "биография, характер и точный цвет глаз пока не утверждены.")
        research = {
            "sources": [{"id": "character-source", "title": "Declared fictional character specification",
                         "url": f"character://{profile['character_id']}/{snapshot['revision_id']}"}],
            "evidence": [{"id": "character-evidence", "source_id": "character-source", "excerpt": text,
                          "locator": "repository character profile", "provenance": "creator-supplied fiction, not real-world evidence"}],
            "claims": [{"id": "character-claim", "text": text, "confidence": "high",
                        "source_ids": ["character-source"], "evidence_ids": ["character-evidence"],
                        "scope": "declared fictional character only", "known_unknowns": profile.get("open_decisions", [])}],
            "editorial_angles": [],
        }
        knowledge.capture(run_id=run_id, research=research)


def character_constraints(snapshot: dict[str, Any]) -> list[str]:
    profile = snapshot["profile"]
    return ["CHARACTER CONTEXT: " + json.dumps(profile, ensure_ascii=False),
            "Produce a non-explicit everyday creator photo and caption. Preserve visual identity and natural photographic texture.",
            "The profile is fictional creative context, not evidence about a real person. Do not invent biography, approved personality, exact eye color, age or real-world events. Preserve all open decisions."]


def validate_character_release(result: dict[str, Any]) -> None:
    from .content_package import review_digest
    character = result.get("character")
    if not character:
        return
    package = result.get("package") or {}
    review = (result.get("production_plan") or {}).get("character_review") or {}
    if not review.get("approved") or not review.get("decision_ref") or review.get("package_digest") != review_digest(package):
        raise ValueError("character package requires human review of the exact image and caption revision")
    if review.get("character_revision_id") != character["revision_id"]:
        raise ValueError("character review is bound to another profile revision")
    media = package.get("media") or []
    if not media or not str(package.get("text") or "").strip():
        raise ValueError("character publication requires image and caption")
    if package.get("platform") == "instagram" and len(package["text"]) > 2200:
        raise ValueError("Instagram caption exceeds 2200 characters")
    assets = {asset["asset_id"]: asset for asset in result.get("production", {}).get("assets", [])}
    for item in media:
        asset = assets.get(item.get("media_id"))
        if asset is None or item.get("uri") != asset.get("uri"):
            raise ValueError("package media must resolve to the run's registered assets")
        info = image_info(Path(item["uri"]))
        if min(info["width"], info["height"]) < 512 or info["sha256"] != review.get("asset_hashes", {}).get(item["media_id"]):
            raise ValueError("reviewed image was replaced or is not full resolution")
        if package.get("platform") == "instagram" and not 0.8 <= info["width"] / info["height"] <= 1.91:
            raise ValueError("Instagram feed image must have aspect ratio between 4:5 and 1.91:1")
