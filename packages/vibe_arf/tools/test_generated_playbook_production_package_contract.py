#!/usr/bin/env python3
from pathlib import Path
import json, sys
R=Path(__file__).resolve().parents[1]
checks=[]
def ck(name, cond, detail=''):
    checks.append((name,bool(cond),detail))

policy=R/'source/generated-playbook-production-package-policy.json'
manifest=R/'PRODUCTION_PACKAGE_CONTRACT.json'
builder=R/'tools/build_production_playbook_package.py'
validator=R/'tools/validate_production_playbook_package.py'
ck('policy_exists',policy.is_file())
ck('manifest_exists',manifest.is_file())
ck('builder_exists',builder.is_file())
ck('validator_exists',validator.is_file())
if policy.is_file():
    p=json.loads(policy.read_text())
    ck('default_is_dev_or_legacy_production',p.get('default_package_profile') in {'edit','dev','production'})
    tiers=p.get('package_profiles',{})
    prod=tiers.get('edit') or tiers.get('dev') or tiers.get('production',{})
    req=set(prod.get('required_surfaces',[]))
    ck('production_self_contained', {'runtime','source','data_layer','analyst_context','authoring_templates','reusable_patterns','editor','validation','materialization'} <= req)
    excl=set(prod.get('excluded_classes',[]))
    ck('production_excludes_debug_baggage', {'development_history','intermediate_reports','large_traces','screenshots','golden_reference_artifacts','interpreter_cache'} <= excl)
    ck('debug_separate', 'debug_handoff' in tiers)
if manifest.is_file():
    m=json.loads(manifest.read_text())
    classes={x.get('class'):x for x in m.get('artifact_classes',[])}
    for k in ['runtime','source','data_layer','analyst_context','authoring_templates','reusable_patterns','editor','validation','materialization']:
        ck('class_'+k,k in classes)
    ck('file_role_required', all({'class','default_inclusion','purpose'} <= set(x) for x in m.get('artifact_classes',[])))
    ck('forbidden_cache', any(x.get('class')=='interpreter_cache' and x.get('default_inclusion')=='forbidden' for x in m.get('artifact_classes',[])))
    ws=classes.get('workspace_metadata',{})
    ws_patterns=set(ws.get('patterns',[]))
    ck('workspace_metadata_forbidden', ws.get('default_inclusion')=='forbidden')
    ck('checkpoints_forbidden', 'checkpoints/**' in ws_patterns)
    ck('production_manifest_forbidden_as_input', 'PRODUCTION_PACKAGE_MANIFEST.json' in ws_patterns)

failed=[n for n,c,d in checks if not c]
print(json.dumps({'status':'PASS' if not failed else 'FAIL','passed':sum(c for _,c,_ in checks),'total':len(checks),'failed':failed},indent=2))
sys.exit(0 if not failed else 1)
