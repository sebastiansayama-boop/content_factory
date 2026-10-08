"""Regression checks for Luka's preserved identity reference and provenance."""

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def test_luka_identity_reference_is_recoverable_and_not_auto_approved():
    character = json.loads((ROOT / "docs/character/character.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "docs/character/references/luka-cafe-2026-10-08.json").read_text(encoding="utf-8"))
    preview = ROOT / manifest["preview"]["path"]

    assert character["slug"] == "luka"
    assert character["display_name"] == "Лука"
    assert character["identity"]["face_description"]
    assert character["identity"]["hair"]
    assert character["identity"]["approved_references"] == []
    assert any(item["reference_id"] == manifest["reference_id"] for item in character["identity"]["reference_candidates"])
    assert manifest["status"] == "candidate_pending_human_identity_qc"
    assert manifest["original"]["sha256"] == "b7476ff7300a83dc1897fdac11c38c36fb249251b0fb84e10c9bcf6a1d7bd9e5"
    assert manifest["original"]["library_file_id"]
    assert preview.is_file(), "The GitHub preview image was not committed"

    binary = preview.read_bytes()
    git_sha = hashlib.sha1(b"blob " + str(len(binary)).encode() + bytes([0]) + binary).hexdigest()
    assert git_sha == manifest["preview"]["git_blob_sha"]
    with Image.open(preview) as image:
        image.load()
        assert image.format == "JPEG"
        assert image.size == (160, 186)
