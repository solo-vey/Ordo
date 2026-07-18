from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

from ordo.flow_reuse_validation import detect_reuse_candidates
from ordo.graph_validation import validate_process_graph
from ordo.performance_budget import APF_LINT_MAX_RSS_MIB, APF_LINT_MAX_SECONDS, SYNTHETIC_GRAPH_MAX_SECONDS

ROOT = Path(__file__).resolve().parents[2]


def _node(node_id: str, nxt: str | None = None, terminal: bool = False) -> dict:
    node = {"id": node_id, "on_unmatched_input": "fail"}
    if nxt is not None:
        node["transition"] = {"next": nxt}
    if terminal:
        node["terminal"] = True
    return node


def test_large_linear_graph_uses_iterative_scc_and_finishes_within_budget():
    count = 5000
    nodes = [_node(f"N{i}", f"N{i+1}") for i in range(count - 1)] + [_node(f"N{count-1}", terminal=True)]
    source = {"nodes": nodes, "graph_contract": {"entry_node": "N0"}}
    started = time.perf_counter()
    report = validate_process_graph(source)
    elapsed = time.perf_counter() - started
    assert report["status"] == "passed", report["issues"][:3]
    assert elapsed < SYNTHETIC_GRAPH_MAX_SECONDS


def test_large_cyclic_reuse_scan_is_bounded_and_deterministic():
    count = 1200
    nodes = [_node(f"N{i}", f"N{(i+1) % count}") for i in range(count)]
    source = {"nodes": nodes}
    started = time.perf_counter()
    first = detect_reuse_candidates(source)
    second = detect_reuse_candidates(source)
    elapsed = time.perf_counter() - started
    assert first == second
    assert elapsed < SYNTHETIC_GRAPH_MAX_SECONDS


def test_real_apf_lint_fits_standard_ci_budget_without_skip():
    code = '''
import json, resource, sys, time, yaml
sys.path.insert(0, "cli")
from ordo.linter import lint_source
source = yaml.safe_load(open("packages/ordo_applied_project_factory/source/program.ordo.yaml", encoding="utf-8"))
started = time.perf_counter()
report = lint_source(source, {"test_cases": [{}]}, repo_root=".")
elapsed = time.perf_counter() - started
rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(json.dumps({"status": report["status"], "seconds": elapsed, "rss_mib": rss / 1024.0}))
'''
    proc = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, timeout=APF_LINT_MAX_SECONDS + 10)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout.strip().splitlines()[-1])
    assert result["status"] == "passed"
    assert result["seconds"] < APF_LINT_MAX_SECONDS
    assert result["rss_mib"] < APF_LINT_MAX_RSS_MIB


def test_delivery_gate_skip_heavy_flag_no_longer_deselects_or_skips_apf():
    spec = importlib.util.spec_from_file_location("build_release_archive", ROOT / "tools/build_release_archive.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert module.HEAVY_TESTS == set()
    source = (ROOT / "tools/build_release_archive.py").read_text(encoding="utf-8")
    assert 'results[pkg.name] = "skipped_heavy_env"' not in source
