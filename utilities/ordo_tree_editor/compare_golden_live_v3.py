#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path


def canon_hash(value):
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),default=str).encode()
    return hashlib.sha256(raw).hexdigest()


def compare(golden, live):
    checks=[]
    def add(i,ok,g,l): checks.append({'id':i,'status':'PASS' if ok else 'FAIL','golden':g,'live':l})
    gr=golden.get('run') or golden.get('source_run') or {}
    lr=live.get('run') or {}
    # Golden corpus v1 stores acceptance_source + model calls but not full run path;
    # when full run metadata exists, compare it. Otherwise report NOT_APPLICABLE rather than fabricate proof.
    gterm=(gr.get('outcome') or {}).get('nodeId') or (golden.get('acceptance_source') or {}).get('terminal')
    lterm=(lr.get('outcome') or {}).get('nodeId')
    add('TERMINAL',gterm==lterm,gterm,lterm)
    gpath=gr.get('path')
    if isinstance(gpath,list): add('CONTROL_FLOW_PATH',gpath==lr.get('path'),gpath,lr.get('path'))
    else: checks.append({'id':'CONTROL_FLOW_PATH','status':'NOT_APPLICABLE','detail':'golden corpus has no full run path'})
    gstate=gr.get('final_state') or golden.get('final_state')
    if isinstance(gstate,dict): add('FINAL_STATE_HASH',canon_hash(gstate)==canon_hash(lr.get('final_state') or {}),canon_hash(gstate),canon_hash(lr.get('final_state') or {}))
    else: checks.append({'id':'FINAL_STATE_HASH','status':'NOT_APPLICABLE','detail':'golden corpus has no final state'})
    gcalls=[c.get('element_id') or c.get('current_id') for c in (golden.get('calls') or []) if c.get('element_id') or c.get('current_id')]
    lcalls=[c.get('current_id') for c in (live.get('calls') or []) if c.get('step_class')=='live_model_call' and c.get('current_id')]
    if gcalls: add('MODEL_ELEMENT_SEQUENCE',gcalls==lcalls,gcalls,lcalls)
    else: checks.append({'id':'MODEL_ELEMENT_SEQUENCE','status':'NOT_APPLICABLE','detail':'golden corpus has no model element IDs'})
    # Never compare raw natural-language model text as a semantic invariant.
    failures=[c for c in checks if c['status']=='FAIL']
    return {'status':'PASS' if not failures else 'FAIL','checks':checks,'semantic_policy':'compare structural/state invariants; do not require byte-identical model prose'}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('golden'); ap.add_argument('live'); args=ap.parse_args()
    g=json.loads(Path(args.golden).read_text(encoding='utf-8')); l=json.loads(Path(args.live).read_text(encoding='utf-8'))
    out=compare(g,l); print(json.dumps(out,ensure_ascii=False,indent=2)); raise SystemExit(0 if out['status']=='PASS' else 1)
if __name__=='__main__': main()
