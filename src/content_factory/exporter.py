from __future__ import annotations

import hashlib
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

        if result.get("character") and (result.get("package") or {}).get("platform") == "instagram":
            return self._export_photo(run_id, result)

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

    def _export_photo(self, run_id: str, result: dict[str, Any]) -> dict[str, Any]:
        from .character import validate_character_release
        validate_character_release(result)
        if result.get("production", {}).get("qc", {}).get("status") != "PASSED":
            raise ExportError("photo publication must pass QC before export")
        package = result["package"]
        export_dir = self.root / "exports" / run_id
        export_dir.mkdir(parents=True, exist_ok=True)
        files = {}
        for index, item in enumerate(package["media"], 1):
            source = Path(item["uri"])
            destination = export_dir / f"image-{index:02d}{source.suffix}"
            shutil.copyfile(source, destination)
            files[destination.name] = {"sha256": self._sha256(destination), "bytes": destination.stat().st_size}
        caption = export_dir / "caption.txt"
        caption.write_text(package["text"], encoding="utf-8")
        files[caption.name] = {"sha256": self._sha256(caption), "bytes": caption.stat().st_size}
        manifest = {"export_id": f"export-{run_id}", "run_id": run_id, "platform": "instagram",
                    "status": "EXPORTED", "publication_status": "NOT_PUBLISHED", "artifact_type": "photo_publication",
                    "artifact": "instagram-publication.zip", "renderer": "photo_package", "files": files,
                    "character_revision_id": result["character"]["revision_id"],
                    "decision_ref": result["approval"]["decision_ref"], "package_revision": package["revision"]}
        package_manifest = export_dir / "publication.json"
        package_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        archive = export_dir / manifest["artifact"]
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for name in [*files, package_manifest.name]:
                bundle.write(export_dir / name, name)
        manifest.update(sha256=self._sha256(archive), bytes=archive.stat().st_size)
        manifest_path = export_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return {**manifest, "manifest_uri": str(manifest_path)}

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
