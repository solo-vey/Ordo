import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'MANIFEST.sha256'


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _manifest_entries():
    entries = {}
    for line in MANIFEST.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        digest, rel = line.split('  ', 1)
        entries[rel] = digest
    return entries


def _shipped_files():
    return {
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob('*')
        if p.is_file()
        and p != MANIFEST
        and '__pycache__' not in p.parts
        and '.pytest_cache' not in p.parts
        and not p.name.endswith(('.pyc', '.pyo'))
    }


def test_manifest_matches_exact_shipped_tree():
    entries = _manifest_entries()
    shipped = _shipped_files()
    assert set(entries) == shipped, {
        'missing_from_manifest': sorted(shipped - set(entries)),
        'stale_manifest_entries': sorted(set(entries) - shipped),
    }
    mismatches = [rel for rel, expected in entries.items() if _sha256(ROOT / rel) != expected]
    assert mismatches == []
