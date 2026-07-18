#!/usr/bin/env python3
import argparse, hashlib, json, sys
from pathlib import Path
import yaml

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(x): return json.dumps(x, sort_keys=True, separators=(",",":"), ensure_ascii=False)
def h(x): return hashlib.sha256(canon(x).encode()).hexdigest()
def index_ids(obj, path='$', out=None, dup=None):
    out={} if out is None else out; dup=[] if dup is None else dup
    if isinstance(obj,dict):
        if isinstance(obj.get('id'),str):
            i=obj['id']
            if i in out: dup.append(i)
            out[i]={'path':path,'value':obj,'hash':h(obj)}
        for k,v in obj.items(): index_ids(v,f'{path}.{k}',out,dup)
    elif isinstance(obj,list):
        for n,v in enumerate(obj): index_ids(v,f'{path}[{n}]',out,dup)
    return out,dup
def diff(a,b,path='$',out=None):
    out=[] if out is None else out
    if type(a)!=type(b): out.append({'path':path,'before':a,'after':b}); return out
    if isinstance(a,dict):
        for k in sorted(set(a)|set(b)):
            if k not in a: out.append({'path':f'{path}.{k}','before':'<MISSING>','after':b[k]})
            elif k not in b: out.append({'path':f'{path}.{k}','before':a[k],'after':'<MISSING>'})
            else: diff(a[k],b[k],f'{path}.{k}',out)
    elif isinstance(a,list):
        if canon(a)!=canon(b): out.append({'path':path,'before':a,'after':b})
    elif a!=b: out.append({'path':path,'before':a,'after':b})
    return out

def main():
 p=argparse.ArgumentParser(); p.add_argument('baseline'); p.add_argument('candidate'); p.add_argument('--allow-id',action='append',default=[]); p.add_argument('--report',required=True); a=p.parse_args()
 errors=[]
 if not a.allow_id: errors.append('empty_allowlist')
 try: before=yaml.safe_load(Path(a.baseline).read_text()); after=yaml.safe_load(Path(a.candidate).read_text())
 except Exception as e:
  Path(a.report).write_text(json.dumps({'status':'FAIL','errors':['yaml_parse_failure',str(e)]},indent=2)); return 2
 bi,bd=index_ids(before); ai,ad=index_ids(after)
 if bd or ad: errors.append('duplicate_node_id')
 added=sorted(set(ai)-set(bi)); removed=sorted(set(bi)-set(ai)); changed=sorted(i for i in set(ai)&set(bi) if ai[i]['hash']!=bi[i]['hash'])
 all_changed=sorted(set(added+removed+changed)); outside=sorted(set(all_changed)-set(a.allow_id))
 if outside: errors.append('changed_node_outside_allowlist')
 unchanged=sum(1 for i in set(ai)&set(bi) if ai[i]['hash']==bi[i]['hash']); denom=max(1,len(set(ai)|set(bi)))
 report={'status':'PASS' if not errors else 'FAIL','errors':errors,'baseline_sha256':sha(a.baseline),'candidate_sha256':sha(a.candidate),'allowlist':sorted(a.allow_id),'added_ids':added,'removed_ids':removed,'changed_ids':changed,'out_of_scope_ids':outside,'unchanged_node_count':unchanged,'total_node_count':denom,'unchanged_node_ratio':round(unchanged/denom,6),'structural_diff':{'added':added,'removed':removed,'changed':changed},'semantic_diff':diff(before,after)}
 Path(a.report).write_text(json.dumps(report,indent=2,ensure_ascii=False))
 return 0 if report['status']=='PASS' else 1
if __name__=='__main__': sys.exit(main())
