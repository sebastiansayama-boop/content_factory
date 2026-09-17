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
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        base_url.rstrip("/") + path,
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the first Content Factory vertical-slice test.")
    parser.add_argument("--url", default=os.environ.get("FACTORY_URL", "http://127.0.0.1:10000"))
    parser.add_argument("--token", default=os.environ.get("FACTORY_API_TOKEN", ""))
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()

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
    source_id = analysis.get("source_id")
    stories = analysis.get("stories")
    if not isinstance(source_id, str) or not source_id:
        raise RuntimeError("analyze did not return source_id")
    if not isinstance(stories, list) or not stories:
        raise RuntimeError("analyze produced no stories")
    story = stories[0]
    if not story.get("id") or not story.get("title"):
        raise RuntimeError("selected story has no id/title")
    if story.get("source_id") != source_id:
        raise RuntimeError("selected story is not tied to the analyzed source")
    evidence = story.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise RuntimeError("selected story has no source evidence")
    print(json.dumps({"source_id": source_id, "story": story}, ensure_ascii=False, indent=2))

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
    if package.get("source_id") != source_id:
        raise RuntimeError("produce changed source identity")
    assets = package.get("package")
    if not isinstance(assets, list) or not assets:
        raise RuntimeError("produce returned an empty package")
    formats = {asset.get("format") for asset in assets if isinstance(asset, dict)}
    missing = {"article", "social_posts"} - formats
    if missing:
        raise RuntimeError(f"produce is missing requested formats: {sorted(missing)}")
    for asset in assets:
        if asset.get("format") in {"article", "social_posts"}:
            refs = asset.get("source_refs")
            if not isinstance(refs, list) or not refs:
                raise RuntimeError(f"asset has no source_refs: {asset.get('format')}")
    print(json.dumps({"story_id": package.get("story_id"), "formats": sorted(formats)}, ensure_ascii=False, indent=2))

    print("[3/3] VERIFY PIPELINE")
    runtime = package.get("runtime", {})
    required = {"work_item_id", "operation_id", "execution_id", "output_revision_id", "state"}
    missing_runtime = required - runtime.keys()
    if missing_runtime:
        raise RuntimeError(f"runtime identity is incomplete: {sorted(missing_runtime)}")
    if runtime["state"] not in {"OBSERVED", "DELIVERED"}:
        raise RuntimeError(f"unexpected final state: {runtime['state']}")

    print("FIRST VERTICAL SECTOR TEST: PASS")
    print(json.dumps({"runtime": runtime, "asset_count": len(assets), "source_id": source_id}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
