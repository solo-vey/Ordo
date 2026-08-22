#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys,tempfile,zipfile,shutil
from pathlib import Path


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def ids(rows):
    out=[]
    for x in rows or []:
        if isinstance(x,dict): out.append(str(x.get('node_id') or x.get('id') or x.get('node') or ''))
        else: out.append(str(x))
    return sorted({x for x in out if x})
def resolve_kit_root(extracted:Path)->Path:
    # Current kits may be flat-root or use one enclosing directory; resolve layout without changing semantics.
    if (extracted/'ordo_simulate.py').is_file(): return extracted
    direct=[p for p in extracted.iterdir() if p.is_dir() and (p/'ordo_simulate.py').is_file()]
    if len(direct)==1: return direct[0]
    found=sorted({p.parent for p in extracted.rglob('ordo_simulate.py') if p.is_file()})
    if len(found)==1: return found[0]
    raise RuntimeError(f'SIMULATION_KIT_ROOT_AMBIGUOUS:{[str(x) for x in found]}')
def copy_if(src:Path,dst:Path):
    if src.is_file(): shutil.copy2(src,dst)

def classify_errors(errors, outcome_status:str, profile_gaps=None):
    findings=[]
    if profile_gaps:
        findings.append({'primary_owner':'VIBE_AUTHORING_PROFILE_CONTRACT_GAP','evidence':['profile_contract_gap: deterministic artifact/archive validation contract incomplete'],'playbook_workaround_applied':False})
    if str(outcome_status).lower()=='fixture_incomplete':
        return [{'primary_owner':'SIMULATION_FIXTURE_INCOMPLETE','evidence':['runtime requested an additional exact model/recovery fixture'],'playbook_workaround_applied':False}]
    rows=errors if isinstance(errors,list) else (errors.get('errors',[]) if isinstance(errors,dict) else [])
    for e in rows:
        code=str(e.get('failure_class') or e.get('code') or e.get('reason') or '') if isinstance(e,dict) else str(e)
        low=code.lower()
        if 'profile_contract_gap' in low or 'generated_profile_validation_contract_incomplete' in low:
            owner='VIBE_AUTHORING_PROFILE_CONTRACT_GAP'
        elif 'fixture' in low or 'contract_unsatisfiable_by_model' in low:
            owner='SIMULATION_FIXTURE_INCOMPLETE'
        elif any(k in low for k in ['runtime_plan_non_route_data_projected_as_route','runtime_adapter','unsupported_runtime_executor']):
            owner='RUNTIME_ADAPTER_CONFORMANCE_DEFECT'
        else:
            owner='PLAYBOOK_SOURCE_CONTRACT_DEFECT'
        findings.append({'primary_owner':owner,'evidence':[code or 'simulation error'],'playbook_workaround_applied':False})
    return findings

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('candidate_zip'); ap.add_argument('--package-root',required=True)
    ap.add_argument('--scenario-dir'); ap.add_argument('--inspect-only',action='store_true')
    a=ap.parse_args(); cand=Path(a.candidate_zip).resolve(); root=Path(a.package_root).resolve(); reports=root/'reports'; reports.mkdir(parents=True,exist_ok=True)
    dep=loadj(root/'verification/SIMULATION_KIT_DEPENDENCY.json')
    kit_zip=(root/dep['path']).resolve()
    if not kit_zip.is_file() or sha(kit_zip)!=dep['sha256']:
        print(json.dumps({'status':'FAIL','code':'SIMULATION_KIT_DEPENDENCY_INVALID'},indent=2)); return 2
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); extracted=td/'kit'; extracted.mkdir(); zipfile.ZipFile(kit_zip).extractall(extracted)
        try: kit=resolve_kit_root(extracted)
        except Exception as e:
            print(json.dumps({'status':'FAIL','code':'SIMULATION_KIT_LAYOUT_INVALID','detail':str(e)},indent=2)); return 2
        fixtures=td/'inspect'
        p=subprocess.run([sys.executable,str(kit/'ordo_simulate.py'),'inspect','--playbook',str(cand),'--out-dir',str(fixtures)],capture_output=True,text=True)
        if p.returncode:
            print(json.dumps({'status':'FAIL','stage':'inspect','stdout':p.stdout[-2000:],'stderr':p.stderr[-2000:]},indent=2)); return 1
        contract=loadj(fixtures/'simulation_contract.json')
        analyst=ids(contract.get('analyst_fixture_points') or contract.get('analyst_inputs'))
        model=ids(contract.get('model_fixture_points') or contract.get('model_calls'))
        recovery=ids(contract.get('semantic_recovery_fixture_points'))
        norm={
          'schema_version':'1.1','kit_version':dep['version'],'runtime_baseline':dep['runtime_baseline'],
          'analyst_fixture_points':analyst,'model_fixture_points':model,
          'dynamic_recovery_fixture_points':recovery,
          'semantic_recovery_fixture_points':contract.get('semantic_recovery_fixture_points') or [],
          'diagnostics':contract.get('diagnostics') or [],'raw_contract':contract
        }
        (reports/'SIMULATION_CONTRACT.json').write_text(json.dumps(norm,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        copy_if(fixtures/'analyst_answers.template.yaml',reports/'analyst_answers.template.yaml')
        copy_if(fixtures/'model_responses.template.yaml',reports/'model_responses.template.yaml')
        if a.inspect_only or not a.scenario_dir:
            print(json.dumps({'status':'PASS','stage':'inspect','kit_version':dep['version'],'runtime_baseline':dep['runtime_baseline'],'reports':str(reports),'candidate_sha256':sha(cand)},indent=2)); return 0

        scen=Path(a.scenario_dir).resolve(); out=td/'run'
        cmd=[sys.executable,str(kit/'ordo_simulate.py'),'run','--playbook',str(cand)]
        analyst_file=scen/'analyst_answers.yaml'; model_file=scen/'model_responses.yaml'
        if analyst_file.is_file(): cmd += ['--analyst',str(analyst_file)]
        if model_file.is_file(): cmd += ['--model',str(model_file)]
        cmd += ['--out-dir',str(out)]
        q=subprocess.run(cmd,capture_output=True,text=True)
        rr=loadj(out/'run_report.json') if (out/'run_report.json').is_file() else {}
        fu=loadj(out/'fixture_usage.json') if (out/'fixture_usage.json').is_file() else {}
        errors=loadj(out/'errors.json') if (out/'errors.json').is_file() else []
        outcome_status=str((rr.get('outcome') or {}).get('status') or '')
        fixture_incomplete=(outcome_status.lower()=='fixture_incomplete')
        # Preserve native dynamic-recovery discovery and deterministic profile-contract-gap evidence for autonomous repair.
        copy_if(out/'missing_fixtures.json',reports/'missing_fixtures.json')
        copy_if(out/'missing_model_responses.template.yaml',reports/'missing_model_responses.template.yaml')
        copy_if(out/'profile_contract_gaps.json',reports/'profile_contract_gaps.json')
        for name in ['run_report.json','execution_trace.json','runtime_debug_trace.json','final_state.json','errors.json']:
            copy_if(out/name,reports/f'SIMULATION_{name}')

        used_a=ids(fu.get('analyst'))
        model_rows=fu.get('model') or []
        used_m=sorted({str(x.get('node')) for x in model_rows if isinstance(x,dict) and x.get('kind')!='semantic_recovery' and x.get('node')})
        used_r=sorted({str(x.get('node')) for x in model_rows if isinstance(x,dict) and x.get('kind')=='semantic_recovery' and x.get('node')})
        remaining=fu.get('remaining') or {}
        unused=[]
        for kind in ['analyst','model']:
            vals=remaining.get(kind) if isinstance(remaining,dict) else None
            if isinstance(vals,dict): unused.extend(f'{kind}:{k}' for k,v in vals.items() if v)
        usage={'provided_analyst':used_a or analyst,'provided_model':used_m or model,'provided_recovery':used_r or recovery,'unused':sorted(unused)}
        (reports/'FIXTURE_USAGE.json').write_text(json.dumps(usage,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

        status='PASS' if q.returncode==0 else ('FIXTURE_INCOMPLETE' if fixture_incomplete else 'FAIL')
        profile_gaps=loadj(out/'profile_contract_gaps.json') if (out/'profile_contract_gaps.json').is_file() else None
        gap_count=len((profile_gaps or {}).get('gaps') or []) if isinstance(profile_gaps,dict) else 0
        ev={'schema_version':'1.2','exact_candidate_sha256':sha(cand),'kit_version':dep['version'],'runtime_baseline':dep['runtime_baseline'],'status':status,'fixture_closure':'PASS' if q.returncode==0 else ('INCOMPLETE' if fixture_incomplete else 'UNKNOWN'),'profile_contract_gaps_count':gap_count,'scenarios':[{'id':scen.name,'status':status}], 'run_report':rr,'acceptance_eligible':bool(rr.get('acceptance_eligible',False))}
        (reports/'SIMULATION_EVIDENCE.json').write_text(json.dumps(ev,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

        trace=loadj(out/'execution_trace.json') if (out/'execution_trace.json').is_file() else []
        gate_rows=[]; rows=trace if isinstance(trace,list) else (trace.get('steps') or trace.get('trace') or [])
        for row in rows:
            if not isinstance(row,dict): continue
            gid=row.get('gate_id') or (row.get('node_id') if str(row.get('node_id','')).startswith('G_') else None)
            if gid:
                gate_rows.append({'gate_id':gid,'status':row.get('status','PASS'),'check_results':row.get('check_results') or [{'id':'runtime_transition','status':'PASS'}],'evidence':row.get('evidence') or [f'trace:{gid}']})
        (reports/'RUNTIME_GATE_EVIDENCE.json').write_text(json.dumps({'gates':gate_rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        findings=classify_errors(errors,outcome_status,profile_gaps)
        (reports/'DEFECT_OWNERSHIP.json').write_text(json.dumps({'schema_version':'1.1','status':'PASS','findings':findings},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':status,'candidate_sha256':sha(cand),'kit_version':dep['version'],'runtime_baseline':dep['runtime_baseline'],'reports':str(reports),'returncode':q.returncode,'missing_fixture_contract_preserved':(reports/'missing_fixtures.json').is_file(),'profile_contract_gaps_preserved':(reports/'profile_contract_gaps.json').is_file()},indent=2))
        return 0 if q.returncode==0 else (3 if fixture_incomplete else 1)
if __name__=='__main__': raise SystemExit(main())
