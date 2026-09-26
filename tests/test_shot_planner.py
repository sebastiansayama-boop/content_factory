from __future__ import annotations

import pytest

from content_factory.integrations import ExternalCallResult
from content_factory.openai_adapter import OpenAIResponsesAdapter
from content_factory.shot_planner import (
    ShotPackConfig,
    ShotPackValidationError,
    build_planner_prompt,
    plan_brief,
    validate_shot_pack,
)


class RecordingAdapter:
    def __init__(self, text: str) -> None:
        self.text = text
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> ExternalCallResult:
        self.prompts.append(prompt)
        return ExternalCallResult(
            integration_id="openai.responses",
            status_code=200,
            response_id="resp_test_planner_001",
            payload={
                "output": [
                    {
                        "content": [
                            {"text": self.text},
                        ]
                    }
                ]
            },
        )

    @staticmethod
    def response_text(result: ExternalCallResult) -> str:
        return OpenAIResponsesAdapter.response_text(result)


def valid_pack(shots: int = 2) -> dict:
    return {
        "title": "Example",
        "logline": "A concise explanation.",
        "style_bible": {
            "visual_style": "editorial motion graphics",
            "palette": "dark blue and warm yellow",
            "lighting": "soft studio",
            "subject_continuity": "same visual language in every shot",
            "negative_constraints": "no logos or text artifacts",
        },
        "shots": [
            {
                "shot_id": f"shot_{i:02d}",
                "narration": f"Narration {i}.",
                "visual_action": f"Action {i}.",
                "composition": "Vertical medium shot.",
                "camera_motion": "slow push_in",
                "mood": "focused",
                "image_prompt": f"Concrete visual scene {i}.",
                "negative_prompt": "No logos.",
                "transition": "hard_cut",
                "image_file": f"scene_{i:02d}.png",
                "voice_file": f"voice_{i:02d}.wav",
            }
            for i in range(1, shots + 1)
        ],
    }


def test_validate_accepts_renderer_shape() -> None:
    config = ShotPackConfig(shots=2)
    result = validate_shot_pack(valid_pack(2), config)
    assert result["shots"][0]["image_file"] == "scene_01.png"
    assert result["shots"][1]["voice_file"] == "voice_02.wav"


def test_validate_rejects_wrong_asset_names() -> None:
    config = ShotPackConfig(shots=2)
    pack = valid_pack(2)
    pack["shots"][0]["image_file"] = "demo.png"
    with pytest.raises(ShotPackValidationError, match="scene_01.png"):
        validate_shot_pack(pack, config)


def test_validate_rejects_wrong_shot_count() -> None:
    config = ShotPackConfig(shots=4)
    with pytest.raises(ShotPackValidationError, match="exactly 4"):
        validate_shot_pack(valid_pack(2), config)


def test_build_prompt_is_explicit_about_no_existing_assets() -> None:
    prompt = build_planner_prompt("Explain a scientific idea", ShotPackConfig())
    assert "Return ONLY valid JSON" in prompt
    assert "do not claim that images or audio already exist" in prompt
    assert "scene_01.png" in prompt
    assert "voice_04.wav" in prompt


def test_plan_brief_parses_real_provider_response_shape() -> None:
    adapter = RecordingAdapter(__import__("json").dumps(valid_pack(2)))
    result = plan_brief("Explain a scientific idea", ShotPackConfig(shots=2), adapter=adapter)
    assert result["planner_response_id"] == "resp_test_planner_001"
    assert result["language"] == "ru"
    assert result["duration_seconds"] == 25
    assert result["resolution"] == "1080x1920"
    assert len(adapter.prompts) == 1


def test_plan_brief_rejects_non_json_provider_output() -> None:
    adapter = RecordingAdapter("not json")
    with pytest.raises(ShotPackValidationError, match="invalid JSON"):
        plan_brief("Explain a scientific idea", adapter=adapter)
