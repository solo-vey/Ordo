from __future__ import annotations
from pathlib import Path
from typing import Any
import hashlib, json, yaml

SCHEMA='ordo.startup_artifact_reconciliation.v1'

def sha256(path: Path)->str:
    h=hashlib.sha256();
    with path.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()

def _safe_path(root: Path, raw: str) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    candidate = (root / raw).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def reconcile(package: str | Path) -> dict[str, Any]:
    root = Path(package).resolve(); findings=[]; checks=[]
    def add(cid,status,msg,target=None,severity='error'):
        item={'check_id':cid,'status':status,'message':msg}
        if target is not None:item['target']=target
        checks.append(item)
        if status=='failed': findings.append({'check_id':cid,'severity':severity,'message':msg,'target':target})
    manifest_path=root/'ordo.yml'
    if not manifest_path.exists():
        add('package_manifest_exists','failed','missing ordo.yml','ordo.yml')
        return {'schema_version':SCHEMA,'package':str(root),'status':'blocked','checks':checks,'findings':findings,'summary':{'checks':len(checks),'errors':1,'warnings':0}}
    manifest=yaml.safe_load(manifest_path.read_text()) or {}
    source_raw=manifest.get('source')
    source_path=_safe_path(root,source_raw) if source_raw else None
    if source_path is None or not source_path.exists():
        add('package_source_safe','failed',f'invalid or missing package source: {source_raw}',source_raw)
        return {'schema_version':SCHEMA,'package':str(root),'status':'blocked','checks':checks,'findings':findings,'summary':{'checks':len(checks),'errors':1,'warnings':0}}
    source=yaml.safe_load(source_path.read_text()) or {}
    startup=source.get('startup_package_profile'); sync=source.get('artifact_sync')
    add('startup_profile_present','passed' if isinstance(startup,dict) else 'failed','startup_package_profile present' if isinstance(startup,dict) else 'missing startup_package_profile')
    add('artifact_sync_present','passed' if isinstance(sync,dict) else 'failed','artifact_sync present' if isinstance(sync,dict) else 'missing artifact_sync')
    if isinstance(startup,dict):
        modes=startup.get('startup_modes') or []
        names={m.get('mode') for m in modes if isinstance(m,dict)}
        default=startup.get('default_startup_mode')
        add('startup_default_mode_resolves','passed' if default in names else 'failed',f'default mode resolves: {default}' if default in names else f'default mode missing: {default}')
        declared_entries={e.get('path') for e in startup.get('entry_files') or [] if isinstance(e,dict) and e.get('path')}
        for m in modes:
            if not isinstance(m,dict) or not m.get('entry_file'): continue
            entry=m['entry_file']
            add('startup_mode_entry_declared','passed' if entry in declared_entries else 'failed',f"startup mode entry {'declared' if entry in declared_entries else 'not declared'}: {entry}",entry)
        for e in startup.get('entry_files') or []:
            if not isinstance(e,dict) or not e.get('path'): continue
            raw=e['path']; p=_safe_path(root,raw); req=str(e.get('required',True)).lower() in {'true','required','1','yes'}
            if p is None:
                add('startup_entry_path_safe','failed',f'unsafe startup entry path: {raw}',raw); continue
            add('startup_entry_path_safe','passed',f'startup entry path safe: {raw}',raw)
            add('startup_entry_exists','passed' if p.exists() else ('failed' if req else 'warning'),f"startup entry {'exists' if p.exists() else 'missing'}: {raw}",raw,'error' if req else 'warning')
        boundary=startup.get('authority_boundary') or {}
        unsafe=[k for k,v in boundary.items() if k.startswith('startup_files_may_') and v is not False]
        add('startup_authority_boundary_safe','passed' if not unsafe else 'failed','startup authority boundary is fail-closed' if not unsafe else f'unsafe startup authority flags: {unsafe}')
    if isinstance(sync,dict):
        strict=sync.get('profile')=='strict'
        source_paths=set(); artifact_ids=set(); artifact_paths=set()
        for item in sync.get('source_of_truth') or []:
            if not isinstance(item,dict) or not item.get('path'): continue
            raw=item['path']; p=_safe_path(root,raw)
            if p is None:
                add('sync_path_safe','failed',f'unsafe source path: {raw}',raw); continue
            add('sync_path_safe','passed',f'source path safe: {raw}',raw)
            source_paths.add(raw)
            add('sync_source_exists','passed' if p.exists() else 'failed',f"source {'exists' if p.exists() else 'missing'}: {raw}",raw)
        for a in sync.get('derived_artifacts') or []:
            if not isinstance(a,dict) or not a.get('path'): continue
            raw=a['path']; aid=a.get('artifact_id'); p=_safe_path(root,raw)
            duplicate=(aid in artifact_ids if aid else False) or raw in artifact_paths
            add('derived_artifact_unique','failed' if duplicate else 'passed',f"derived artifact {'duplicate' if duplicate else 'unique'}: {raw}",raw)
            if aid: artifact_ids.add(aid)
            artifact_paths.add(raw)
            add('derived_not_source_of_truth','failed' if raw in source_paths else 'passed',f"derived artifact {'overlaps source of truth' if raw in source_paths else 'separate from source of truth'}: {raw}",raw)
            if p is None:
                add('sync_path_safe','failed',f'unsafe derived artifact path: {raw}',raw); continue
            add('sync_path_safe','passed',f'derived artifact path safe: {raw}',raw)
            exists=p.exists()
            add('derived_artifact_exists','passed' if exists else 'failed',f"derived artifact {'exists' if exists else 'missing'}: {raw}",raw)
            expected=a.get('sha256')
            if strict:
                add('derived_artifact_sha_required','passed' if expected else 'failed',f"strict artifact SHA-256 {'present' if expected else 'missing'}: {raw}",raw)
            if exists and expected:
                ok=sha256(p)==expected
                add('derived_artifact_checksum','passed' if ok else 'failed',f"checksum {'matches' if ok else 'mismatch'}: {raw}",raw)
        boundary=sync.get('authority_boundary') or {}
        safe=boundary.get('derived_artifacts_may_override_source_of_truth') is False
        add('derived_authority_boundary_safe','passed' if safe else 'failed','derived artifact authority boundary is fail-closed' if safe else 'derived artifacts may override source of truth')
    status='passed' if not [f for f in findings if f['severity']=='error'] else 'blocked'
    return {'schema_version':SCHEMA,'package':str(root),'status':status,'checks':checks,'findings':findings,'summary':{'checks':len(checks),'errors':sum(f['severity']=='error' for f in findings),'warnings':sum(f['severity']=='warning' for f in findings)}}
