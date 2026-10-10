from io import BytesIO
from zipfile import ZipFile
import json

import pytest
from PIL import Image

from content_factory.exporter import ContentExporter, ExportError


def _ready_run(root):
    run_id = "run-bundle-1"
    exported = root / "exports" / run_id
    exported.mkdir(parents=True)
    (exported / "content-package.json").write_text('{"run_id":"run-bundle-1"}', encoding="utf-8")
    image = root / "approved-visual.png"
    Image.new("RGB", (12, 12), (100, 120, 140)).save(image)
    result = {
        "approval": {"status": "APPROVED", "decision_ref": "human-accept-1", "approved_version": "v1"},
        "export": {"status": "EXPORTED", "artifact_type": "content_package", "artifact": "content-package.json"},
        "package": {"text": "Подпись, одобренная редактором.", "title": "Пост", "platform": "telegram"},
        "production": {"assets": [{"asset_id": "img-1", "asset_type": "visual", "uri": str(image), "provider": "local-test"}]},
    }
    return run_id, result


def test_bundle_contains_caption_image_json_and_explicitly_unpublished_state(tmp_path):
    run_id, result = _ready_run(tmp_path)
    payload = ContentExporter(tmp_path).build_post_bundle(run_id=run_id, result=result)
    with ZipFile(BytesIO(payload)) as archive:
        assert set(archive.namelist()) == {
            "caption.txt", "metadata.json", "content-package.json", "images/image-01.png",
        }
        assert archive.read("caption.txt").decode("utf-8") == "Подпись, одобренная редактором.\n"
        assert archive.read("images/image-01.png").startswith(b"\x89PNG")
        metadata = json.loads(archive.read("metadata.json"))
        assert metadata["decision_ref"] == "human-accept-1"
        assert metadata["publication_status"] == "NOT_PUBLISHED_BY_EXPORT"
        assert metadata["images"][0]["file"] == "images/image-01.png"


def test_bundle_rejects_unapproved_and_unexported_results(tmp_path):
    run_id, result = _ready_run(tmp_path)
    result["approval"]["status"] = "PENDING"
    with pytest.raises(ExportError, match="approved"):
        ContentExporter(tmp_path).build_post_bundle(run_id=run_id, result=result)
    result["approval"]["status"] = "APPROVED"
    result["export"]["status"] = "PENDING"
    with pytest.raises(ExportError, match="export"):
        ContentExporter(tmp_path).build_post_bundle(run_id=run_id, result=result)


def test_bundle_rejects_images_outside_data_root(tmp_path):
    root = tmp_path / "data"
    root.mkdir()
    run_id, result = _ready_run(root)
    outside = tmp_path / "outside.png"
    Image.new("RGB", (8, 8)).save(outside)
    result["production"]["assets"][0]["uri"] = str(outside)
    with pytest.raises(ExportError, match="durable data directory"):
        ContentExporter(root).build_post_bundle(run_id=run_id, result=result)


def test_bundle_fails_closed_when_image_missing(tmp_path):
    run_id, result = _ready_run(tmp_path)
    result["production"]["assets"][0]["uri"] = str(tmp_path / "missing.png")
    with pytest.raises(ExportError, match="missing"):
        ContentExporter(tmp_path).build_post_bundle(run_id=run_id, result=result)
