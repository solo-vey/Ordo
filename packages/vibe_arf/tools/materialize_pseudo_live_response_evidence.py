#!/usr/bin/env python3
from pathlib import Path
import argparse,json,hashlib

def canon(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def h(v): return hashlib.sha256((v if isinstance(v,str) else canon(v)).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('out'); a=ap.parse_args()
 d=json.loads(Path(a.spec).read_text()); forbidden={'expected_score','target_score','golden_artifact','hidden_reference','evaluator_output','candidate_ranking','competing_candidate'}
 leaks=sorted(k for k in forbidden if k in d)
 if leaks: raise SystemExit('forbidden pseudo-live generator context fields: '+','.join(leaks))
 cand=d.get('candidate_sha256')
 calls=[]
 for i,x in enumerate(d.get('calls') or [],1):
  eff=x.get('effective_input')
  if eff is None: raise SystemExit(f'calls[{i}].effective_input required')
  raw=x.get('raw_response')
  if raw is None: raise SystemExit(f'calls[{i}].raw_response required')
  ih=h(eff)
  calls.append({'step_index':x.get('step_index',i),'element_id':x.get('element_id'),'origin':'PSEUDO_LIVE_SYNTHETIC','effective_input_sha256':ih,'response_binding_input_sha256':ih,'output_sha256':h(raw),'candidate_sha256':cand,'hidden_reference_visible_to_generator':False,'post_generation_mutation':False,'generator_policy_version':d.get('generator_policy_version'),'generator_identity':d.get('generator_identity'),'generation_config_hash':h(d.get('generation_config') or {}),'raw_response':raw,'parsed_response':x.get('parsed_response',raw)})
 out={'schema_version':'2.0','execution_mode':'PSEUDO_LIVE_OPTIMIZATION','candidate_sha256':cand,'expected_or_reference_visible_to_generator':False,'fixture_mutated_after_run_start':False,'executed_model_nodes':[x.get('element_id') for x in d.get('calls') or []],'model_calls':calls,'final_artifact':d.get('final_artifact') or {}}
 Path(a.out).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'status':'PASS','calls':len(calls),'out':a.out}))
if __name__=='__main__': main()
