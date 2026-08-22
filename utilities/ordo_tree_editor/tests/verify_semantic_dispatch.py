#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

MODEL_PHASES={'enter','respond'}
KNOWN_EXECUTORS={'semantic_model','human_interaction','human_gate','deterministic_gate','document_generate','artifact_presenter','state_patch_template','package_tool','terminal'}

def verify(plan: dict) -> dict:
    errors=[]; checked=0
    for eid,e in (plan.get('elements') or {}).items():
        tr=e.get('execution_traits') or {}; ex=tr.get('runtime_executor'); phases=set(tr.get('model_executed_phases') or [])
        checked += 1
        if ex not in KNOWN_EXECUTORS:
            errors.append(f'{eid}: unknown runtime_executor {ex!r}')
        if not phases <= MODEL_PHASES:
            errors.append(f'{eid}: invalid model phases {sorted(phases-MODEL_PHASES)}')
        if tr.get('model_executed') != bool(phases):
            errors.append(f'{eid}: model_executed disagrees with model_executed_phases')
        if ex=='semantic_model' and not phases:
            errors.append(f'{eid}: semantic_model executor has no model phase')
        if e.get('kind')=='unknown_node':
            errors.append(f'{eid}: unknown_node is not executable')
        if e.get('kind')=='interactive_node' and ex!='human_interaction':
            errors.append(f'{eid}: interactive node lacks human_interaction executor')
    return {'status':'PASS' if not errors else 'FAIL','elements':checked,'errors':errors}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('plan'); a=ap.parse_args()
    out=verify(json.loads(Path(a.plan).read_text()))
    print(json.dumps(out,ensure_ascii=False,indent=2)); sys.exit(0 if out['status']=='PASS' else 1)
if __name__=='__main__': main()
