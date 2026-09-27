from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


class ExportError(ValueError):
    pass


class ContentExporter:
    """Create a durable, hashable export package from an approved run."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def export(self, *, run_id: str, result: dict[str, Any]) -> dict[str, Any]:
        approval = result.get("approval")
        if not isinstance(approval, dict) or approval.get("status") != "APPROVED":
            raise ExportError("content run must have an explicit APPROVED decision")
        production = result.get("production")
        if not isinstance(production, dict):
            raise ExportError("production result is missing")
        output = production.get("output")
        if not isinstance(output, dict):
            raise ExportError("assembled output is missing")

        source_uri = str(output.get("uri") or "").strip()
        if not source_uri:
            raise ExportError("assembled output has no uri")
        source = Path(source_uri)
        if not source.is_file():
            raise ExportError("assembled output file does not exist")

        export_dir = self.root / "exports" / run_id
        export_dir.mkdir(parents=True, exist_ok=True)
        package_path = export_dir / source.name
        if source.resolve() != package_path.resolve():
            shutil.copy2(source, package_path)

        manifest = {
            "export_id": f"export-{run_id}",
            "run_id": run_id,
            "decision_ref": approval.get("decision_ref"),
            "source_output_id": output.get("output_id"),
            "artifact": package_path.name,
            "bytes": package_path.stat().st_size,
            "sha256": self._sha256(package_path),
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
