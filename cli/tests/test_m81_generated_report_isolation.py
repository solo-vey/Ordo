from pathlib import Path
import json
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_workspace_report_manifest_is_complete_and_hashed():
    manifest_path = ROOT / 'reports' / 'CANONICAL_REPORTS_MANIFEST.yaml'
    manifest = yaml.safe_load(manifest_path.read_text(encoding='utf-8'))
    declared = {e['path'] for e in manifest['entries']}
    actual = {
        p.relative_to(ROOT / 'reports').as_posix()
        for p in (ROOT / 'reports').rglob('*')
        if p.is_file() and p != manifest_path
    }
    assert actual == declared


def test_generated_report_relocation_manifest_matches_output_root():
    manifest = json.loads((ROOT / 'manifests' / 'GENERATED_REPORT_RELOCATION_MANIFEST.json').read_text())
    actual = {
        p.relative_to(ROOT / '.ordo-generated' / 'workspace-reports').as_posix()
        for p in (ROOT / '.ordo-generated' / 'workspace-reports').rglob('*')
        if p.is_file()
    }
    declared = {Path(e['generated_path']).relative_to('.ordo-generated/workspace-reports').as_posix() for e in manifest['entries']}
    assert actual == declared


def test_generated_artifact_isolation_gate_passes():
    proc = subprocess.run(
        [sys.executable, str(ROOT / 'tools' / 'check_generated_artifact_isolation.py')],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    assert report['status'] == 'passed'
