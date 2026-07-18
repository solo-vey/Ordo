from pathlib import Path

from ordo.package_cache import CACHE_SCHEMA_VERSION, evaluate_package_reload_necessity, validate_package_cache_state


def state(tmp_path: Path):
    (tmp_path / "ordo.yml").write_text("name: x\n", encoding="utf-8")
    return {
        "schema_version": CACHE_SCHEMA_VERSION,
        "package_loaded": True,
        "package_version": "1.0.0",
        "package_fingerprint": "a" * 64,
        "unpacked_location": str(tmp_path),
        "manifest_validated": True,
        "source_of_truth_loaded": True,
        "cache_valid": True,
    }


def test_valid_state_and_cache_hit(tmp_path):
    s = state(tmp_path)
    assert validate_package_cache_state(s)["status"] == "pass"
    r = evaluate_package_reload_necessity(s, incoming_version="1.0.0", incoming_fingerprint="a" * 64, required_files=["ordo.yml"])
    assert r["decision"] == "cache_hit"
    assert r["trace_event"] == "PACKAGE_CACHE_HIT"
    assert r["active_node_must_remain_unchanged"] is True


def test_missing_state_is_cache_miss():
    r = evaluate_package_reload_necessity(None, incoming_version="1", incoming_fingerprint="a" * 64)
    assert r["reload_required"] is True
    assert r["trace_event"] == "PACKAGE_CACHE_MISS"


def test_version_change_requires_reload(tmp_path):
    r = evaluate_package_reload_necessity(state(tmp_path), incoming_version="2.0.0", incoming_fingerprint="a" * 64)
    assert "package_version_changed" in r["reasons"]


def test_fingerprint_change_requires_reload(tmp_path):
    r = evaluate_package_reload_necessity(state(tmp_path), incoming_version="1.0.0", incoming_fingerprint="b" * 64)
    assert "package_fingerprint_changed" in r["reasons"]


def test_missing_required_file_requires_reload(tmp_path):
    r = evaluate_package_reload_necessity(state(tmp_path), incoming_version="1.0.0", incoming_fingerprint="a" * 64, required_files=["missing.txt"])
    assert "required_file_missing:missing.txt" in r["reasons"]


def test_explicit_reload_requires_reload(tmp_path):
    r = evaluate_package_reload_necessity(state(tmp_path), incoming_version="1.0.0", incoming_fingerprint="a" * 64, explicit_reload=True)
    assert "explicit_reload_requested" in r["reasons"]


def test_invalid_state_fails_closed(tmp_path):
    s = state(tmp_path)
    s["package_fingerprint"] = "bad"
    r = evaluate_package_reload_necessity(s, incoming_version="1.0.0", incoming_fingerprint="bad")
    assert "cache_state_invalid" in r["reasons"]


def test_path_escape_is_reload_reason(tmp_path):
    r = evaluate_package_reload_necessity(state(tmp_path), incoming_version="1.0.0", incoming_fingerprint="a" * 64, required_files=["../secret"])
    assert "required_file_path_escape:../secret" in r["reasons"]
