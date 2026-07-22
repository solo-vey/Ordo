import json
from pathlib import Path

from utilities.ordo_pathwalk.runner.scorer import (
    actual_path_from_state,
    cell_match_rate,
    direct_compiled_access_detected,
    load_actual_state,
    runtime_metadata,
)


def test_cell_match_rate_counts_pairs():
    actual = [("A", "x"), ("B", "y"), ("C", "z")]
    truth = [("A", "x"), ("B", "no"), ("C", "z")]
    assert cell_match_rate(actual, truth) == 2 / 3


def test_m60_snapshot_envelope_state_load(tmp_path: Path):
    d = tmp_path / "pkg" / "runtime" / "state_snapshots"
    d.mkdir(parents=True)
    (d / "SESSION-001.json").write_text(json.dumps({"session_chain": {}, "state": {"path_complete": True}}))
    assert load_actual_state(tmp_path / "pkg") == {"path_complete": True}


def test_actual_path_from_state():
    state = {"path_node_step_0": "N0", "path_step_0": "left"}
    assert actual_path_from_state(state, 2) == [("N0", "left"), (None, None)]


def test_direct_compiled_access_detected():
    transcript = [{"tool_calls_made": [{"command": "cat compiled/program.ir.json"}]}]
    assert direct_compiled_access_detected(transcript) is True


def test_runtime_metadata_hashes(tmp_path: Path):
    pkg = tmp_path / "pkg"
    (pkg / "compiled").mkdir(parents=True)
    (pkg / "runtime").mkdir()
    (pkg / "compiled" / "program.ir.json").write_text("{}")
    (pkg / "compiled" / "targets.manifest.json").write_text(json.dumps({"targets": {"json-ir": {}}}))
    (pkg / "runtime" / "session.ordo.trace").write_text("session {}")
    (pkg / "ordo.runtime.json").write_text(json.dumps({"runtime_view": "ordo-code", "runtime_protocol": "M60.4"}))
    m = runtime_metadata(pkg)
    assert m["runtime_view"] == "ordo-code"
    assert m["canonical_ir_hash"].startswith("sha256:")
    assert "json-ir" in m["targets"]
