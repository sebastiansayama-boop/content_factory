from __future__ import annotations

from pathlib import Path
from typing import Any

from .asset_generator import OpenAIAssetGenerator, materialize_shot_pack_assets
from .shot_planner import ShotPackConfig, plan_brief


def generate_media_pack(
    brief: str,
    output_dir: Path,
    config: ShotPackConfig | None = None,
    generator: OpenAIAssetGenerator | None = None,
) -> dict[str, Any]:
    """Run the real brief -> plan -> PNG/WAV generation path.

    The planner must first produce a valid renderer contract. Media generation
    then calls the real OpenAI image and speech endpoints. No fixture fallback
    exists: any provider failure raises and no synthetic asset is substituted.
    """
    pack = plan_brief(brief, config=config)
    asset_manifest = materialize_shot_pack_assets(
        pack,
        output_dir,
        generator=generator,
    )
    return {
        "pack": pack,
        "assets": asset_manifest,
    }
