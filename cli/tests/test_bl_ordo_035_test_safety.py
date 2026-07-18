from __future__ import annotations
import importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_gate():
    spec = importlib.util.spec_from_file_location("build_release_archive", ROOT / "tools" / "build_release_archive.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_execution_classification_declares_serial_safety_classes():
    data = json.loads((ROOT / "manifests" / "TEST_EXECUTION_CLASSIFICATION.json").read_text())
    serial = data["serial_files"]
    assert serial["test_cli_workflow.py"] == "workspace_mutating"
    assert serial["test_bl_ordo_025_linter_performance.py"] == "performance_sensitive"
    assert all((ROOT / "cli" / "tests" / name).is_file() for name in serial)


def test_release_gate_loads_machine_readable_serial_classification():
    source = (ROOT / "tools" / "build_release_archive.py").read_text()
    assert "TEST_EXECUTION_CLASSIFICATION.json" in source
    assert "declared_serial" in source
    assert "results.append(run_batch(len(batches), serial_files))" in source


def test_negative_fixture_mutation_proves_change():
    source = (ROOT / "cli" / "tests" / "test_cli_workflow.py").read_text()
    assert "self.assertNotEqual(" in source
    assert "expected to inject a trust_class mismatch" in source
    assert "re.sub(" in source


def test_silent_fixture_noop_is_registered_blocking():
    registry = json.loads((ROOT / "language" / "registries" / "antipattern_registry.v1.json").read_text())
    item = next(x for x in registry["items"] if x["id"] == "SILENT_FIXTURE_NOOP")
    assert item["enforcement"] == "blocking"
    assert "TEST_FIXTURE_MUTATION_ASSERT" in item["detection"]["rule_ids"]


def test_safety_audit_reports_passed(tmp_path):
    import subprocess, sys
    out = tmp_path / "test_fixture_safety_audit.json"
    proc = subprocess.run([sys.executable, "tools/audit_test_fixture_safety.py", "--out", str(out)], cwd=ROOT, text=True, capture_output=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads(out.read_text())
    assert report["status"] == "passed"
