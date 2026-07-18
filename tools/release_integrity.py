#!/usr/bin/env python3
"""Canonical release identity, freeze, and post-unpack verification."""
from __future__ import annotations
import hashlib, json, os, shutil, tempfile, zipfile
from datetime import datetime, timezone
from pathlib import Path

EXCLUDE_NAMES = {'.git','__pycache__','.pytest_cache','node_modules'}
GENERATED_REPORTS = {'DELIVERY_GATE_REPORT.json','FINAL_PACKAGE_SELF_CHECK_REPORT.json','FINAL_PACKAGE_SELF_CHECK_REPORT.md','SHA256SUMS.txt'}

def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def iter_source_files(root: Path):
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if any(part in EXCLUDE_NAMES for part in rel.parts) or p.suffix=='.pyc': continue
        if rel.as_posix() in GENERATED_REPORTS: continue
        yield p, rel

def source_tree_hash(root: Path) -> str:
    h=hashlib.sha256()
    for p,rel in iter_source_files(root):
        h.update(rel.as_posix().encode()+b'\0'+bytes.fromhex(sha256_file(p)))
    return h.hexdigest()

def load_identity(root: Path) -> dict:
    data=json.loads((root/'manifests/RELEASE_IDENTITY.json').read_text())
    required={'release_id','archive_filename','internal_root','language_version','framework_version'}
    missing=sorted(required-set(data))
    if missing: raise ValueError(f'missing release identity fields: {missing}')
    if not data['archive_filename'].endswith('.zip'): raise ValueError('archive_filename must end with .zip')
    if '/' in data['internal_root'] or '\\' in data['internal_root']: raise ValueError('internal_root must be one directory name')
    return data

def stage_candidate(root: Path, staging_parent: Path, reports: dict[str,str]) -> Path:
    identity=load_identity(root)
    staged=staging_parent/identity['internal_root']
    staged.mkdir(parents=True)
    for p,rel in iter_source_files(root):
        dest=staged/rel; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dest)
    for rel,text in reports.items():
        dest=staged/rel; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(text,encoding='utf-8')
    # Checksums are generated last; no file may change afterwards.
    lines=[]
    for p in sorted(staged.rglob('*')):
        if p.is_file() and p.name!='SHA256SUMS.txt':
            lines.append(f'{sha256_file(p)}  {p.relative_to(staged).as_posix()}')
    (staged/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    frozen=source_tree_hash_including_reports(staged)
    if frozen != source_tree_hash_including_reports(staged):
        raise RuntimeError('candidate changed after checksum freeze')
    return staged

def source_tree_hash_including_reports(root: Path) -> str:
    h=hashlib.sha256()
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.name!='SHA256SUMS.txt':
            h.update(p.relative_to(root).as_posix().encode()+b'\0'+bytes.fromhex(sha256_file(p)))
    return h.hexdigest()

def verify_extracted(root: Path, expected_identity: dict, expected_run_id: str|None=None) -> dict:
    failures=[]; verified=0
    checks=root/'SHA256SUMS.txt'
    if not checks.is_file(): failures.append('missing SHA256SUMS.txt')
    else:
        for line in checks.read_text().splitlines():
            expected,rel=line.split('  ',1); p=root/rel
            actual=sha256_file(p) if p.is_file() else None
            if actual==expected: verified+=1
            else: failures.append(f'checksum mismatch: {rel}')
    identity=load_identity(root)
    for k in ('release_id','internal_root','archive_filename','language_version','framework_version'):
        if identity.get(k)!=expected_identity.get(k): failures.append(f'identity mismatch: {k}')
    if root.name!=identity['internal_root']: failures.append('internal root does not match RELEASE_IDENTITY')
    gate=json.loads((root/'DELIVERY_GATE_REPORT.json').read_text())
    selfcheck=json.loads((root/'FINAL_PACKAGE_SELF_CHECK_REPORT.json').read_text())
    if gate.get('run_id')!=selfcheck.get('run_id'): failures.append('gate/self-check run_id mismatch')
    if gate.get('generated_at')!=selfcheck.get('generated_at'): failures.append('gate/self-check timestamp mismatch')
    if expected_run_id and gate.get('run_id')!=expected_run_id: failures.append('unexpected run_id')
    if gate.get('source_tree_hash')!=selfcheck.get('source_tree_hash'): failures.append('gate/self-check source hash mismatch')
    if gate.get('release_id')!=identity['release_id']: failures.append('gate release_id mismatch')
    state=json.loads((root/'manifests/VERSION_STATE.json').read_text())
    if state.get('release_id')!=identity['release_id']: failures.append('version state release_id mismatch')
    if state.get('language',{}).get('version')!=identity['language_version']: failures.append('language version mismatch')
    if state.get('framework',{}).get('version')!=identity['framework_version']: failures.append('framework version mismatch')
    return {'status':'passed' if not failures else 'failed','verified_files':verified,'failures':failures,'run_id':gate.get('run_id'),'source_tree_hash':gate.get('source_tree_hash')}

def build_verified_archive(root: Path,out: Path,reports:dict[str,str],run_id:str)->dict:
    identity=load_identity(root)
    if out.name!=identity['archive_filename']:
        raise ValueError(f"output filename must be {identity['archive_filename']}")
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); staged=stage_candidate(root,td,reports)
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(staged.rglob('*')):
                if p.is_file(): zf.write(p,p.relative_to(td))
        with zipfile.ZipFile(out) as zf:
            if zf.testzip() is not None: raise RuntimeError('zip integrity failed')
            extract=td/'verify'; zf.extractall(extract)
        verification=verify_extracted(extract/identity['internal_root'],identity,run_id)
        if verification['status']!='passed': raise RuntimeError(str(verification['failures']))
    return {'archive':out.name,'archive_sha256':sha256_file(out),**verification}
