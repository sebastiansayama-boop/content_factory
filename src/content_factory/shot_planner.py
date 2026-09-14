from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .openai_adapter import OpenAIResponsesAdapter


@dataclass(frozen=True)
class ShotPackConfig:
    language: str = "ru"
    duration_seconds: int = 25
    shots: int = 4
    resolution: str = "1080x1920"


class ShotPackValidationError(ValueError):
    pass


_REQUIRED_SHOT_FIELDS = (
    "shot_id",
    "narration",
    "visual_action",
    "composition",
    "camera_motion",
    "mood",
    "image_prompt",
    "negative_prompt",
    "transition",
    "image_file",
    "voice_file",
)


def _extract_json(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()

    try:
        value = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ShotPackValidationError(f"planner returned invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ShotPackValidationError("planner JSON root must be an object")
    return value


def validate_shot_pack(pack: dict[str, Any], config: ShotPackConfig) -> dict[str, Any]:
    if not isinstance(pack.get("title"), str) or not pack["title"].strip():
        raise ShotPackValidationError("title must be a non-empty string")
    if not isinstance(pack.get("logline"), str) or not pack["logline"].strip():
        raise ShotPackValidationError("logline must be a non-empty string")

    style_bible = pack.get("style_bible")
    if not isinstance(style_bible, dict):
        raise ShotPackValidationError("style_bible must be an object")
    for key in ("visual_style", "palette", "lighting", "subject_continuity", "negative_constraints"):
        if not isinstance(style_bible.get(key), str) or not style_bible[key].strip():
            raise ShotPackValidationError(f"style_bible.{key} must be a non-empty string")

    shots = pack.get("shots")
    if not isinstance(shots, list) or len(shots) != config.shots:
        raise ShotPackValidationError(f"shots must contain exactly {config.shots} items")

    for index, shot in enumerate(shots, start=1):
        if not isinstance(shot, dict):
            raise ShotPackValidationError(f"shots[{index}] must be an object")
        missing = [field for field in _REQUIRED_SHOT_FIELDS if not isinstance(shot.get(field), str) or not shot[field].strip()]
        if missing:
            raise ShotPackValidationError(f"shots[{index}] missing required fields: {', '.join(missing)}")
        expected_id = f"shot_{index:02d}"
        if shot["shot_id"] != expected_id:
            raise ShotPackValidationError(f"shots[{index}].shot_id must be {expected_id}")
        if shot["image_file"] != f"scene_{index:02d}.png":
            raise ShotPackValidationError(f"shots[{index}].image_file must be scene_{index:02d}.png")
        if shot["voice_file"] != f"voice_{index:02d}.wav":
            raise ShotPackValidationError(f"shots[{index}].voice_file must be voice_{index:02d}.wav")
        if not shot["image_file"].endswith(".png") or not shot["voice_file"].endswith(".wav"):
            raise ShotPackValidationError(f"shots[{index}] asset extensions are invalid")

    return pack


def build_planner_prompt(brief: str, config: ShotPackConfig) -> str:
    if not brief.strip():
        raise ValueError("brief must not be empty")
    return f"""Create an executable local-pack plan for a short social video.

Return ONLY valid JSON. Do not use Markdown fences and do not add commentary.

Brief:
{brief.strip()}

Hard output requirements:
- language: {config.language}
- duration_seconds: {config.duration_seconds}
- resolution: {config.resolution}
- exactly {config.shots} shots
- every shot must contain: shot_id, narration, visual_action, composition, camera_motion, mood, image_prompt, negative_prompt, transition, image_file, voice_file
- shot IDs must be shot_01 through shot_{config.shots:02d}
- image files must be scene_01.png through scene_{config.shots:02d}.png
- voice files must be voice_01.wav through voice_{config.shots:02d}.wav
- image_prompt must describe a concrete visual that can actually be rendered
- narration must be spoken copy, not instructions to another model
- do not claim that images or audio already exist; this step creates the plan only
- keep visual continuity explicit in style_bible

Required JSON shape:
{{
  "title": "...",
  "logline": "...",
  "style_bible": {{
    "visual_style": "...",
    "palette": "...",
    "lighting": "...",
    "subject_continuity": "...",
    "negative_constraints": "..."
  }},
  "shots": [
    {{
      "shot_id": "shot_01",
      "narration": "...",
      "visual_action": "...",
      "composition": "...",
      "camera_motion": "...",
      "mood": "...",
      "image_prompt": "...",
      "negative_prompt": "...",
      "transition": "hard_cut",
      "image_file": "scene_01.png",
      "voice_file": "voice_01.wav"
    }}
  ]
}}"""


def plan_brief(
    brief: str,
    config: ShotPackConfig | None = None,
    adapter: OpenAIResponsesAdapter | None = None,
) -> dict[str, Any]:
    cfg = config or ShotPackConfig()
    provider = adapter or OpenAIResponsesAdapter()
    result = provider.generate(build_planner_prompt(brief, cfg))
    if result.status_code < 200 or result.status_code >= 300:
        raise RuntimeError(f"OpenAI planner returned HTTP {result.status_code}")
    if not result.response_id:
        raise RuntimeError("OpenAI planner response has no response_id")
    text = provider.response_text(result)
    pack = validate_shot_pack(_extract_json(text), cfg)
    pack["language"] = cfg.language
    pack["duration_seconds"] = cfg.duration_seconds
    pack["resolution"] = cfg.resolution
    pack["planner_response_id"] = result.response_id
    return pack
