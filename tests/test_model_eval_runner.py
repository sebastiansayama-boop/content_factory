from pathlib import Path
from scripts.run_model_eval import load_cases

def test_model_eval_runner_loads_50_cases():
    path = Path("model_data/eval/content_factory_eval_v1.jsonl")
    cases = load_cases(path)
    assert len(cases) == 50
    assert len({case["id"] for case in cases}) == 50
