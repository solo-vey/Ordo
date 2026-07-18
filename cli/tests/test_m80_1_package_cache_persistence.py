import json
from pathlib import Path
import pytest

from ordo.package_cache import (
    atomic_load_package_cache,
    compute_package_fingerprint,
    invalidate_package_cache_atomic,
    load_cache_state,
    persist_cache_state_atomic,
)


def make_package(root: Path, value: str = "one") -> Path:
    root.mkdir(parents=True)
    (root / "ordo.yml").write_text(f"name: {value}\n", encoding="utf-8")
    (root / "source").mkdir()
    (root / "source" / "program.ordo.yaml").write_text(f"value: {value}\n", encoding="utf-8")
    return root


def test_fingerprint_is_stable_and_content_sensitive(tmp_path):
    a = make_package(tmp_path / "a")
    b = make_package(tmp_path / "b")
    assert compute_package_fingerprint(a) == compute_package_fingerprint(b)
    (b / "ordo.yml").write_text("name: changed\n", encoding="utf-8")
    assert compute_package_fingerprint(a) != compute_package_fingerprint(b)


def test_fingerprint_rejects_symlink(tmp_path):
    package = make_package(tmp_path / "pkg")
    (package / "link").symlink_to(package / "ordo.yml")
    with pytest.raises(ValueError, match="symlinks"):
        compute_package_fingerprint(package)


def test_state_persistence_roundtrip(tmp_path):
    state = {
        "schema_version": "ordo.apf.package_cache_state.v1",
        "package_loaded": True,
        "package_version": "1.0.0",
        "package_fingerprint": "a" * 64,
        "unpacked_location": str(tmp_path),
        "manifest_validated": True,
        "source_of_truth_loaded": True,
        "cache_valid": True,
    }
    target = persist_cache_state_atomic(state, tmp_path / "state.json")
    assert target.exists()
    assert load_cache_state(target) == state


def test_atomic_load_and_replace(tmp_path):
    one = make_package(tmp_path / "one", "one")
    two = make_package(tmp_path / "two", "two")
    state_file = tmp_path / "session" / "cache-state.json"
    cache_root = tmp_path / "cache"
    first = atomic_load_package_cache(one, package_version="1.0.0", cache_root=cache_root, state_file=state_file, required_files=["ordo.yml"])
    assert first["status"] == "pass"
    assert (cache_root / "active" / "ordo.yml").read_text() == "name: one\n"
    second = atomic_load_package_cache(two, package_version="2.0.0", cache_root=cache_root, state_file=state_file, required_files=["ordo.yml"])
    assert second["status"] == "pass"
    assert (cache_root / "active" / "ordo.yml").read_text() == "name: two\n"
    assert load_cache_state(state_file)["package_version"] == "2.0.0"


def test_failed_replace_preserves_previous_cache_and_state(tmp_path):
    good = make_package(tmp_path / "good", "good")
    bad = make_package(tmp_path / "bad", "bad")
    state_file = tmp_path / "session" / "cache-state.json"
    cache_root = tmp_path / "cache"
    atomic_load_package_cache(good, package_version="1.0.0", cache_root=cache_root, state_file=state_file, required_files=["ordo.yml"])
    before_state = state_file.read_bytes()
    before_payload = (cache_root / "active" / "ordo.yml").read_bytes()
    with pytest.raises(ValueError, match="required file missing"):
        atomic_load_package_cache(bad, package_version="2.0.0", cache_root=cache_root, state_file=state_file, required_files=["missing.yml"])
    assert state_file.read_bytes() == before_state
    assert (cache_root / "active" / "ordo.yml").read_bytes() == before_payload


def test_expected_fingerprint_mismatch_does_not_mutate_cache(tmp_path):
    package = make_package(tmp_path / "pkg")
    with pytest.raises(ValueError, match="expected_fingerprint"):
        atomic_load_package_cache(package, package_version="1", cache_root=tmp_path / "cache", state_file=tmp_path / "state.json", expected_fingerprint="0" * 64)
    assert not (tmp_path / "state.json").exists()


def test_invalidate_persists_without_destroying_payload_by_default(tmp_path):
    package = make_package(tmp_path / "pkg")
    state_file = tmp_path / "state.json"
    cache_root = tmp_path / "cache"
    atomic_load_package_cache(package, package_version="1", cache_root=cache_root, state_file=state_file)
    result = invalidate_package_cache_atomic(state_file=state_file, reason="operator-request")
    assert result["state"]["cache_valid"] is False
    assert result["state"]["invalidation_reason"] == "operator-request"
    assert (cache_root / "active" / "ordo.yml").exists()


def test_invalid_json_state_fails_closed(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{bad", encoding="utf-8")
    with pytest.raises(ValueError, match="unreadable"):
        load_cache_state(path)
