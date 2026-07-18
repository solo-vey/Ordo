from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import zipfile

from .loader import load_package
from .reporter import write_json


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _file_entry(path: Path, root: Path) -> dict[str, Any]:
    return {
        'path': _rel(path, root),
        'sha256': _sha256_file(path),
        'bytes': path.stat().st_size,
    }


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def _collect_files(root: Path, patterns: list[str]) -> list[dict[str, Any]]:
    seen: set[Path] = set()
    out: list[dict[str, Any]] = []
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            if path.is_file() and path not in seen:
                seen.add(path)
                out.append(_file_entry(path, root))
    return out


def _zip_package(root: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(root.rglob('*')):
            if path.is_file():
                if '__pycache__' in path.parts or path.suffix == '.pyc':
                    continue
                if path.resolve() == out.resolve():
                    continue
                zf.write(path, path.relative_to(root.parent))


def build_release_provenance(package_path: str | Path, *, release_archive: str | Path | None = None) -> dict[str, Any]:
    """Build a release provenance manifest for an Ordo package.

    M14 provenance is not an execution mechanism. It records what was built,
    which reports exist, which artifacts were derived, and the hashes of source,
    IR, generated outputs, lockfile, and release archive.
    """
    root, manifest, source, tests = load_package(package_path)
    reports_dir = root / manifest.get('reports', 'reports')
    release_dir = root / 'release'
    release_dir.mkdir(exist_ok=True)

    generated_at = datetime.now(timezone.utc).isoformat()
    package_name = manifest.get('name', root.name)
    package_version = manifest.get('version', '0.0.0')
    source_meta = source.get('ordo') or {}
    release_archive_path = Path(release_archive).resolve() if release_archive else release_dir / f'{package_name}-{package_version}.zip'
    if not release_archive_path.exists():
        _zip_package(root, release_archive_path)

    report_files = _collect_files(root, ['reports/*.json'])
    source_files = _collect_files(root, ['ordo.yml', 'README.md', 'source/**/*.yaml', 'source/**/*.yml', 'domain/**/*.md', 'domain/**/*.yaml', 'profiles/**/*.yaml', 'output_templates/**/*.yaml', 'output_templates/**/*.md'])
    compiled_files = _collect_files(root, ['compiled/*.json'])
    runtime_files = _collect_files(root, ['runtime/**/*.json'])
    output_files = _collect_files(root, ['generated_outputs/*.md', 'generated_outputs/*.json'])
    lock_files = _collect_files(root, ['ordo.lock.json'])

    release_validation_report = _read_json(reports_dir / 'release_validation_report.json') or {}
    output_manifest = _read_json(root / 'generated_outputs' / 'output_manifest.json') or {}
    lock = _read_json(root / 'ordo.lock.json') or {}

    command_history = []
    for step in release_validation_report.get('steps', []):
        name = step.get('name')
        if name:
            command_history.append({
                'command': f'ordo {name} {root.name}',
                'step': name,
                'status': step.get('status'),
                'report': step.get('report'),
            })

    provenance = {
        'schema': 'ordo.release_provenance.v0.1',
        'generated_at': generated_at,
        'toolchain': {
            'ordo_cli_version': '0.10.0',
            'ordo_language_version': manifest.get('ordo_version') or source_meta.get('version'),
        },
        'package': {
            'name': package_name,
            'version': package_version,
            'root': str(root),
            'control_level': source_meta.get('control_level'),
            'execution_mode': source_meta.get('execution_mode'),
        },
        'release': {
            'status': release_validation_report.get('status', 'unknown'),
            'archive': _file_entry(release_archive_path, root),
            'handoff_status': 'ready_for_handoff' if release_validation_report.get('status') == 'passed' else 'blocked',
        },
        'command_history': command_history,
        'inputs': {
            'source_files': source_files,
            'lock_files': lock_files,
            'lock_summary': lock.get('summary', {}),
        },
        'derived_artifacts': {
            'compiled_ir': compiled_files,
            'runtime_trace_and_state': runtime_files,
            'generated_outputs': output_files,
            'output_manifest_summary': output_manifest.get('summary') or output_manifest.get('outputs_summary') or {},
        },
        'reports': report_files,
        'evidence': {
            'release_validation_report': _file_entry(reports_dir / 'release_validation_report.json', root) if (reports_dir / 'release_validation_report.json').exists() else None,
            'output_manifest': _file_entry(root / 'generated_outputs' / 'output_manifest.json', root) if (root / 'generated_outputs' / 'output_manifest.json').exists() else None,
            'dependency_lock': _file_entry(root / 'ordo.lock.json', root) if (root / 'ordo.lock.json').exists() else None,
        },
        'summary': {
            'source_files': len(source_files),
            'report_files': len(report_files),
            'compiled_files': len(compiled_files),
            'runtime_files': len(runtime_files),
            'generated_output_files': len(output_files),
        },
    }
    out_path = reports_dir / 'release_provenance.json'
    write_json(out_path, provenance)
    return provenance


def validate_release_provenance(package_path: str | Path) -> dict[str, Any]:
    root, manifest, source, tests = load_package(package_path)
    path = root / manifest.get('reports', 'reports') / 'release_provenance.json'
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not path.exists():
        errors.append({'code': 'PROVENANCE_MISSING', 'message': 'reports/release_provenance.json is missing.'})
        report = {'status': 'failed', 'errors': errors, 'warnings': warnings}
        write_json(root / manifest.get('reports', 'reports') / 'release_provenance_validation_report.json', report)
        return report
    data = json.loads(path.read_text(encoding='utf-8'))
    required_top = ['schema', 'generated_at', 'toolchain', 'package', 'release', 'inputs', 'derived_artifacts', 'reports', 'evidence', 'summary']
    for key in required_top:
        if key not in data:
            errors.append({'code': 'PROVENANCE_FIELD_MISSING', 'message': f'Missing top-level field: {key}'})
    archive = ((data.get('release') or {}).get('archive') or {})
    archive_path = archive.get('path')
    archive_hash = archive.get('sha256')
    if not archive_path or not archive_hash:
        errors.append({'code': 'RELEASE_ARCHIVE_EVIDENCE_MISSING', 'message': 'Release archive path/hash must be present.'})
    else:
        abs_archive = root / archive_path if not Path(archive_path).is_absolute() else Path(archive_path)
        if not abs_archive.exists():
            # archive is often stored as release/... relative to root
            candidate = root / archive_path
            if not candidate.exists():
                errors.append({'code': 'RELEASE_ARCHIVE_MISSING', 'message': f'Release archive not found: {archive_path}'})
            else:
                abs_archive = candidate
        if abs_archive.exists() and _sha256_file(abs_archive) != archive_hash:
            errors.append({'code': 'RELEASE_ARCHIVE_HASH_MISMATCH', 'message': 'Release archive hash differs from provenance.'})
    # Verify listed evidence hashes where files exist inside root.
    for section in ['source_files', 'lock_files']:
        for item in ((data.get('inputs') or {}).get(section) or []):
            p = root / item.get('path', '')
            if p.exists() and item.get('sha256') and _sha256_file(p) != item.get('sha256'):
                errors.append({'code': 'INPUT_HASH_MISMATCH', 'message': f'Hash mismatch: {item.get("path")}'})
    for section in ['compiled_ir', 'runtime_trace_and_state', 'generated_outputs']:
        for item in ((data.get('derived_artifacts') or {}).get(section) or []):
            p = root / item.get('path', '')
            if p.exists() and item.get('sha256') and _sha256_file(p) != item.get('sha256'):
                errors.append({'code': 'DERIVED_HASH_MISMATCH', 'message': f'Hash mismatch: {item.get("path")}'})
    status = 'passed' if not errors else 'failed'
    report = {
        'status': status,
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'provenance': str(path),
        'summary': {'errors': len(errors), 'warnings': len(warnings)},
        'errors': errors,
        'warnings': warnings,
    }
    write_json(root / manifest.get('reports', 'reports') / 'release_provenance_validation_report.json', report)
    return report
