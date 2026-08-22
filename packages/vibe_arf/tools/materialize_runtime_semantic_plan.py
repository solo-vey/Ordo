#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
import yaml
from pathlib import Path

def sha(p:Path): return hashlib.sha256(p.read_bytes()).hexdigest()
def kit_root(ex:Path):
    hits=[p.parent for p in ex.rglob('ordo_simulate.py') if p.is_file()]
    if len(hits)!=1: raise RuntimeError('simulation kit root ambiguous')
    return hits[0]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); a=ap.parse_args(); root=Path(a.root).resolve()
    actor_proj=root/'tools/materialize_runtime_actor_projection.py'
    pp=subprocess.run([sys.executable,str(actor_proj),str(root)],cwd=root,capture_output=True,text=True,timeout=30)
    if pp.returncode: raise SystemExit('RUNTIME_ACTOR_PROJECTION_FAIL:'+(pp.stderr or pp.stdout)[-3000:])
    dep=json.loads((root/'verification/SIMULATION_KIT_DEPENDENCY.json').read_text()); z=root/dep['path']
    if sha(z)!=dep['sha256']: raise SystemExit('SIMULATION_KIT_DEPENDENCY_HASH_MISMATCH')
    # Deterministic fast path: reuse an already validated runtime plan only when every
    # authoritative derivation input and the artifact hash still match provenance.
    plan_path=root/'runtime_semantic_plan.json'; prov_path=root/'verification/RUNTIME_SEMANTIC_PLAN_PROVENANCE.json'
    state_inputs=['design/variable_catalog.yaml','authoring_templates/reusable/EDITOR_PROJECTION.template.yaml']
    if plan_path.is_file() and prov_path.is_file():
        try: cached=json.loads(prov_path.read_text())
        except Exception: cached={}
        expected_inputs=[{'path':r,'sha256':sha(root/r)} for r in state_inputs if (root/r).is_file()]
        cache_ok=(cached.get('status')=='PASS' and cached.get('validation_status')=='PASS'
                  and cached.get('artifact_sha256')==sha(plan_path)
                  and cached.get('canonical_source_sha256')==sha(root/'source/program.ordo.yaml')
                  and cached.get('runtime_projection_sha256')==sha(root/'runtime_projection/program.ordo.yaml')
                  and cached.get('state_type_registry_inputs')==expected_inputs
                  and cached.get('simulation_kit_version')==dep.get('version')
                  and cached.get('runtime_baseline')==dep.get('runtime_baseline'))
        if cache_ok:
            plan=json.loads(plan_path.read_text())
            print(json.dumps({'status':'PASS','cache':'validated_provenance','artifact_sha256':cached['artifact_sha256'],'elements':len(plan.get('elements') or {}),'compiler_issues':cached.get('compiler_issue_count',0)},indent=2))
            return
        # Provenance-only rebind: if the already validated plan contains an exact
        # semantic_source copy of every projected node/gate and the exact current state
        # schema, its derived execution semantics are unchanged. Rebind only identity
        # hashes; any semantic drift falls through to the cold compiler path.
        try:
            proj=yaml.safe_load((root/'runtime_projection/program.ordo.yaml').read_text()) or {}
            plan=json.loads(plan_path.read_text())
            elements=plan.get('elements') or {}
            current_items={}
            for section in ('nodes','gates'):
                for item in proj.get(section) or []:
                    if isinstance(item,dict) and item.get('id'): current_items[str(item['id'])]=item
            semantic_equal=(set(current_items).issubset(set(elements)) and
                            all(elements[i].get('semantic_source')==item for i,item in current_items.items()) and
                            (plan.get('state') or {}).get('schema')==((proj.get('state') or {}).get('schema')))
            # State-type registry files may change in metadata that the compiler does not
            # consume. Permit provenance rebind only when a separately materialized,
            # machine-readable equivalence proof ties the cached hashes to the current
            # hashes and proves the compiler-relevant declarations are identical.
            registry_equiv=False
            equiv_path=root/'verification/RUNTIME_STATE_TYPE_REGISTRY_SEMANTIC_EQUIVALENCE.json'
            if equiv_path.is_file():
                try:
                    equiv=json.loads(equiv_path.read_text())
                    by_path={str(x.get('path')):x for x in (equiv.get('files') or []) if isinstance(x,dict)}
                    cached_by={str(x.get('path')):str(x.get('sha256')) for x in (cached.get('state_type_registry_inputs') or []) if isinstance(x,dict)}
                    current_by={str(x.get('path')):str(x.get('sha256')) for x in expected_inputs}
                    registry_equiv=(equiv.get('status')=='PASS' and set(cached_by)==set(current_by)==set(by_path) and
                                    all(bool(by_path[r].get('semantically_equal_for_compiler')) and
                                        str(by_path[r].get('baseline_sha256'))==cached_by[r] and
                                        str(by_path[r].get('current_sha256'))==current_by[r]
                                        for r in current_by))
                except Exception:
                    registry_equiv=False
            registry_inputs_equal=(cached.get('state_type_registry_inputs')==expected_inputs or registry_equiv)
            inputs_equal=(registry_inputs_equal and
                          cached.get('simulation_kit_version')==dep.get('version') and
                          cached.get('runtime_baseline')==dep.get('runtime_baseline') and
                          cached.get('validation_status')=='PASS')
            if semantic_equal and inputs_equal:
                plan.setdefault('source',{})['program']='source/program.ordo.yaml'
                plan['source']['sha256']=sha(root/'runtime_projection/program.ordo.yaml')
                plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
                cached['artifact_sha256']=sha(plan_path)
                cached['canonical_source_sha256']=sha(root/'source/program.ordo.yaml')
                cached['runtime_projection_sha256']=sha(root/'runtime_projection/program.ordo.yaml')
                cached['state_type_registry_inputs']=expected_inputs
                cached['derivation']='semantic-equivalence provenance rebind over exact projected nodes, gates, state schema and unchanged-or-proven-equivalent registry/compiler identities'
                if registry_equiv:
                    cached['state_type_registry_semantic_equivalence']='verification/RUNTIME_STATE_TYPE_REGISTRY_SEMANTIC_EQUIVALENCE.json'
                prov_path.write_text(json.dumps(cached,ensure_ascii=False,indent=2)+'\n')
                print(json.dumps({'status':'PASS','cache':'semantic_equivalence_rebind','artifact_sha256':cached['artifact_sha256'],'elements':len(elements),'compiler_issues':cached.get('compiler_issue_count',0)},indent=2))
                return
        except Exception:
            pass
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); ex=td/'kit'; ex.mkdir(); zipfile.ZipFile(z).extractall(ex); kit=kit_root(ex)
        comp=kit/'runtime_core/integrated_compiler/compile_runtime_semantic_plan_v7.py'
        val=kit/'runtime_core/integrated_compiler/validate_runtime_semantic_plan_v7.py'
        cr=comp.parent
        stage=td/'stage'; (stage/'source').mkdir(parents=True)
        shutil.copy2(root/'runtime_projection/program.ordo.yaml',stage/'source/program.ordo.yaml')
        # Compiler state-type discovery is content-based. Preserve every package YAML that actually declares variables.
        copied=[]
        for rel in ['design/variable_catalog.yaml','authoring_templates/reusable/EDITOR_PROJECTION.template.yaml']:
            p=root/rel
            if p.is_file():
                dst=stage/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dst); copied.append(rel)
        out=stage/'runtime_semantic_plan.json'; env=dict(os.environ); env['PYTHONPATH']=str(cr)+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
        cp=subprocess.run([sys.executable,str(comp),str(stage/'source/program.ordo.yaml'),'-o',str(out)],cwd=stage,env=env,capture_output=True,text=True,timeout=120)
        if cp.returncode or not out.is_file(): raise SystemExit('RUNTIME_SEMANTIC_PLAN_COMPILE_FAIL:'+(cp.stderr or cp.stdout)[-3000:])
        vp=subprocess.run([sys.executable,str(val),str(out)],cwd=stage,env=env,capture_output=True,text=True,timeout=120)
        try: vr=json.loads(vp.stdout or '{}')
        except: vr={'status':'FAIL','raw':(vp.stdout or vp.stderr)[-3000:]}
        if vp.returncode or vr.get('status')!='PASS': raise SystemExit('RUNTIME_SEMANTIC_PLAN_VALIDATE_FAIL:'+json.dumps(vr,ensure_ascii=False))
        shutil.copy2(out,root/'runtime_semantic_plan.json')
        plan=json.loads(out.read_text())
        prov={'schema_version':'1.0','status':'PASS','artifact':'runtime_semantic_plan.json','artifact_sha256':sha(root/'runtime_semantic_plan.json'),
              'canonical_source':'source/program.ordo.yaml','canonical_source_sha256':sha(root/'source/program.ordo.yaml'),'runtime_projection':'runtime_projection/program.ordo.yaml','runtime_projection_sha256':sha(root/'runtime_projection/program.ordo.yaml'),'actor_projection_provenance':'runtime_projection/ACTOR_PROJECTION_PROVENANCE.json',
              'compiler_version':plan.get('compiler_version'),'simulation_kit_version':dep['version'],'runtime_baseline':dep['runtime_baseline'],
              'state_type_registry_inputs':[{'path':r,'sha256':sha(root/r)} for r in copied],
              'validation_status':vr.get('status'),'structural_status':vr.get('structural_status'),'semantic_status':vr.get('semantic_status'),
              'compiler_issue_count':len(vr.get('compiler_issues') or []),'derivation':'compiler-safe runtime actor projection derived from canonical source plus complete content-discovered state-type registry set'}
        (root/'verification/RUNTIME_SEMANTIC_PLAN_PROVENANCE.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'status':'PASS','artifact_sha256':prov['artifact_sha256'],'elements':len(plan.get('elements') or {}),'compiler_issues':prov['compiler_issue_count']},indent=2))
if __name__=='__main__': main()
