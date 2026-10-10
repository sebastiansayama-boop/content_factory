from __future__ import annotations

import hashlib
import io
import json
import shutil
import zipfile
from pathlib import Path
from typing import Any

from .renderer import Renderer, build_renderer


class ExportError(ValueError):
    pass


class ContentExporter:
    """Render an approved run and create a durable, hashable export manifest."""

    def __init__(self, root: str | Path, renderer: Renderer | None = None) -> None:
        self.root = Path(root)
        self.renderer = renderer or build_renderer(self.root)

    def export(self, *, run_id: str, result: dict[str, Any]) -> dict[str, Any]:
        approval = result.get("approval")
        if not isinstance(approval, dict) or approval.get("status") != "APPROVED":
            raise ExportError("content run must have an explicit APPROVED decision")

        production = result.get("production")
        if not isinstance(production, dict):
            raise ExportError("production result is missing")
        script = result.get("script")
        if not isinstance(script, dict):
            raise ExportError("script is missing")

        content_spec = result.get("content_spec")
        title = (
            str(content_spec.get("title"))
            if isinstance(content_spec, dict) and content_spec.get("title")
            else str(result.get("editorial", {}).get("selected_idea", {}).get("title") or run_id)
        )
        rendered = self.renderer.render(
            run_id=run_id,
            title=title,
            script=script,
            production=production,
        )

        source = Path(rendered.final_video)
        if not source.is_file():
            raise ExportError("renderer returned a missing final video")

        export_dir = self.root / "exports" / run_id
        export_dir.mkdir(parents=True, exist_ok=True)
        if rendered.renderer == "package":
            package_path = export_dir / "content-package.json"
        else:
            package_path = export_dir / ("final" + (source.suffix or ".mp4"))
        if source.resolve() != package_path.resolve():
            shutil.copy2(source, package_path)

        manifest = {
            "export_id": f"export-{run_id}",
            "run_id": run_id,
            "decision_ref": approval.get("decision_ref"),
            "renderer": rendered.renderer,
            "source_output_id": production.get("output", {}).get("output_id"),
            "source_video": rendered.final_video,
            "artifact": package_path.name,
            "artifact_type": "content_package" if rendered.renderer == "package" else "video",
            "bytes": package_path.stat().st_size,
            "sha256": self._sha256(package_path),
            "renderer_manifest": rendered.manifest,
            "renderer_artifacts": rendered.artifacts,
            "status": "EXPORTED",
        }
        manifest_path = export_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        manifest["manifest_uri"] = str(manifest_path)
        return manifest

    def build_post_bundle(self, *, run_id: str, result: dict[str, Any]) -> bytes:
        """Downloadable caption + local images for an already approved/exported run.

        The existing content-package.json remains the canonical export.
        Missing or external image files are not silently represented as shipped.
        """
        approval = result.get("approval")
        exported = result.get("export")
        if not isinstance(approval, dict) or approval.get("status") != "APPROVED":
            raise ExportError("an approved content revision is required")
        if not isinstance(exported, dict) or exported.get("status") != "EXPORTED":
            raise ExportError("export is required before downloading a post bundle")
        if exported.get("artifact_type") != "content_package":
            raise ExportError("post bundle is available only for package exports")

        data_root = self.root.resolve()
        export_root = (data_root / "exports").resolve()
        export_dir = (export_root / run_id).resolve()
        try:
            export_dir.relative_to(export_root)
        except ValueError as exc:
            raise ExportError("invalid export location") from exc

        package_path = export_dir / "content-package.json"
        if not package_path.is_file():
            raise ExportError("original content package is unavailable")

        package = result.get("package") if isinstance(result.get("package"), dict) else {}
        script = result.get("script") if isinstance(result.get("script"), dict) else {}
        units = script.get("units") if isinstance(script.get("units"), list) else []
        caption = str(package.get("text") or "").strip()
        if not caption:
            caption = "\n\n".join(str(unit.get("text") or "").strip() for unit in units if isinstance(unit, dict)).strip()
        if not caption:
            raise ExportError("approved publication has no usable caption")

        production = result.get("production") if isinstance(result.get("production"), dict) else {}
        all_assets = production.get("assets") if isinstance(production.get("assets"), list) else []
        images: list[tuple[Path, str, dict[str, Any]]] = []
        for asset in all_assets:
            if not isinstance(asset, dict) or str(asset.get("asset_type") or "").lower() not in {"visual", "image"}:
                continue
            if len(images) >= 12:
                raise ExportError("post bundle supports at most 12 images")
            uri = str(asset.get("uri") or "").strip()
            image_path = Path(uri).resolve()
            try:
                image_path.relative_to(data_root)
            except ValueError as exc:
                raise ExportError("image is not stored within the durable data directory") from exc
            if not image_path.is_file() or image_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                raise ExportError("a referenced image is missing or not a supported local image")
            if image_path.stat().st_size > 20 * 1024 * 1024:
                raise ExportError("a referenced image exceeds the 20 MB bundle limit")
            image_name = f"images/image-{len(images) + 1:02d}{image_path.suffix.lower()}"
            images.append((image_path, image_name, {
                "file": image_name,
                "sha256": self._sha256(image_path),
                "asset_id": asset.get("asset_id"),
                "provider": asset.get("provider"),
                "claim_refs": asset.get("claim_refs", []),
                "evidence_refs": asset.get("evidence_refs", []),
                "source": asset.get("source") or (asset.get("metadata") or {}).get("source_url"),
                "license": asset.get("license") or (asset.get("metadata") or {}).get("license"),
            }))

        metadata = {
            "run_id": run_id,
            "title": package.get("title") or (result.get("content_spec") or {}).get("title"),
            "platform": package.get("platform") or "unknown",
            "approved_version": approval.get("approved_version"),
            "decision_ref": approval.get("decision_ref"),
            "publication_status": "NOT_PUBLISHED_BY_EXPORT",
            "caption_sha256": hashlib.sha256(caption.encode("utf-8")).hexdigest(),
            "images": [item[2] for item in images],
        }
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("caption.txt", caption + "\n")
            archive.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2))
            archive.write(package_path, arcname="content-package.json")
            for image_path, image_name, _ in images:
                archive.write(image_path, arcname=image_name)
        return buffer.getvalue()

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
