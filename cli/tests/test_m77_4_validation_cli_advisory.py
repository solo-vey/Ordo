from copy import deepcopy

from ordo.flow_reuse_validation import detect_reuse_candidates, validate_flow_reuse
from ordo.linter import lint_source


def base_source():
    return {
        "ordo": {"version": "0.12", "package": "demo.pkg", "control_level": "standard", "execution_mode": "full_runtime"},
        "nodes": [
            {"id": "A1", "prompt": "Review", "on_unmatched_input": "retry", "transition": {"next": "A2"}},
            {"id": "A2", "prompt": "Close", "on_unmatched_input": "retry", "transition": {"next": "DONE"}},
            {"id": "B1", "prompt": "Review", "on_unmatched_input": "retry", "transition": {"next": "B2"}},
            {"id": "B2", "prompt": "Close", "on_unmatched_input": "retry", "transition": {"next": "DONE"}},
        ],
        "graph_contract": {"entry_node": "A1", "external_terminal_targets": ["DONE"], "allowed_cycle_regions": []},
    }


def test_advisory_detection_is_non_blocking():
    source = base_source()
    candidates = detect_reuse_candidates(source)
    assert candidates
    report = validate_flow_reuse(source)
    assert report["status"] == "passed"
    assert report["summary"]["reuse_candidates"] >= 1
    assert all(i["severity"] == "info" for i in report["issues"])


def test_lint_exposes_flow_reuse_subreport_without_error():
    report = lint_source(base_source())
    assert report["flow_reuse_validation"]["status"] == "passed"
    assert report["summary"]["errors"] == 2  # B1 and B2 are intentionally unreachable; advisory remains non-blocking.
    assert any(i["code"] == "FLOW_REUSE_CANDIDATE" for i in report["issues"])


def test_invalid_authored_reference_blocks():
    source = base_source()
    source["flow_reuse"] = {
        "references": [{
            "id": "REF.X", "namespace": "demo", "tail_id": "MISSING", "entry": "N",
            "namespace_policy": "inherit"
        }]
    }
    report = validate_flow_reuse(source)
    assert report["status"] == "failed"
    assert report["issues"][0]["code"] == "FLOW_REUSE_INVALID"


def test_no_automatic_rewrite_marker():
    candidate = detect_reuse_candidates(base_source())[0]
    assert candidate["automatic_rewrite"] is False
