from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = ROOT / "model" / "test-impact.yaml"


def load_model(path: Path = DEFAULT_MODEL) -> dict[str, Any]:
    # JSON is a valid YAML 1.2 subset; using stdlib keeps the impact engine dependency-free.
    with path.open("r", encoding="utf-8") as handle:
        model = json.load(handle)
    if not isinstance(model, dict):
        raise ValueError("test-impact model must be an object")
    return model


def validate_model(model: dict[str, Any]) -> None:
    gates = model.get("gates")
    if not isinstance(gates, dict) or not gates:
        raise ValueError("model.gates must be a non-empty object")

    known = set(gates)
    for gate_id, gate in gates.items():
        if not isinstance(gate, dict):
            raise ValueError(f"{gate_id} must be an object")
        deps = gate.get("depends_on", [])
        if not isinstance(deps, list) or not all(isinstance(dep, str) for dep in deps):
            raise ValueError(f"{gate_id}.depends_on must be an array of gate ids")
        unknown = set(deps) - known
        if unknown:
            raise ValueError(f"{gate_id} depends on unknown gates: {sorted(unknown)}")

    policy = model.get("policy") or {}
    always = policy.get("always_gates", [])
    if not isinstance(always, list) or not set(always).issubset(known):
        raise ValueError("policy.always_gates contains unknown gates")

    patterns = model.get("file_rules", [])
    if not isinstance(patterns, list):
        raise ValueError("file_rules must be an array")
    for rule in patterns:
        if not isinstance(rule, dict) or not isinstance(rule.get("pattern"), str):
            raise ValueError("every file rule requires a pattern")
        rule_gates = rule.get("gates", [])
        if not isinstance(rule_gates, list) or not set(rule_gates).issubset(known):
            raise ValueError(f"file rule {rule.get('pattern')} contains unknown gates")

    indegree = {gate_id: 0 for gate_id in known}
    children: dict[str, list[str]] = defaultdict(list)
    for gate_id, gate in gates.items():
        for dep in gate.get("depends_on", []):
            indegree[gate_id] += 1
            children[dep].append(gate_id)
    queue = deque(sorted(gate_id for gate_id, degree in indegree.items() if degree == 0))
    visited = 0
    while queue:
        current = queue.popleft()
        visited += 1
        for child in sorted(children[current]):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if visited != len(known):
        raise ValueError("gate dependency graph contains a cycle")


def _is_no_gate_file(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def direct_gates_for_files(model: dict[str, Any], files: list[str]) -> tuple[set[str], list[str]]:
    gates: set[str] = set()
    unknown: list[str] = []
    rules = model.get("file_rules", [])
    no_gate_patterns = (model.get("policy") or {}).get("no_gate_patterns", [])

    for path in files:
        matched = False
        for rule in rules:
            if fnmatch.fnmatch(path, str(rule["pattern"])):
                matched = True
                gates.update(rule.get("gates", []))
        if not matched and not _is_no_gate_file(path, no_gate_patterns):
            unknown.append(path)
    return gates, unknown


def downstream_closure(model: dict[str, Any], initial: set[str]) -> set[str]:
    gates = model["gates"]
    reverse: dict[str, set[str]] = defaultdict(set)
    for gate_id, gate in gates.items():
        for dep in gate.get("depends_on", []):
            reverse[dep].add(gate_id)

    closure = set(initial)
    queue = deque(sorted(initial))
    while queue:
        current = queue.popleft()
        for child in sorted(reverse[current]):
            if child not in closure:
                closure.add(child)
                queue.append(child)
    return closure


def _risk_rank(value: str) -> int:
    return {"R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4}.get(value, 9)


def order_gates(model: dict[str, Any], selected: set[str]) -> list[str]:
    gates = model["gates"]
    indegree = {gate_id: 0 for gate_id in selected}
    children: dict[str, list[str]] = defaultdict(list)

    for gate_id in selected:
        for dep in gates[gate_id].get("depends_on", []):
            if dep in selected:
                indegree[gate_id] += 1
                children[dep].append(gate_id)

    def key(gate_id: str) -> tuple[int, str]:
        return (_risk_rank(str(gates[gate_id].get("risk", "R9"))), gate_id)

    queue = sorted((gate_id for gate_id, degree in indegree.items() if degree == 0), key=key)
    ordered: list[str] = []

    while queue:
        current = queue.pop(0)
        ordered.append(current)
        for child in sorted(children[current], key=key):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
        queue.sort(key=key)

    if len(ordered) != len(selected):
        raise ValueError("selected gate set contains a dependency cycle")
    return ordered


def plan_for_files(model: dict[str, Any], files: list[str]) -> dict[str, Any]:
    validate_model(model)
    normalized = sorted(dict.fromkeys(path.replace("\\", "/") for path in files if path.strip()))
    direct, unknown = direct_gates_for_files(model, normalized)

    policy = model.get("policy") or {}
    fallback_used = bool(unknown)
    if fallback_used and policy.get("unknown_files") != "fail_closed":
        raise ValueError("unknown file policy must be fail_closed")

    if fallback_used:
        fallback_risks = set(policy.get("fallback_risks", ["R0", "R1"]))
        direct.update(
            gate_id
            for gate_id, gate in model["gates"].items()
            if gate.get("risk") in fallback_risks
        )

    meaningful_change = bool(normalized) and any(
        not _is_no_gate_file(path, policy.get("no_gate_patterns", []))
        for path in normalized
    )
    if meaningful_change:
        direct.update(policy.get("always_gates", []))

    closure = downstream_closure(model, direct)
    return {
        "changed_files": normalized,
        "unknown_files": sorted(unknown),
        "fallback_used": fallback_used,
        "direct_gates": sorted(direct),
        "closure": sorted(closure),
        "ordered_gates": order_gates(model, closure),
    }


def changed_files_from_git(base: str | None, head: str | None) -> list[str]:
    resolved_head = head or subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    resolved_base = base
    if not resolved_base or set(resolved_base) == {"0"}:
        try:
            resolved_base = subprocess.check_output(["git", "rev-parse", f"{resolved_head}^"], text=True).strip()
        except subprocess.CalledProcessError as exc:
            raise ValueError("cannot infer a parent commit for impact analysis") from exc

    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", resolved_base, resolved_head],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute dependency-aware Content Factory test gates.")
    parser.add_argument("--base", help="Base git revision.")
    parser.add_argument("--head", help="Head git revision.")
    parser.add_argument("--files", nargs="*", help="Explicit changed files; skips git diff when supplied.")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        model = load_model(args.model)
        files = args.files if args.files else changed_files_from_git(args.base, args.head)
        plan = plan_for_files(model, files)
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"impact analysis failed: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print("Changed files:")
        for path in plan["changed_files"]:
            print(f"  - {path}")
        print(f"Unknown files: {len(plan['unknown_files'])}")
        for path in plan["unknown_files"]:
            print(f"  ! {path}")
        print(f"Fallback used: {plan['fallback_used']}")
        print("Direct gates: " + (", ".join(plan["direct_gates"]) or "none"))
        print("Closure: " + (", ".join(plan["closure"]) or "none"))
        print("Execution order: " + (", ".join(plan["ordered_gates"]) or "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
