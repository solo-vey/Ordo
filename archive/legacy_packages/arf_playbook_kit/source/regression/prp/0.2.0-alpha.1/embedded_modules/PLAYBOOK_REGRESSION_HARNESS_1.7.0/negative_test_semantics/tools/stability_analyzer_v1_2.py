#!/usr/bin/env python3
import argparse, json, yaml
from pathlib import Path
from collections import Counter

def load(path):
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return json.loads(text) if p.suffix.lower() == ".json" else yaml.safe_load(text)

def evaluate_run(trace, fixture):
    observed = set(trace.get("violations", []))
    expected = {
        item["violation_id"]
        for item in fixture.get("expected_violations", [])
        if item.get("expectation") == "must_observe"
    }
    missing = sorted(expected - observed)
    unexpected = sorted(observed - expected)
    terminal = trace.get("terminal")
    success = terminal in set(fixture.get("success_terminals", ["SUCCESS", "T_GO", "SUCCESS_TERMINAL"]))
    unexpected_success = fixture.get("scenario_kind") == "negative_test" and success

    if missing:
        status = "expected_violation_missing"
    elif expected:
        status = "expected_violation_observed"
    else:
        status = "not_applicable"

    verdict = "PASS"
    if missing or unexpected or unexpected_success:
        verdict = "FAIL"

    return {
        "run_id": trace.get("run_id"),
        "expected_violation_status": status,
        "unexpected_violations": unexpected,
        "unexpected_success": unexpected_success,
        "route": trace.get("route"),
        "terminal": terminal,
        "verdict": verdict,
    }

def consistency(values):
    values = [v for v in values if v is not None]
    if not values:
        return 1.0
    return max(Counter(values).values()) / len(values)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--traces", nargs="+", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    fixture = load(args.fixture)
    runs = [evaluate_run(load(p), fixture) for p in args.traces]

    expected_rate = (
        sum(r["expected_violation_status"] == "expected_violation_observed" for r in runs) / len(runs)
    )
    unexpected_free_rate = (
        sum(not r["unexpected_violations"] for r in runs) / len(runs)
    )
    unexpected_success_free_rate = (
        sum(not r["unexpected_success"] for r in runs) / len(runs)
    )
    route_consistency = consistency([r["route"] for r in runs])
    terminal_consistency = consistency([r["terminal"] for r in runs])

    stable = all([
        expected_rate == 1.0,
        unexpected_free_rate == 1.0,
        unexpected_success_free_rate == 1.0,
        route_consistency == 1.0,
        terminal_consistency == 1.0,
    ])

    out = {
        "schema": "ordo.prh.stability_report.v1.2",
        "scenario_id": fixture["scenario_id"],
        "run_count": len(runs),
        "expected_violation_observed_rate": expected_rate,
        "unexpected_violation_free_rate": unexpected_free_rate,
        "unexpected_success_free_rate": unexpected_success_free_rate,
        "route_consistency": route_consistency,
        "terminal_consistency": terminal_consistency,
        "stable": stable,
        "runs": runs,
    }
    Path(args.output).write_text(
        yaml.safe_dump(out, sort_keys=False, allow_unicode=True),
        encoding="utf-8"
    )

if __name__ == "__main__":
    main()
