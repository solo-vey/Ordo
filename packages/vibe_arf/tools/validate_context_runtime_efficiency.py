#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import importlib.util

def load_audit(root):
    p=root/'tools/audit_context_runtime_efficiency.py'; spec=importlib.util.spec_from_file_location('ctxaudit',p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m.audit(root)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); a=ap.parse_args(); root=Path(a.root).resolve(); errors=[]
    policy=root/'source/context-runtime-efficiency-policy.json'
    if not policy.is_file(): errors.append('CONTEXT_POLICY_MISSING')
    start='\n'.join((root/x).read_text(encoding='utf-8',errors='ignore') for x in ['START_HERE_MODEL_MODE.md','START_PROMPT_MODEL_MODE.md'] if (root/x).is_file()).lower()
    for phrase,code in [('do not recursively read','MODEL_START_NO_RECURSIVE_READ'),('do not preload','MODEL_START_NO_PRELOAD'),('active node','MODEL_START_ACTIVE_NODE_TARGETING'),('authoring/','MODEL_START_AUTHORING_ISOLATION'),('design/','MODEL_START_DESIGN_ISOLATION')]:
        if phrase not in start: errors.append(code)
    try: audit=load_audit(root); report=audit['report']
    except Exception as e: errors.append('CONTEXT_AUDIT_FAILED:'+str(e)); report={}
    result={'schema_version':'1.0','validator':'CONTEXT_RUNTIME_EFFICIENCY','status':'PASS' if not errors else 'FAIL','errors':errors,'diagnostic':report,'score_effect':0}
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
