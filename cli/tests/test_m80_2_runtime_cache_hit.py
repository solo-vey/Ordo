from pathlib import Path

import ordo.package_cache as pc


def make_package(root: Path, value: str = "one") -> Path:
    root.mkdir(parents=True)
    (root / "ordo.yml").write_text(f"name: {value}\n", encoding="utf-8")
    (root / "source").mkdir()
    (root / "source" / "program.ordo.yaml").write_text(f"value: {value}\n", encoding="utf-8")
    return root


def test_second_ensure_is_cache_hit_without_source_read_or_unpack(tmp_path, monkeypatch):
    package = make_package(tmp_path / "pkg")
    cache_root = tmp_path / "cache"
    state_file = tmp_path / "session" / "state.json"

    first = pc.ensure_package_cache(
        package,
        package_version="1.0.0",
        cache_root=cache_root,
        state_file=state_file,
        required_files=["ordo.yml", "source/program.ordo.yaml"],
    )
    assert first["decision"] == "reloaded"

    def fail_fingerprint(*args, **kwargs):
        raise AssertionError("source package must not be reread on cache hit")

    def fail_load(*args, **kwargs):
        raise AssertionError("package must not be unpacked on cache hit")

    monkeypatch.setattr(pc, "compute_package_fingerprint", fail_fingerprint)
    monkeypatch.setattr(pc, "atomic_load_package_cache", fail_load)

    second = pc.ensure_package_cache(
        package,
        package_version="1.0.0",
        cache_root=cache_root,
        state_file=state_file,
        required_files=["ordo.yml", "source/program.ordo.yaml"],
    )
    assert second["decision"] == "cache_hit"
    assert second["source_read_performed"] is False
    assert second["unpack_performed"] is False


def test_missing_cached_file_forces_reload(tmp_path):
    package = make_package(tmp_path / "pkg")
    cache_root = tmp_path / "cache"
    state_file = tmp_path / "state.json"
    pc.ensure_package_cache(package, package_version="1", cache_root=cache_root, state_file=state_file, required_files=["ordo.yml"])
    (cache_root / "active" / "ordo.yml").unlink()
    result = pc.ensure_package_cache(package, package_version="1", cache_root=cache_root, state_file=state_file, required_files=["ordo.yml"])
    assert result["decision"] == "reloaded"
    assert "required_file_missing:ordo.yml" in result["reload_reason"]


def test_version_change_forces_reload(tmp_path):
    package = make_package(tmp_path / "pkg")
    cache_root = tmp_path / "cache"
    state_file = tmp_path / "state.json"
    pc.ensure_package_cache(package, package_version="1", cache_root=cache_root, state_file=state_file)
    result = pc.ensure_package_cache(package, package_version="2", cache_root=cache_root, state_file=state_file)
    assert result["decision"] == "reloaded"
    assert "package_version_changed" in result["reload_reason"]


def test_explicit_reload_bypasses_cache_hit(tmp_path):
    package = make_package(tmp_path / "pkg")
    cache_root = tmp_path / "cache"
    state_file = tmp_path / "state.json"
    pc.ensure_package_cache(package, package_version="1", cache_root=cache_root, state_file=state_file)
    result = pc.ensure_package_cache(package, package_version="1", cache_root=cache_root, state_file=state_file, explicit_reload=True)
    assert result["decision"] == "reloaded"
    assert "explicit_reload_requested" in result["reload_reason"]
