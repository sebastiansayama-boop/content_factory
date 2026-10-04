from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

LIVE_MODES = {
    "exact", "exact_reason", "exact_structural", "substring",
    "casefold_substring", "structural", "state_transition",
    "policy_exact", "state_policy", "policy_sequence", "authority_policy",
    "judge", "hybrid", "heuristic_plus_manual", "judge_or_policy",
    "acceptance_observation",
}

HUMAN_MODES = {
    "judge", "hybrid", "heuristic_plus_manual", "judge_or_policy",
    "acceptance_observation",
}

def load_cases(path: Path) -> list[dict]:
    cases = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        item = json.loads(raw)
        item["_line"] = line_no
        cases.append(item)
    return cases

def load_responses(path: Path | None) -> dict[str, dict]:
    if path is None:
        return {}
    result = {}
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        item = json.loads(raw)
        case_id = item.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"response line {line_no}: missing id")
        if case_id in result:
            raise ValueError(f"response line {line_no}: duplicate id {case_id}")
        result[case_id] = item
    return result

def evaluate(case: dict, response: dict | None) -> dict:
    mode = case["evaluation"]["mode"]
    if response is None:
        return {"status": "NOT_RUN", "mode": mode}
    # Provider adapters may return a normalized JSON object under "output".
    output = response.get("output", response)
    if not isinstance(output, dict):
        return {"status": "INVALID_RESPONSE", "mode": mode, "reason": "output is not an object"}
    if mode in HUMAN_MODES:
        return {"status": "REQUIRES_JUDGE", "mode": mode}
    # This first runner deliberately avoids guessing semantics for free-form model output.
    # Exact scoring is enabled only for explicitly declared fields.
    expected = case.get("expected", {})
    fields = case["evaluation"].get("fields")
    if mode == "exact" and fields:
        mismatches = {f: {"expected": expected.get(f), "actual": output.get(f)}
                      for f in fields if output.get(f) != expected.get(f)}
        return {"status": "PASS" if not mismatches else "FAIL", "mode": mode,
                **({"mismatches": mismatches} if mismatches else {})}
    return {"status": "UNSCOPED_RESPONSE", "mode": mode}

def main() -> int:
    parser = argparse.ArgumentParser(description="Run repository-grounded Content Factory model evals.")
    parser.add_argument("--eval", default="model_data/eval/content_factory_eval_v1.jsonl")
    parser.add_argument("--responses", help="Provider response JSONL; one object per case with an id.")
    parser.add_argument("--output", default="model_data/eval/latest_report.json")
    args = parser.parse_args()

    cases = load_cases(Path(args.eval))
    responses = load_responses(Path(args.responses) if args.responses else None)

    results = []
    for case in cases:
        results.append({
            "id": case["id"],
            "task": case["task"],
            "mode": case["evaluation"]["mode"],
            "result": evaluate(case, responses.get(case["id"])),
        })

    counts = {}
    for row in results:
        status = row["result"]["status"]
        counts[status] = counts.get(status, 0) + 1

    report = {
        "schema": "content_factory_model_eval_report_v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "case_count": len(cases),
        "response_count": len(responses),
        "counts": counts,
        "live_inference_performed": bool(responses),
        "results": results,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"MODEL EVAL RUN: {len(cases)} cases")
    print(f"RESPONSES: {len(responses)}")
    for key in sorted(counts):
        print(f"{key}: {counts[key]}")
    if not responses:
        print("LIVE INFERENCE: NOT PERFORMED (no provider response input supplied)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
