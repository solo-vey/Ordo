#!/usr/bin/env python3
from pathlib import Path
import json,sys,re
HEX64=re.compile(r'^[0-9a-f]{64}$')

def goodhash(x): return isinstance(x,str) and bool(HEX64.fullmatch(x.lower()))
def emit(msgs,out,mode,cand,calls,art):
    pseudo=(mode=='PSEUDO_LIVE_OPTIMIZATION')
    rep={'schema_version':'2.0','status':'FAIL' if msgs else 'PASS','execution_mode':mode,
         'result_scoring_eligible':False if msgs else (not pseudo),
         'pseudo_score_eligible':False if msgs else pseudo,
         'formal_score_eligible':False if msgs else (mode=='LIVE_ACCEPTANCE'),
         'provenance_tier':'PSEUDO_LIVE_SYNTHETIC' if pseudo else 'LIVE_ACCEPTANCE',
         'candidate_sha256':cand,'verified_model_steps':len(calls),'artifact_sha256':art.get('artifact_sha256'),'errors':msgs}
    if out: Path(out).write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(rep,ensure_ascii=False)); return 1 if msgs else 0

def main(inp,out):
    p=Path(inp)
    if not p.is_file(): return emit([f'evidence missing: {p}'],out,'LIVE_ACCEPTANCE',None,[],{})
    d=json.loads(p.read_text(encoding='utf-8')); errs=[]
    mode=str(d.get('execution_mode') or 'LIVE_ACCEPTANCE').upper()
    if mode not in {'PSEUDO_LIVE_OPTIMIZATION','LIVE_ACCEPTANCE'}: errs.append(f'unsupported execution_mode {mode}')
    cand=d.get('candidate_sha256')
    if not goodhash(cand): errs.append('candidate_sha256 missing/invalid')
    calls=d.get('model_calls') or []
    executed=d.get('executed_model_nodes')
    if executed is None:
        # Backward-compatible evidence: the call list is the known executed-model-node set.
        executed=[c.get('element_id') for c in calls if c.get('element_id')]
    if not isinstance(executed,list): errs.append('executed_model_nodes must be a list')
    else:
        call_nodes=[c.get('element_id') for c in calls if c.get('element_id')]
        missing=[x for x in executed if x not in call_nodes]
        if missing: errs.append('executed model nodes missing response provenance: '+','.join(map(str,missing)))
    allowed_live={'live_model_call','replayed_live_call','LIVE_CALL','EXACT_LIVE_REPLAY'}
    allowed_pseudo={'PSEUDO_LIVE_SYNTHETIC'}
    for i,c in enumerate(calls,1):
        tag=f'model_calls[{i}]'; origin=c.get('origin')
        if mode=='LIVE_ACCEPTANCE' and origin not in allowed_live: errs.append(f'{tag}: forbidden origin {origin} for LIVE_ACCEPTANCE')
        if mode=='PSEUDO_LIVE_OPTIMIZATION' and origin not in allowed_pseudo: errs.append(f'{tag}: forbidden origin {origin} for PSEUDO_LIVE_OPTIMIZATION')
        for k in ['effective_input_sha256','output_sha256','candidate_sha256']:
            if not goodhash(c.get(k)): errs.append(f'{tag}: {k} missing/invalid')
        if cand and c.get('candidate_sha256')!=cand: errs.append(f'{tag}: candidate hash mismatch')
        if c.get('hidden_reference_visible_to_generator') is not False: errs.append(f'{tag}: hidden reference visibility must be false')
        if c.get('post_generation_mutation') is not False: errs.append(f'{tag}: post_generation_mutation must be false')
        if origin in {'live_model_call','LIVE_CALL'}:
            for k in ['provider','model','runtime_run_id']:
                if not c.get(k): errs.append(f'{tag}: live call requires {k}')
        if origin in {'replayed_live_call','EXACT_LIVE_REPLAY'}:
            for k in ['source_live_run_id','source_live_step_index','source_live_input_sha256','source_live_output_sha256']:
                if c.get(k) in (None,''): errs.append(f'{tag}: replay requires {k}')
            if not goodhash(c.get('source_live_input_sha256')) or not goodhash(c.get('source_live_output_sha256')): errs.append(f'{tag}: replay source hashes invalid')
            if c.get('exact_input_match') is not True: errs.append(f'{tag}: replay exact_input_match must be true')
            if goodhash(c.get('effective_input_sha256')) and goodhash(c.get('source_live_input_sha256')) and c.get('effective_input_sha256')!=c.get('source_live_input_sha256'): errs.append(f'{tag}: replay effective input hash differs from source live input')
            if goodhash(c.get('output_sha256')) and goodhash(c.get('source_live_output_sha256')) and c.get('output_sha256')!=c.get('source_live_output_sha256'): errs.append(f'{tag}: replay output hash differs from source live output')
        if origin=='PSEUDO_LIVE_SYNTHETIC':
            for k in ['generator_policy_version','generator_identity','generation_config_hash','response_binding_input_sha256']:
                if c.get(k) in (None,''): errs.append(f'{tag}: pseudo-live response requires {k}')
            if not goodhash(c.get('generation_config_hash')): errs.append(f'{tag}: generation_config_hash missing/invalid')
            if not goodhash(c.get('response_binding_input_sha256')): errs.append(f'{tag}: response_binding_input_sha256 missing/invalid')
            if goodhash(c.get('effective_input_sha256')) and goodhash(c.get('response_binding_input_sha256')) and c.get('effective_input_sha256')!=c.get('response_binding_input_sha256'):
                errs.append(f'{tag}: pseudo-live input binding differs from effective input; regenerate response')
    art=d.get('final_artifact') or {}
    for k in ['artifact_path','producer_node_id']:
        if not art.get(k): errs.append(f'final_artifact.{k} required')
    if not goodhash(art.get('artifact_sha256')): errs.append('final_artifact.artifact_sha256 missing/invalid')
    if art.get('declared_graph_lineage') is not True: errs.append('final_artifact.declared_graph_lineage must be true')
    if art.get('post_generation_mutation') is not False: errs.append('final_artifact.post_generation_mutation must be false')
    if d.get('expected_or_reference_visible_to_generator') is not False: errs.append('expected_or_reference_visible_to_generator must be false')
    if d.get('fixture_mutated_after_run_start') is not False: errs.append('fixture_mutated_after_run_start must be false')
    return emit(errs,out,mode,cand,calls,art)
if __name__=='__main__':
    if len(sys.argv)!=3:
        print('usage: validate_model_response_provenance.py MODEL_CALL_EVIDENCE.json REPORT.json',file=sys.stderr); sys.exit(2)
    sys.exit(main(sys.argv[1],sys.argv[2]))
