from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CHECKSUM_PATH = ROOT / "SHA256SUMS.txt"
ENTRY = re.compile(r"^([0-9a-f]{64})  (.+)$")


def tracked_repository_files() -> set[str] | None:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return {
        path
        for path in result.stdout.splitlines()
        if Path(path).name != "SHA256SUMS.txt"
    }


def checksum_entries() -> dict[str, str]:
    entries: dict[str, str] = {}
    paths: list[str] = []

    for line in CHECKSUM_PATH.read_text(encoding="utf-8").splitlines():
        match = ENTRY.fullmatch(line)
        assert match is not None, f"malformed checksum entry: {line!r}"
        digest, path = match.groups()
        assert path not in entries, f"duplicate checksum entry: {path}"
        entries[path] = digest
        paths.append(path)

    assert paths == sorted(paths), "SHA256SUMS.txt paths must be sorted"
    return entries


def test_root_checksum_manifest_exactly_covers_tracked_payload() -> None:
    entries = checksum_entries()
    tracked = tracked_repository_files()
    if tracked is None:
        pytest.skip("exact tracked-file coverage requires Git metadata")

    assert set(entries) == tracked, {
        "missing": sorted(tracked - set(entries)),
        "stale": sorted(set(entries) - tracked),
    }


def test_root_checksum_manifest_hashes_match_repository_bytes() -> None:
    for path, expected in checksum_entries().items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        assert actual == expected, path
