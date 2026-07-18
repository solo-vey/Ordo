from pathlib import Path
import shutil
import yaml
from ordo.template_tooling import validate_template_registry

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "examples" / "template_tooling"


def test_example_registry_passes():
    report = validate_template_registry(FIXTURE / "template_registry.yaml")
    assert report["status"] == "passed", report
    assert report["entry_count"] == 1


def test_duplicate_template_version_fails(tmp_path):
    shutil.copytree(FIXTURE, tmp_path / "pkg")
    p = tmp_path / "pkg" / "template_registry.yaml"
    data = yaml.safe_load(p.read_text())
    data["templates"].append(dict(data["templates"][0]))
    p.write_text(yaml.safe_dump(data, sort_keys=False))
    report = validate_template_registry(p)
    assert report["status"] == "failed"
    assert any(i["code"] == "TEMPLATE_REGISTRY_DUPLICATE_ENTRY" for i in report["issues"])


def test_stale_checksum_fails(tmp_path):
    shutil.copytree(FIXTURE, tmp_path / "pkg")
    p = tmp_path / "pkg" / "template_registry.yaml"
    data = yaml.safe_load(p.read_text())
    data["templates"][0]["sha256"] = "0" * 64
    p.write_text(yaml.safe_dump(data, sort_keys=False))
    report = validate_template_registry(p)
    assert any(i["code"] == "TEMPLATE_REGISTRY_STALE_CHECKSUM" for i in report["issues"])


def test_metadata_mismatch_fails(tmp_path):
    shutil.copytree(FIXTURE, tmp_path / "pkg")
    p = tmp_path / "pkg" / "template_registry.yaml"
    data = yaml.safe_load(p.read_text())
    data["templates"][0]["version"] = "9.9.9"
    p.write_text(yaml.safe_dump(data, sort_keys=False))
    report = validate_template_registry(p)
    assert any(i["code"] == "TEMPLATE_REGISTRY_METADATA_MISMATCH" for i in report["issues"])


def test_multiple_active_versions_fail(tmp_path):
    shutil.copytree(FIXTURE, tmp_path / "pkg")
    src = tmp_path / "pkg" / "qa_package.template.yaml"
    second = tmp_path / "pkg" / "qa_package_v3.template.yaml"
    contract = yaml.safe_load(src.read_text())
    contract["version"] = "3.0.0"
    second.write_text(yaml.safe_dump(contract, sort_keys=False))
    import hashlib
    data = yaml.safe_load((tmp_path / "pkg" / "template_registry.yaml").read_text())
    entry = dict(data["templates"][0])
    entry["version"] = "3.0.0"
    entry["contract_ref"] = second.name
    entry["sha256"] = hashlib.sha256(second.read_bytes()).hexdigest()
    data["templates"].append(entry)
    p = tmp_path / "pkg" / "template_registry.yaml"
    p.write_text(yaml.safe_dump(data, sort_keys=False))
    report = validate_template_registry(p)
    assert any(i["code"] == "TEMPLATE_REGISTRY_MULTIPLE_ACTIVE_VERSIONS" for i in report["issues"])
