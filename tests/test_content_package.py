from content_factory.content_package import apply_package_edit, build_content_package


def test_build_content_package_is_platform_neutral_and_keeps_provenance():
    result = {
        "content_brief": {"title": "Эволюция не случайна", "revision_id": "brief-r1"},
        "script": {"units": [{"text": "Первый абзац."}, {"text": "Второй абзац."}]},
        "production": {
            "output": {"output_id": "out-1"},
            "assets": [
                {
                    "asset_id": "asset-1",
                    "asset_type": "visual",
                    "origin": "openverse",
                    "uri": "data/a.png",
                    "claim_refs": ["c1"],
                    "evidence_refs": ["e1"],
                }
            ],
            "qc": {"status": "PASSED", "passed": True},
        },
        "information_flow": {
            "research": {
                "claims": [{"claim_id": "c1", "text": "bounded claim"}],
                "evidence": [{"evidence_id": "e1", "text": "evidence"}],
            }
        },
    }

    package = build_content_package(run_id="run-1", result=result, platform="telegram")

    assert package["platform"] == "telegram"
    assert package["text"] == "Первый абзац.\n\nВторой абзац."
    assert package["media"][0]["origin"] == "openverse"
    assert package["claims"][0]["claim_id"] == "c1"
    assert package["provenance"]["content_brief_revision_id"] == "brief-r1"


def test_package_edit_creates_revision_and_invalidates_qc_and_approval():
    package = {
        "package_version": 1,
        "package_id": "run-1:package",
        "run_id": "run-1",
        "platform": "telegram",
        "title": "Old",
        "text": "Old text",
        "media": [],
        "claims": [],
        "evidence": [],
        "qc": {"status": "PASSED", "passed": True},
        "approval": {"status": "APPROVED"},
        "revision": {"revision_id": "r1", "edited": False},
    }
    result = {"package_revision_id": "r1", "approval": {"status": "APPROVED"}}

    updated_result, updated = apply_package_edit(
        result=result,
        package=package,
        patch={"text": "Edited text"},
    )

    assert updated["text"] == "Edited text"
    assert updated["revision"]["revision_id"] == "r2"
    assert updated["qc"]["status"] == "NEEDS_RECHECK"
    assert updated["approval"] == {}
    assert updated_result["package_edited"] is True
    assert "approval" not in updated_result
