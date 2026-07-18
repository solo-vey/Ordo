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
    entries = manifest['entries']
    assert manifest['entry_count'] == len(entries)

    generated_paths = [e['generated_path'] for e in entries]
    assert len(generated_paths) == len(set(generated_paths))
    assert all(path.startswith('.ordo-generated/workspace-reports/') for path in generated_paths)
    assert all(len(e['sha256']) == 64 and all(c in '0123456789abcdef' for c in e['sha256']) for e in entries)

    # Generated payloads are not required to be committed to the source tree.
    # When a generated root is present, every physical file must still be
    # declared; absence is valid under source_tree_policy=forbid_generated_payloads.
    output_root = ROOT / '.ordo-generated' / 'workspace-reports'
    actual = {
        p.relative_to(output_root).as_posix()
        for p in output_root.rglob('*')
        if p.is_file()
    } if output_root.exists() else set()
    declared = {
        Path(path).relative_to('.ordo-generated/workspace-reports').as_posix()
        for path in generated_paths
    }
    assert actual <= declared


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
