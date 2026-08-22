#!/usr/bin/env python3
from pathlib import Path
import json, shutil, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def ck(i,ok,d=''): checks.append({'id':i,'status':'PASS' if ok else 'FAIL','detail':d})

policy=ROOT/'source/dependency-aware-validation-policy.json'
ck('POLICY_PRESENT',policy.is_file())
if policy.is_file():
    try: p=json.loads(policy.read_text())
    except Exception as e: p={}; ck('POLICY_PARSE',False,str(e))
    else:
        ck('POLICY_PARSE',True)
        ck('FAST_FULL_CLASSES',set((p.get('validation_classes') or {}).keys())=={'FAST','FULL'})
        ck('FAST_IS_IMPACTED_ONLY',(p.get('validation_classes') or {}).get('FAST',{}).get('selection')=='dependency_aware_impacted')
        ck('FULL_ONLY_FINAL_BOUNDARY',(p.get('validation_classes') or {}).get('FULL',{}).get('allowed_modes')==['CANDIDATE','RELEASE'])
        ck('FULL_FORBIDDEN_DURING_EDIT',(p.get('validation_classes') or {}).get('FAST',{}).get('forbids_full_suite') is True)

impact=ROOT/'verification_impact_map.json'
try: im=json.loads(impact.read_text())
except Exception as e: im={}; ck('IMPACT_MAP_PARSE',False,str(e))
else:
    ck('IMPACT_MAP_PARSE',True)
    modes=im.get('modes') or {}
    ck('MODE_CLASS_MAPPING',all(modes.get(m,{}).get('validation_class')=='FAST' for m in ['PATCH','CHECKPOINT']) and modes.get('CANDIDATE',{}).get('validation_class')=='TARGETED' and modes.get('RELEASE',{}).get('validation_class')=='FULL')
    ck('NO_FULL_IN_FAST',not modes.get('PATCH',{}).get('full_pre_editor') and not modes.get('CHECKPOINT',{}).get('full_pre_editor'))
    ck('FULL_AT_FINAL_ONLY',not modes.get('CANDIDATE',{}).get('full_pre_editor') and modes.get('RELEASE',{}).get('full_pre_editor'))
    rules=im.get('path_rules') or []
    required={
      'source/data-layer-first-hard-architecture-policy.json':'data_layer_first_hard_architecture',
      'source/reusable-authoring-template-policy.json':'reusable_authoring_templates',
      'source/quality_acceptance_policy.json':'hybrid_reference_fidelity_feedback',
      'source/deterministic-first-execution-policy.json':'deterministic_first_execution',
      'source/information-preservation-policy.json':'information_preservation_monotonic_evidence',
      'source/editor-visible-architecture-policy.json':'editor_visible_architecture',
    }
    for path,cid in required.items():
        hit=[r for r in rules if path in (r.get('globs') or []) and cid in (r.get('checks') or []) and r.get('exclusive') is True]
        ck('SPECIFIC_RULE_'+cid.upper(),bool(hit),repr(hit))

ext=ROOT/'verification/PROFILE_EXTENSIONS.json'
try: ex=json.loads(ext.read_text())
except Exception as e: ex={}; ck('PROFILE_EXT_PARSE',False,str(e))
else:
    ids={c.get('id') for c in ex.get('checks',[])}
    required_ids={
      'scoring_v3_development_acceptance','constructive_correctness','data_layer_first_hard_architecture',
      'reusable_authoring_templates','hybrid_reference_fidelity_feedback','deterministic_first_execution',
      'information_preservation_monotonic_evidence','dynamic_multi_reference_comparative_evaluator',
      'editor_visible_architecture','fast_full_dependency_aware_validation'}
    ck('WORKING_TARGETED_CHECKS_REGISTERED',required_ids <= ids,repr(sorted(required_ids-ids)))

runner=ROOT/'tools/run_incremental_verification.py'
src=runner.read_text() if runner.is_file() else ''
ck('RUNNER_SUPPORTS_EXCLUSIVE_RULES','exclusive' in src)
ck('RUNNER_REPORTS_VALIDATION_CLASS','validation_class' in src)
ck('RUNNER_REPORTS_SELECTION_REASONS','selection_reasons' in src)

# Behavioral dry-selection: changing only editor-visible policy must not drag generic source suite.
if runner.is_file():
    with tempfile.TemporaryDirectory() as td0:
        td=Path(td0)/'pkg'; shutil.copytree(ROOT,td,ignore=shutil.ignore_patterns('.verification_cache','.dev_checkpoint.json','reports'))
        cp=td/'.dev_checkpoint.json'
        c=subprocess.run([sys.executable,str(td/'tools/create_verification_checkpoint.py'),str(td),'--output',str(cp)],capture_output=True,text=True,timeout=30)
        if c.returncode==0:
            q=td/'source/editor-visible-architecture-policy.json'
            q.write_text(q.read_text()+'\n')
            r=subprocess.run([sys.executable,str(td/'tools/run_incremental_verification.py'),str(td),'--mode','PATCH','--checkpoint',str(cp),'--dry-select'],capture_output=True,text=True,timeout=30)
            try: out=json.loads(r.stdout[r.stdout.find('{'):])
            except Exception: out={}
            selected=out.get('selected_checks') or []
            ck('EDITOR_POLICY_SELECTS_TARGETED_FAST',r.returncode==0 and selected==['editor_visible_architecture'],repr(selected))
            ck('EDITOR_POLICY_DOES_NOT_SELECT_HEAVY_HISTORY','alpha20_generated_playbook_regression_layer' not in selected and 'simulation_kit_dependency_integrity' not in selected,repr(selected))
            ck('DRY_SELECTION_CLASS_FAST',out.get('validation_class')=='FAST',repr(out.get('validation_class')))
            ck('SELECTION_REASON_RECORDED',bool(out.get('selection_reasons')),repr(out.get('selection_reasons')))
        else:
            ck('EDITOR_POLICY_SELECTS_TARGETED_FAST',False,c.stderr[-500:])
            ck('EDITOR_POLICY_DOES_NOT_SELECT_HEAVY_HISTORY',False)
            ck('DRY_SELECTION_CLASS_FAST',False)
            ck('SELECTION_REASON_RECORDED',False)

ok=all(x['status']=='PASS' for x in checks)
print(json.dumps({'status':'PASS' if ok else 'FAIL','tests_total':len(checks),'tests_passed':sum(x['status']=='PASS' for x in checks),'checks':checks},indent=2))
raise SystemExit(0 if ok else 1)
