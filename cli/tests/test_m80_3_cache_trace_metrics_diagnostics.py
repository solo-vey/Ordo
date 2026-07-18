from pathlib import Path
import json
import ordo.package_cache as pc


def valid_state(tmp_path: Path):
    payload = tmp_path / "cache" / "active"
    payload.mkdir(parents=True)
    (payload / "ordo.yml").write_text("name: demo\n", encoding="utf-8")
    state = {
        "schema_version": pc.CACHE_SCHEMA_VERSION,
        "package_loaded": True,
        "package_version": "1",
        "package_fingerprint": "a" * 64,
        "unpacked_location": str(payload),
        "manifest_validated": True,
        "source_of_truth_loaded": True,
        "cache_valid": True,
    }
    state_file = tmp_path / "state.json"
    pc.persist_cache_state_atomic(state, state_file)
    return state_file


def test_trace_append_and_metrics(tmp_path):
    trace = tmp_path / "trace.jsonl"
    pc.append_cache_trace_event(trace, event="PACKAGE_CACHE_HIT")
    pc.append_cache_trace_event(trace, event="PACKAGE_RELOAD_REQUIRED", details={"reason": "version"})
    metrics = pc.compute_cache_metrics(trace)
    assert metrics["counts"]["PACKAGE_CACHE_HIT"] == 1
    assert metrics["counts"]["PACKAGE_RELOAD_REQUIRED"] == 1
    assert metrics["cache_hit_ratio"] == 0.5


def test_unknown_trace_event_rejected(tmp_path):
    try:
        pc.append_cache_trace_event(tmp_path / "t", event="BAD")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown event must fail")


def test_diagnostics_pass_for_valid_cache(tmp_path):
    state_file = valid_state(tmp_path)
    result = pc.diagnose_package_cache(state_file, required_files=["ordo.yml"])
    assert result["status"] == "pass"


def test_diagnostics_fail_for_missing_required_file(tmp_path):
    state_file = valid_state(tmp_path)
    result = pc.diagnose_package_cache(state_file, required_files=["missing.yml"])
    assert result["status"] == "fail"
    assert any(x["code"] == "CACHE_REQUIRED_FILE_MISSING" for x in result["findings"])


def test_malformed_trace_is_warning(tmp_path):
    state_file = valid_state(tmp_path)
    trace = tmp_path / "trace.jsonl"
    trace.write_text("not-json\n", encoding="utf-8")
    result = pc.diagnose_package_cache(state_file, trace_file=trace)
    assert result["status"] == "warn"
