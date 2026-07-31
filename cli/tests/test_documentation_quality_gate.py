from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import yaml


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "manifests/DOCUMENTATION_QUALITY_GATE.json"
STARTER = ROOT / "examples/chat_first_playbook_starter"
ARF_KIT = ROOT / "packages/arf_playbook_kit"
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
UKRAINIAN = re.compile(r"[\u0400-\u052f]")


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


def test_arf_playbook_kit_manifest_is_safe_and_reproducible() -> None:
    current = load_json(ROOT / "manifests/ARF_PLAYBOOK_KIT_CURRENT.json")
    manifest = load_json(ARF_KIT / "manifest.json")
    assert current["archive_filename"] == manifest["archive"]
    assert current["release_tag"] == f"arf-playbook-kit-v{current['version']}"
    assert current["download_url"].endswith(f"/{manifest['archive']}")
    assert current["sha256_url"].endswith(f"/{manifest['archive']}.sha256")
    assert current["archive_sha256"] == manifest["archive_sha256"]

    spec = importlib.util.spec_from_file_location("arf_kit_builder", ROOT / "tools/build_arf_playbook_kit.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    with TemporaryDirectory() as temp_dir:
        first = Path(temp_dir) / manifest["archive"]
        second = Path(temp_dir) / "second.zip"
        first_manifest = module.build(first)
        second_manifest = module.build(second)
        assert first.read_bytes() == second.read_bytes()
        assert first_manifest["archive_sha256"] == second_manifest["archive_sha256"]
        assert {
            key: value
            for key, value in first_manifest.items()
            if key != "archive"
        } == {
            key: value
            for key, value in second_manifest.items()
            if key != "archive"
        }
        assert first_manifest["version"] == (ARF_KIT / "VERSION").read_text(encoding="utf-8").strip()
        assert first_manifest["schema_version"] == "ordo.arf_playbook_kit.v2"
        assert first_manifest["package_kind"] == "standalone_arf_playbook_factory"
        with ZipFile(first) as archive:
            expected = [*[entry["path"] for entry in first_manifest["members"]], "KIT_MANIFEST.json"]
            assert archive.namelist() == expected
            assert all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in expected)
            internal_manifest = json.loads(archive.read("KIT_MANIFEST.json"))
            assert internal_manifest["version"] == first_manifest["version"]
            for required in (
                "START_HERE_RUNTIME_MODE.md",
                "START_PROMPT_RUNTIME_MODE.md",
                "compiled/program.ir.json",
                "compiled/targets.manifest.json",
                "cli_embedded/ordo",
                "source/program.ordo.yaml",
                "source/module_manifest.yaml",
                "tests/test_cases.yaml",
                "workspace/README.md",
                "guides/START_PROMPT.md",
                "guides/ARF_PACKAGE_README.md",
                "migration/README.md",
                "migration/scope_confirmation.yaml",
                "migration/domain_model.md",
                "migration/parameter_registry.yaml",
                "migration/traceability_matrix.yaml",
                "migration/materialization_gate_catalog.yaml",
                "migration/readiness_report.yaml",
                "utilities/README.md",
                "utilities/ordo_pathwalk/README.md",
                "utilities/ordo_pathwalk/cli.py",
                "utilities/ordo_visual_graph_generator/README.md",
                "utilities/ordo_visual_graph_generator/ordo_graph.py",
                "utilities/playbook_lifecycle/README.md",
                "utilities/playbook_regression_harness/README.md",
                "release_tools/build_arf_playbook_kit.py",
                "release_tools/build_release_archive.py",
                "release_tools/release_integrity.py",
                "release_tools/check_english_only_policy.py",
                "language/registries/antipattern_registry.v1.json",
                "language/registries/fundamental_antipattern_registry.v1.json",
                "language/integration/antipattern_gate_adapter.py",
                "language/runtime/antipattern_runtime.py",
                "language/runtime/fixtures/antipattern_integration_cases.v1.json",
                "integration/test_antipattern_all_rules_e2e.py",
                "integration/validate_antipattern_rule_coverage.py",
            ):
                assert required in archive.namelist()
            package_readme = archive.read("guides/ARF_PACKAGE_README.md").decode("utf-8")
            assert "## Included capabilities" in package_readme
            assert "## Not included" in package_readme
            migration_readme = archive.read("migration/README.md").decode("utf-8")
            assert "collect -> save -> review -> gate -> checkpoint -> next" in migration_readme
            user_entry_documents = (
                "START_HERE_RUNTIME_MODE.md",
                "START_PROMPT_RUNTIME_MODE.md",
                "PLAYBOOK_LAWS.md",
                "workspace/README.md",
                *tuple(name for name in archive.namelist() if name.startswith("guides/") and name.endswith(".md")),
            )
            for name in user_entry_documents:
                assert not UKRAINIAN.search(archive.read(name).decode("utf-8")), name
            assert not any(name.startswith("reports/") for name in archive.namelist())
            runtime_root = Path(temp_dir) / "runtime-package"
            archive.extractall(runtime_root)

        for command in ("runtime-status", "verify-targets"):
            result = subprocess.run(
                [
                    sys.executable,
                    str(runtime_root / "cli_embedded" / "ordo"),
                    command,
                    str(runtime_root),
                ],
                text=True,
                capture_output=True,
            )
            assert result.returncode == 0, result.stdout + result.stderr

        for command in (
            "integration/validate_antipattern_rule_coverage.py",
            "integration/test_antipattern_fundamental_taxonomy_binding.py",
            "integration/test_antipattern_hook_runtime.py",
            "integration/test_antipattern_state_evidence_contract.py",
            "integration/test_antipattern_all_rules_e2e.py",
        ):
            result = subprocess.run(
                [sys.executable, str(runtime_root / command), str(runtime_root)]
                if command.endswith("validate_antipattern_rule_coverage.py")
                else [sys.executable, str(runtime_root / command)],
                text=True,
                capture_output=True,
            )
            assert result.returncode == 0, result.stdout + result.stderr


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
