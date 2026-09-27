from pathlib import Path

from content_factory.content_run import ContentRunStore
from content_factory.exporter import ContentExporter


def test_approval_requires_review_and_export_requires_approval(tmp_path):
    store = ContentRunStore(tmp_path / "runs.sqlite3")
    run = store.create(title="Test", brief="Test brief")
    store.start_planning(run.run_id)
    store.save_result(run.run_id, {
        "production": {
            "qc": {"status": "PASSED"},
            "output": {"output_id": "output-1", "uri": str(tmp_path / "sequence.json")},
        }
    })
    Path(tmp_path / "sequence.json").write_text('{"status":"ASSEMBLED"}', encoding="utf-8")

    approved = store.approve(run.run_id, decision_ref="human-review-1")
    assert approved.status == "APPROVED"
    assert approved.result["approval"]["decision_ref"] == "human-review-1"

    export = ContentExporter(tmp_path).export(run_id=run.run_id, result=approved.result)
    assert export["status"] == "EXPORTED"
    assert Path(export["manifest_uri"]).is_file()

    exported = store.mark_exported(run.run_id, export)
    assert exported.status == "EXPORTED"
    assert exported.result["export"]["sha256"] == export["sha256"]
    store.close()
