from __future__ import annotations
import argparse
import json
from pathlib import Path

REQUIRED_FIELDS = ("id", "task", "input", "expected", "source_refs", "tags")

def validate(path: Path) -> list[str]:
    errors = []
    ids = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            errors.append(f"line {line_no}: blank line")
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(item, dict):
            errors.append(f"line {line_no}: record is not an object")
            continue
        missing = [field for field in REQUIRED_FIELDS if field not in item]
        if missing:
            errors.append(f"line {line_no}: missing fields: {', '.join(missing)}")
        record_id = item.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            errors.append(f"line {line_no}: id must be a non-empty string")
        else:
            ids.append(record_id)
        if not isinstance(item.get("task"), str) or not item["task"].strip():
            errors.append(f"line {line_no}: task must be a non-empty string")
        for field in ("source_refs", "tags"):
            value = item.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"line {line_no}: {field} must be a non-empty list")
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    if duplicates:
        errors.append("duplicate ids: " + ", ".join(duplicates))
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="model_data/eval/content_factory_eval_v1.jsonl")
    args = parser.parse_args()
    errors = validate(Path(args.path))
    if errors:
        print("MODEL EVAL VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    count = sum(1 for line in Path(args.path).read_text(encoding="utf-8").splitlines() if line.strip())
    print(f"MODEL EVAL VALIDATION: PASSED ({count} cases)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
