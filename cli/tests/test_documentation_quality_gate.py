from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import yaml


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "manifests/DOCUMENTATION_QUALITY_GATE.json"
STARTER = ROOT / "examples/chat_first_playbook_starter"
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def heading_slugs(path: Path) -> set[str]:
    slugs = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            continue
        heading = re.sub(r"<[^>]+>", "", line.lstrip("#").strip().lower())
        heading = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE)
        slugs.add(heading.replace(" ", "-"))
    return slugs


def test_active_document_links_and_anchors_resolve() -> None:
    policy = load_json(POLICY_PATH)
    for document in policy["active_documents"]:
        path = ROOT / document
        assert path.is_file(), document
        for raw_target in LINK.findall(path.read_text(encoding="utf-8")):
            if raw_target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target, _, anchor = raw_target.partition("#")
            resolved = (path.parent / target).resolve()
            assert resolved.exists(), f"{document} -> {raw_target}"
            assert ROOT == resolved or ROOT in resolved.parents
            if anchor and resolved.is_file() and resolved.suffix == ".md":
                assert anchor in heading_slugs(resolved), f"{document} -> {raw_target}"


def test_chat_first_starter_archive_is_safe_and_reproducible() -> None:
    manifest = load_json(STARTER / "manifest.json")
    archive_path = STARTER / manifest["archive"]
    expected_members = [entry["path"] for entry in manifest["members"]]

    assert manifest["schema_version"] == "ordo.chat_first_starter_manifest.v1"
    assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == manifest["archive_sha256"]
    with ZipFile(archive_path) as archive:
        assert archive.namelist() == expected_members
        assert all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in archive.namelist())
        for entry in manifest["members"]:
            assert hashlib.sha256(archive.read(entry["path"])).hexdigest() == entry["sha256"]

    spec = importlib.util.spec_from_file_location("chat_starter_builder", ROOT / "tools/build_chat_first_starter.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    with TemporaryDirectory() as temp_dir:
        rebuilt = Path(temp_dir) / archive_path.name
        rebuilt_manifest = module.build(rebuilt)
        assert rebuilt.read_bytes() == archive_path.read_bytes()
        assert rebuilt_manifest == manifest


def test_packaged_release_claims_are_synchronized() -> None:
    identity = load_json(ROOT / "manifests/RELEASE_IDENTITY.json")
    version_state = load_json(ROOT / "manifests/VERSION_STATE.json")
    maturity = load_json(ROOT / "manifests/CURRENT_MATURITY_STATE.json")
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    maturity_md = (ROOT / "backlog/CURRENT_MATURITY_STATE.md").read_text(encoding="utf-8")

    release_id = identity["release_id"]
    language_version = identity["language_version"]
    framework_version = identity["framework_version"]
    assert version_state["release_id"] == release_id
    assert version_state["language"]["version"] == language_version
    assert version_state["framework"]["version"] == framework_version
    assert maturity["release"]["release_id"] == release_id
    assert maturity["release"]["version"] == language_version
    assert maturity["release"]["framework_version"] == framework_version
    assert citation["version"] == release_id
    for value in (release_id, language_version, framework_version):
        assert value in readme
        assert value in maturity_md


def test_historical_link_exceptions_are_exact_and_bounded() -> None:
    policy = load_json(POLICY_PATH)
    exceptions = policy["bounded_historical_link_exceptions"]
    assert len(exceptions) == 3
    assert all("*" not in entry["path"] for entry in exceptions)
    assert all((ROOT / entry["path"]).is_file() for entry in exceptions)
