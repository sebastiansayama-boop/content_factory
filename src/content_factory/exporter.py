from __future__ import annotations

import hashlib
import json
import shutil
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

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
