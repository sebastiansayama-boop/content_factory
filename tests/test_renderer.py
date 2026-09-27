from pathlib import Path

import pytest

from content_factory.renderer import RenderError, WhisperStudioRenderer


def _production(tmp_path: Path, *, image: Path, voice: Path) -> dict:
    return {
        "output": {
            "format": "video",
            "sequence": [
                {
                    "script_unit_id": f"unit-{i}",
                    "asset_uri": str(image),
                    "voice_uri": str(voice),
                }
                for i in range(4)
            ],
        }
    }


def test_whisper_studio_adapter_builds_local_pack_and_rejects_non_png(tmp_path):
    studio = tmp_path / "whisper-studio"
    studio.mkdir()
    (studio / "one_command.py").write_text("print('fixture')", encoding="utf-8")
    image = tmp_path / "scene.png"
    image.write_bytes(b"png")
    voice = tmp_path / "voice.wav"
    voice.write_bytes(b"wav")

    renderer = WhisperStudioRenderer(root=studio, data_root=tmp_path)
    with pytest.raises(RenderError, match="Whisper Studio completed without manifest"):
        renderer.render(
            run_id="run-1",
            title="Test",
            script={"units": [{"unit_id": f"unit-{i}", "text": "line", "visual_intent": "visual"} for i in range(4)]},
            production=_production(tmp_path, image=image, voice=voice),
        )
    pack = tmp_path / "renderer_inputs" / "run-1" / "pack.json"
    assert pack.is_file()
    assert (tmp_path / "renderer_inputs" / "run-1" / "scene_01.png").is_file()
    assert (tmp_path / "renderer_inputs" / "run-1" / "voice_01.wav").is_file()


def test_whisper_studio_adapter_requires_media_assets(tmp_path):
    studio = tmp_path / "whisper-studio"
    studio.mkdir()
    (studio / "one_command.py").write_text("print('fixture')", encoding="utf-8")
    bad = tmp_path / "asset.json"
    bad.write_text("{}", encoding="utf-8")
    voice = tmp_path / "voice.wav"
    voice.write_bytes(b"wav")

    renderer = WhisperStudioRenderer(root=studio, data_root=tmp_path)
    with pytest.raises(RenderError, match="requires PNG"):
        renderer.render(
            run_id="run-2",
            title="Test",
            script={"units": [{"unit_id": f"unit-{i}", "text": "line", "visual_intent": "visual"} for i in range(4)]},
            production=_production(tmp_path, image=bad, voice=voice),
        )
