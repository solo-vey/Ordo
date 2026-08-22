#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, sys
from pathlib import Path

def canon_sha(value):
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

def decode_token(t): return t.replace('~1','/').replace('~0','~')
def tokens(path):
    if not isinstance(path,str) or not path.startswith('/') or path=='/':
        raise ValueError('patch path must be an absolute non-root JSON pointer')
    return [decode_token(x) for x in path[1:].split('/')]

def apply_patch(state, patch):
    if patch.get('contract')!='state_patch_v1': raise ValueError('invalid contract')
    if patch.get('base_state_sha256')!=canon_sha(state): raise ValueError('STALE_BASE_STATE')
    allowed=patch.get('allowed_roots')
    if not isinstance(allowed,list) or not allowed or not all(isinstance(x,str) and x for x in allowed): raise ValueError('allowed_roots required')
    set_map=patch.get('set')
    if not isinstance(set_map,dict): raise ValueError('set must be object')
    deletes=patch.get('delete',[])
    if deletes and patch.get('allow_delete') is not True: raise ValueError('delete forbidden without allow_delete=true')
    out=copy.deepcopy(state); touched=set()
    for path,val in set_map.items():
        ts=tokens(path); root=ts[0]
        if root not in allowed: raise ValueError('PATH_OUTSIDE_ALLOWED_ROOTS:'+root)
        cur=out
        for key in ts[:-1]:
            if not isinstance(cur,dict): raise ValueError('non-object parent at '+path)
            if key not in cur: cur[key]={}
            cur=cur[key]
        if not isinstance(cur,dict): raise ValueError('non-object parent at '+path)
        cur[ts[-1]]=copy.deepcopy(val); touched.add(root)
    for path in deletes:
        ts=tokens(path); root=ts[0]
        if root not in allowed: raise ValueError('PATH_OUTSIDE_ALLOWED_ROOTS:'+root)
        cur=out
        for key in ts[:-1]:
            if not isinstance(cur,dict) or key not in cur: raise ValueError('delete path missing:'+path)
            cur=cur[key]
        if not isinstance(cur,dict) or ts[-1] not in cur: raise ValueError('delete path missing:'+path)
        del cur[ts[-1]]; touched.add(root)
    updates={k:copy.deepcopy(out.get(k)) for k in sorted(touched)}
    return out, {'contract':'state_updates_v1','status':'PASS','report':{'base_state_sha256':patch['base_state_sha256'],'result_state_sha256':canon_sha(out),'touched_roots':sorted(touched),'dependency_fingerprint':patch.get('dependency_fingerprint')},'state_updates':updates}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--state',required=True); ap.add_argument('--patch',required=True); ap.add_argument('--output')
    a=ap.parse_args()
    try:
        s=json.loads(Path(a.state).read_text(encoding='utf-8')); p=json.loads(Path(a.patch).read_text(encoding='utf-8'))
        _,env=apply_patch(s,p)
        txt=json.dumps(env,ensure_ascii=False,indent=2)
        if a.output: Path(a.output).write_text(txt+'\n',encoding='utf-8')
        else: print(txt)
        return 0
    except Exception as e:
        print(json.dumps({'contract':'state_updates_v1','status':'FAIL','report':{'error':str(e)},'state_updates':{}},ensure_ascii=False,indent=2))
        return 2
if __name__=='__main__': raise SystemExit(main())
