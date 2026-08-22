#!/usr/bin/env python3
"""Select zero or one domain implementation profile from a generated catalog.

The selector is generic, deterministic, side-effect free, and never guesses.
"""
from __future__ import annotations
import argparse, json, re, yaml
from pathlib import Path

def extract_field(text, field):
    pat = rf'(?im)\b{re.escape(field)}\b\s*[:=|]\s*[`"\']?([^`"\'\n|]+)'
    m = re.search(pat, text)
    if m: return m.group(1).strip()
    try: data=json.loads(text)
    except Exception:
        try: data=yaml.safe_load(text)
        except Exception: data=None
    stack=[data] if isinstance(data,(dict,list)) else []
    while stack:
        x=stack.pop()
        if isinstance(x,dict):
            for k,v in x.items():
                if k==field and isinstance(v,(str,int,float)): return str(v).strip()
                if isinstance(v,(dict,list)): stack.append(v)
        elif isinstance(x,list): stack.extend(y for y in x if isinstance(y,(dict,list)))
    return None

def main():
    p=argparse.ArgumentParser(); p.add_argument('--catalog',required=True); p.add_argument('--document'); p.add_argument('--value'); p.add_argument('--knowledge-dir')
    a=p.parse_args(); cpath=Path(a.catalog); cat=yaml.safe_load(cpath.read_text(encoding='utf-8')); field=cat['discriminator_field']
    value=a.value
    if value is None and a.document: value=extract_field(Path(a.document).read_text(encoding='utf-8'), field)
    match=None
    for item in cat.get('profiles',[]):
        vals=[str(item.get('key',''))]+[str(x) for x in item.get('aliases',[])]
        if value is not None and str(value).strip().lower() in [x.strip().lower() for x in vals]: match=item; break
    if not match:
        print(json.dumps({'status':'GENERIC_FALLBACK','field':field,'value':value,'profile_path':None,'profile_content':None,'reason':'profile unresolved or unsupported; do not guess'},ensure_ascii=False,indent=2)); return 0
    base=Path(a.knowledge_dir) if a.knowledge_dir else cpath.parent
    path=base/match['file']
    if not path.is_file():
        print(json.dumps({'status':'GENERIC_FALLBACK','field':field,'value':value,'profile_path':str(path),'profile_content':None,'reason':'selected profile missing; use generic repository-grounded implementation'},ensure_ascii=False,indent=2)); return 0
    print(json.dumps({'status':'SELECTED','field':field,'value':value,'profile_key':match['key'],'profile_path':str(path),'profile_content':path.read_text(encoding='utf-8')},ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
