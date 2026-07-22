from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "manifests/ROOT_RELOCATION_CONTRACT.json"
CHECKSUM_PATH = ROOT / "SHA256SUMS.txt"
REPORT_MANIFEST_PATH = ROOT / "reports/CANONICAL_REPORTS_MANIFEST.yaml"
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^]]*]\(([^)]+)\)")
ROOT_FILES = {
    ".gitignore",
    "CHANGELOG.md",
    "CITATION.cff",
    "CODE_OF_CONDUCT.md",
    "COMMERCIAL_LICENSE.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "LICENSE.md",
    "NOTICE.md",
    "README.md",
    "SECURITY.md",
    "SHA256SUMS.txt",
    "SUPPORT.md",
    "generated_artifacts_policy.yaml",
    "repo_hygiene.yml",
}


def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def relocations(contract: dict) -> list[dict]:
    return [entry for group in contract["groups"] for entry in group["relocations"]]


def root_checksums() -> dict[str, str]:
    entries = {}
    for line in CHECKSUM_PATH.read_text(encoding="utf-8").splitlines():
        digest, path = line.split("  ", 1)
        entries[path] = digest
    return entries


def test_relocation_contract_is_complete_and_unique() -> None:
    contract = load_contract()
    entries = relocations(contract)
    sources = [entry["source_path"] for entry in entries]
    destinations = [entry["canonical_path"] for entry in entries]

    assert contract["schema_version"] == "ordo.root_relocation_contract.v1"
    assert contract["entry_count"] == len(entries) == 48
    assert len(sources) == len(set(sources))
    assert len(destinations) == len(set(destinations))
    assert all(Path(source).parent == Path(".") for source in sources)


def test_repository_root_contains_only_canonical_front_door_files() -> None:
    actual = {path.name for path in ROOT.iterdir() if path.is_file()}
    assert actual == ROOT_FILES


def test_relocated_sources_are_absent_and_destinations_exist() -> None:
    for entry in relocations(load_contract()):
        assert not (ROOT / entry["source_path"]).exists(), entry["source_path"]
        assert (ROOT / entry["canonical_path"]).is_file(), entry["canonical_path"]


def test_active_consumers_use_canonical_paths() -> None:
    for consumer in load_contract()["active_consumers"]:
        text = (ROOT / consumer["path"]).read_text(encoding="utf-8")
        for required_path in consumer["required_paths"]:
            assert required_path in text, f"{consumer['path']} -> {required_path}"


def test_relocation_indexes_have_resolvable_relative_links() -> None:
    for document in load_contract()["link_indexes"]:
        path = ROOT / document
        for raw_target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
            target = raw_target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            assert (path.parent / target).resolve().exists(), f"{document} -> {raw_target}"


def test_root_checksums_cover_relocated_destinations() -> None:
    checksums = root_checksums()
    for entry in relocations(load_contract()):
        source = entry["source_path"]
        destination = entry["canonical_path"]
        assert source not in checksums
        assert destination in checksums
        assert hashlib.sha256((ROOT / destination).read_bytes()).hexdigest() == checksums[destination]


def test_canonical_report_manifest_hashes_relocated_reports() -> None:
    manifest = yaml.safe_load(REPORT_MANIFEST_PATH.read_text(encoding="utf-8"))
    declared = {entry["path"]: entry["sha256"] for entry in manifest["entries"]}
    report_paths = {
        entry["canonical_path"]
        for entry in relocations(load_contract())
        if entry["canonical_path"].startswith("reports/")
    }

    for repository_path in report_paths:
        report_path = Path(repository_path).relative_to("reports").as_posix()
        assert report_path in declared
        assert hashlib.sha256((ROOT / repository_path).read_bytes()).hexdigest() == declared[report_path]


def test_external_historical_archive_is_explicitly_outside_the_relocation_set() -> None:
    archive = load_contract()["external_archives"]
    assert archive == [{
        "archive_id": "historical-provenance-2026-07-22",
        "locator_path": "manifests/external_archives/HISTORICAL_PROVENANCE_2026_07_22.json",
        "former_canonical_paths": [
            "TRANSFER_2026-07-14/",
            "recovery/2026-07-14/",
            "archive/handoffs/",
            "docs/handoff/legacy-root/",
            "docs/releases/legacy-root/",
            "docs/status/legacy-root/",
            "manifests/releases/legacy-root/",
            "checkpoints/",
        ],
    }]
