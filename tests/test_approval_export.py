from pathlib import Path

from content_factory.content_run import ContentRunStore
from content_factory.exporter import ContentExporter
from content_factory.renderer import RenderResult


class FakeRenderer:
    def __init__(self, video: Path, manifest: Path) -> None:
        self.video = video
        self.manifest = manifest

    def render(self, *, run_id, title, script, production):
        return RenderResult(
            renderer="fake",
            final_video=str(self.video),
            manifest=str(self.manifest),
            artifacts={"final.mp4": {"bytes": self.video.stat().st_size}},
        )


def test_approval_requires_review_and_export_requires_approval(tmp_path):
    store = ContentRunStore(tmp_path / "runs.sqlite3")
    run = store.create(title="Test", brief="Test brief")
    store.start_planning(run.run_id)

    sequence = tmp_path / "sequence.json"
    sequence.write_text('{"status":"ASSEMBLED"}', encoding="utf-8")
    video = tmp_path / "rendered.mp4"
    video.write_bytes(b"fake-mp4")
    renderer_manifest = tmp_path / "renderer-manifest.json"
    renderer_manifest.write_text("{}", encoding="utf-8")

    store.save_result(
        run.run_id,
        {
            "script": {"script_id": "script-1", "units": []},
            "production": {
                "qc": {"status": "PASSED"},
                "output": {"output_id": "output-1", "uri": str(sequence)},
            },
        },
    )

    approved = store.approve(run.run_id, decision_ref="human-review-1")
    assert approved.status == "APPROVED"

    export = ContentExporter(
        tmp_path,
        renderer=FakeRenderer(video, renderer_manifest),
    ).export(run_id=run.run_id, result=approved.result)
    assert export["status"] == "EXPORTED"
    assert export["artifact"] == "final.mp4"
    assert Path(export["manifest_uri"]).is_file()
    assert export["renderer"] == "fake"

    exported = store.mark_exported(run.run_id, export)
    assert exported.status == "EXPORTED"
    assert exported.result["export"]["sha256"] == export["sha256"]
    store.close()
