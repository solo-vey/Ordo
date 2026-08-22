#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, sys, fnmatch
R=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]).resolve()
p=R/'PRODUCTION_DEPENDENCY_CLOSURE.json'
errs=[]
if not p.is_file(): errs.append('manifest_missing'); data={}
else:
    try:data=json.loads(p.read_text())
    except Exception as e:data={}; errs.append('manifest_invalid:'+str(e))
contract=json.loads((R/'PRODUCTION_PACKAGE_CONTRACT.json').read_text())
forbidden_patterns=[pat for cls in contract.get('artifact_classes',[]) if cls.get('default_inclusion')=='forbidden' for pat in cls.get('patterns',[])]
def is_forbidden(rel):
    return any(fnmatch.fnmatch(rel,pat) or (pat.endswith('/**') and (rel==pat[:-3] or rel.startswith(pat[:-2]))) for pat in forbidden_patterns)
paths=set()
for row in data.get('files',[]):
    rel=row.get('path'); paths.add(rel)
    f=R/rel if rel else None
    if not rel or not f.is_file(): errs.append('missing:'+str(rel)); continue
    if hashlib.sha256(f.read_bytes()).hexdigest()!=row.get('sha256'): errs.append('hash_mismatch:'+rel)
    if is_forbidden(rel): errs.append('forbidden_dependency_leak:'+rel)
    n=Path(rel).name
    if rel.startswith('tools/') and (n.startswith('mutate_') or n.startswith('repair_') or n.startswith('fix_') or n.startswith('refresh_') or n.startswith('finalize_')): errs.append('development_tool_leak:'+rel)
vp=json.loads((R/'verification_profile.json').read_text())
for c in vp.get('checks',[]):
    s=(c.get('args') or {}).get('script')
    if s and s not in paths: errs.append('profile_script_uncovered:'+s)
rm=json.loads((R/'verification/EXECUTION_RESPONSIBILITY_MAP.json').read_text())
for e in rm.get('entries',[]):
    for ref in e.get('tool_or_validator_refs') or []:
        if isinstance(ref,str) and ref.startswith('tools/') and (R/ref).is_file() and ref not in paths: errs.append('responsibility_tool_uncovered:'+ref)
print(json.dumps({'status':'PASS' if not errs else 'FAIL','files':len(paths),'errors':errs[:50]},indent=2))
raise SystemExit(0 if not errs else 1)
