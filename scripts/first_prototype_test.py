from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_SOURCE = Path(__file__).parent.parent / "tests" / "fixtures" / "first_prototype_source.txt"


def request(base_url: str, token: str, path: str, payload: dict) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the first Content Factory vertical-slice test.")
    parser.add_argument("--url", default=os.environ.get("FACTORY_URL", "http://127.0.0.1:10000"))
    parser.add_argument("--token", default=os.environ.get("FACTORY_API_TOKEN", ""))
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()

    if not args.token:
        raise SystemExit("FACTORY_API_TOKEN is required")
    source = args.source.read_text(encoding="utf-8").strip()
    if not source:
        raise SystemExit("source fixture is empty")

    print("[1/3] ANALYZE")
    analysis = request(
        args.url,
        args.token,
        "/api/analyze",
        {"title": "First prototype source", "source": source},
    )
    stories = analysis.get("stories")
    if not isinstance(stories, list) or not stories:
        raise RuntimeError("analyze produced no stories")
    story = stories[0]
    if not story.get("id") or not story.get("title"):
        raise RuntimeError("selected story has no id/title")
    print(json.dumps({"source_id": analysis.get("source_id"), "story": story}, ensure_ascii=False, indent=2))

    print("[2/3] PRODUCE")
    package = request(
        args.url,
        args.token,
        "/api/produce",
        {
            "source": source,
            "story": story,
            "formats": ["article", "social_posts"],
        },
    )
    assets = package.get("package")
    if not isinstance(assets, list) or not assets:
        raise RuntimeError("produce returned an empty package")
    formats = {asset.get("format") for asset in assets if isinstance(asset, dict)}
    missing = {"article", "social_posts"} - formats
    if missing:
        raise RuntimeError(f"produce is missing requested formats: {sorted(missing)}")
    print(json.dumps({"story_id": package.get("story_id"), "formats": sorted(formats)}, ensure_ascii=False, indent=2))

    print("[3/3] VERIFY PIPELINE")
    runtime = package.get("runtime", {})
    required = {"work_item_id", "operation_id", "execution_id", "output_revision_id", "state"}
    missing_runtime = required - runtime.keys()
    if missing_runtime:
        raise RuntimeError(f"runtime identity is incomplete: {sorted(missing_runtime)}")
    if runtime["state"] not in {"OBSERVED", "DELIVERED"}:
        raise RuntimeError(f"unexpected final state: {runtime['state']}")

    print("FIRST PROTOTYPE TEST: PASS")
    print(json.dumps({"runtime": runtime, "asset_count": len(assets)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
