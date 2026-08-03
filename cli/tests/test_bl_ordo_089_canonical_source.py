from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from ordo.canonical_source import validate_canonical_source
from ordo.loader import load_package


def make_package(tmp_path: Path, source_text: str = "nodes: []\n", version: str = "1.0.0") -> Path:
    package = tmp_path / "package"
    (package / "source").mkdir(parents=True)
    (package / "source" / "program.ordo.yaml").write_text(source_text, encoding="utf-8")
    (package / "ordo.yml").write_text(f"name: demo\nversion: {version}\nsource: source/program.ordo.yaml\n", encoding="utf-8")
    return package


def test_canonical_source_pass_contains_physical_identity(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    report = validate_canonical_source(package, expected_version="1.0.0")
    assert report["status"] == "passed"
    identity = report["pass_evidence"]
    assert identity["verified_source_path"] == "source/program.ordo.yaml"
    assert identity["size_bytes"] > 0
    assert identity["mtime_ns"]
    assert len(identity["sha256"]) == 64


def test_stale_digest_and_version_block(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    report = validate_canonical_source(package, expected_sha256="0" * 64, expected_version="9.9.9")
    assert report["status"] == "blocked"
    codes = {item["code"] for item in report["errors"]}
    assert {"CANONICAL_SOURCE_SHA256_MISMATCH", "CANONICAL_SOURCE_VERSION_MISMATCH"} <= codes


def test_noncanonical_supplied_path_and_duplicate_name_block(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    duplicate = package / "copy" / "program.ordo.yaml"
    duplicate.parent.mkdir()
    duplicate.write_text("nodes: []\n", encoding="utf-8")
    report = validate_canonical_source(package, supplied_source=duplicate)
    assert report["status"] == "blocked"
    codes = {item["code"] for item in report["errors"]}
    assert "CANONICAL_SOURCE_PATH_MISMATCH" in codes
    assert "CANONICAL_SOURCE_DUPLICATE_NAME" in codes


def test_cli_emits_json_report(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    result = subprocess.run([sys.executable, "-m", "ordo.canonical_source", str(package)], cwd=Path(__file__).parents[1], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["schema_version"] == "ordo.canonical_source_identity.v1"


def test_package_loader_blocks_ambiguous_or_stale_source_copy(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    duplicate = package / "attachment" / "program.ordo.yaml"
    duplicate.parent.mkdir()
    duplicate.write_text("nodes: []\n", encoding="utf-8")
    try:
        load_package(package)
    except ValueError as exc:
        assert "canonical source check blocked" in str(exc)
    else:
        raise AssertionError("ambiguous package source must be rejected before a caller can load it")
