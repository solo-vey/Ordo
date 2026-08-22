from __future__ import annotations
import json,re
from pathlib import Path
import yaml

def load_yaml(p):
    p=Path(p); return yaml.safe_load(p.read_text(encoding='utf-8')) if p.is_file() else None

def load_json(p):
    p=Path(p); return json.loads(p.read_text(encoding='utf-8')) if p.is_file() else None

def source_program(root):
    root=Path(root); p=root/'source/program.ordo.yaml'
    if p.is_file(): return load_yaml(p) or {}
    # self-hosted modular source
    nodes=[]; gates=[]; out={}
    for mp in sorted((root/'source/modules').glob('*.yaml')) if (root/'source/modules').is_dir() else []:
        d=load_yaml(mp) or {}
        for k,v in d.items():
            if k=='nodes': nodes.extend(v or [])
            elif k=='gates': gates.extend(v or [])
            elif k not in out: out[k]=v
    if nodes: out['nodes']=nodes
    if gates: out['gates']=gates
    return out

def emit(validator,errors,warnings=None,extra=None):
    d={'schema_version':'1.0','validator':validator,'status':'PASS' if not errors else 'FAIL','errors':errors,'warnings':warnings or []}
    if extra:d.update(extra)
    print(json.dumps(d,ensure_ascii=False,indent=2)); return 0 if not errors else 1

def route_targets(v):
    out=[]
    if isinstance(v,str): out.append(v)
    elif isinstance(v,dict):
        for k,x in v.items():
            if k in {'next','on_pass','on_fail','fail_to'} and isinstance(x,str): out.append(x)
            else: out.extend(route_targets(x))
    elif isinstance(v,list):
        for x in v: out.extend(route_targets(x))
    return out

def update_paths(node):
    vals=[]
    def rec(v):
        if isinstance(v,dict):
            u=v.get('update_state')
            if isinstance(u,dict): vals.extend(str(k) for k in u)
            for x in v.values(): rec(x)
        elif isinstance(v,list):
            for x in v: rec(x)
    rec(node.get('on_answer')); return vals
