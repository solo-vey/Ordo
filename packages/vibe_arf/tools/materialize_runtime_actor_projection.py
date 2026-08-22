#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, re
from pathlib import Path
import yaml

def sha_file(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def state_paths(text:str)->list[str]:
    return sorted(set(re.findall(r'\bstate\.([A-Za-z0-9_.]+)', text or '')))
def routes_of(e:dict):
    out=[]
    if isinstance(e.get('next'),str): out.append(e['next'])
    oa=e.get('on_answer')
    if isinstance(oa,dict):
        if isinstance(oa.get('next'),str): out.append(oa['next'])
        for v in oa.values():
            if isinstance(v,dict) and isinstance(v.get('next'),str): out.append(v['next'])
    for k in ('on_pass','on_fail'):
        if isinstance(e.get(k),str): out.append(e[k])
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); a=ap.parse_args(); root=Path(a.root).resolve()
    src=root/'source/program.ordo.yaml'; doc=yaml.safe_load(src.read_text(encoding='utf-8')) or {}; proj=copy.deepcopy(doc)
    all_e={e.get('id'):e for sec in ('nodes','gates') for e in (proj.get(sec) or []) if isinstance(e,dict) and e.get('id')}
    transformed=[]
    # Actor lowering: every canonical MODEL_INTERNAL becomes compiler-native model execution.
    for node in proj.get('nodes') or []:
        if not isinstance(node,dict): continue
        ctx=node.get('node_context') if isinstance(node.get('node_context'),dict) else {}
        if str(ctx.get('interaction_class') or '')!='MODEL_INTERNAL': continue
        if 'question' in node and 'model_instruction' not in node: node['model_instruction']=node.pop('question')
        else: node.pop('question',None)
        node.pop('answer_type',None)
        node['type']='automatic'; node['action']='AI.MODEL_STEP'; transformed.append(str(node.get('id')))
    # Required-write lowering: canonical runtime binding makes producer obligations explicit.
    # The binding itself is canonical policy; this projection only materializes it.
    binding_path=root/'source/runtime-required-state-write-contract.json'
    binding=json.loads(binding_path.read_text(encoding='utf-8'))
    required_by_node={}
    provenance=[]
    # Start with explicit supplemental/non-gate obligations.
    merged_required={}
    for entry in binding.get('producer_contracts') or []:
        pid=str(entry.get('producer_id') or '')
        merged_required.setdefault(pid,set()).update(str(x) for x in (entry.get('required_state_writes') or []) if x)

    # Mechanically derive every mechanical-gate state input from its canonical writer.
    writers={}
    for pred in all_e.values():
        oa=pred.get('on_answer') if isinstance(pred.get('on_answer'),dict) else {}
        upd=oa.get('update_state') if isinstance(oa.get('update_state'),dict) else {}
        for path in upd.keys(): writers.setdefault(path,[]).append(pred['id'])
    deriv=binding.get('mechanical_gate_derivation') or {}
    overrides=deriv.get('writer_overrides') or {}
    if deriv.get('enabled'):
        for gate in proj.get('gates') or []:
            if not isinstance(gate,dict) or str(gate.get('method') or '').lower()!='mechanical': continue
            for path in state_paths(str(gate.get('condition') or '')+' '+str(gate.get('assert') or '')):
                candidates=writers.get(path,[])
                key=f"{gate.get('id')}:{path}"
                pid=overrides.get(key)
                if pid:
                    if pid not in candidates: raise SystemExit(f'invalid required-write override {key} -> {pid}; candidates={candidates}')
                elif len(candidates)==1: pid=candidates[0]
                else: raise SystemExit(f'ambiguous/missing writer for mechanical gate input {key}: {candidates}')
                merged_required.setdefault(pid,set()).add(path)
                provenance.append({'producer_id':pid,'gate_id':gate.get('id'),'state_path':path,'basis':'mechanical_gate_unique_writer' if len(candidates)==1 else 'mechanical_gate_writer_override'})

    for pid,reqset in sorted(merged_required.items()):
        pred=all_e.get(pid)
        if not isinstance(pred,dict): raise SystemExit(f'unknown required-write producer: {pid}')
        oa=pred.get('on_answer') if isinstance(pred.get('on_answer'),dict) else {}
        upd=oa.get('update_state') if isinstance(oa.get('update_state'),dict) else {}
        declared=set(pred.get('writes') or []) | set(upd.keys())
        reqpaths=sorted(reqset)
        missing=[x for x in reqpaths if x not in declared]
        if missing: raise SystemExit(f'required-write binding not declared writable by {pid}: {missing}')
        ctx=pred.setdefault('node_context',{}) if isinstance(pred.get('node_context'),dict) else {}
        pred['node_context']=ctx
        ctx['required_state_writes']=reqpaths
        ctx['required_state_writes_provenance']='derived from canonical runtime binding + mechanical gate writer analysis; runtime projection only'
        required_by_node[pid]=set(reqpaths)
        explicit=set(next((e.get('required_state_writes') or [] for e in binding.get('producer_contracts') or [] if e.get('producer_id')==pid),[]))
        for path in sorted(set(reqpaths)-explicit):
            # provenance for gate-derived paths is already recorded above
            pass
        for path in sorted(explicit):
            if not any(x.get('producer_id')==pid and x.get('state_path')==path for x in provenance):
                provenance.append({'producer_id':pid,'state_path':path,'basis':'canonical_runtime_required_write_binding'})
    outdir=root/'runtime_projection'; outdir.mkdir(exist_ok=True); out=outdir/'program.ordo.yaml'
    out.write_text(yaml.safe_dump(proj,sort_keys=False,allow_unicode=True),encoding='utf-8')
    manifest={'schema_version':'2.0','status':'PASS','projection_id':'VIBE_RUNTIME_ACTOR_PROJECTION_V2',
      'canonical_source':'source/program.ordo.yaml','canonical_source_sha256':sha_file(src),
      'derived_projection':'runtime_projection/program.ordo.yaml','derived_projection_sha256':sha_file(out),
      'actor_rule':'Every MODEL_INTERNAL canonical node lowers to compiler-native semantic_model shape; allowed_tools never changes actor authority.',
      'required_write_rule':'Supplemental canonical obligations plus all mechanical-gate state inputs are materialized from unique canonical writers; ambiguous writers require explicit overrides.',
      'transformed_model_internal_count':len(transformed),'transformed_model_internal_ids':sorted(transformed),
      'required_write_producer_count':len(required_by_node),'required_write_count':sum(len(x) for x in required_by_node.values()),
      'forbidden_mutation':'canonical source rewrite'}
    (outdir/'ACTOR_PROJECTION_PROVENANCE.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    rp={'schema_version':'1.0','status':'PASS','canonical_source_sha256':sha_file(src),'projection_sha256':sha_file(out),'derivations':provenance}
    (outdir/'REQUIRED_STATE_WRITES_PROVENANCE.json').write_text(json.dumps(rp,ensure_ascii=False,indent=2)+'\n')
    (outdir/'MODEL_INTERNAL_EXECUTION_PROVENANCE.json').write_text(json.dumps({'schema_version':'1.0','status':'PASS','ids':sorted(transformed),'count':len(transformed),'projection_sha256':sha_file(out)},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'PASS','model_internal':len(transformed),'required_write_producers':len(required_by_node),'required_write_count':sum(len(x) for x in required_by_node.values()),'projection_sha256':sha_file(out)},indent=2))
if __name__=='__main__': main()
