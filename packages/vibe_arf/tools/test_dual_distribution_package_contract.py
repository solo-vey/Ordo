#!/usr/bin/env python3
from pathlib import Path
import json, sys
R=Path(__file__).resolve().parents[1]
checks=[]
def ck(name,cond,detail=''): checks.append((name,bool(cond),detail))
policy=R/'source/generated-playbook-production-package-policy.json'; contract=R/'DISTRIBUTION_PACKAGE_CONTRACT.json'; builder=R/'tools/build_three_profile_playbook_distribution.py'; validator=R/'tools/validate_distribution_package.py'
for n,p in [('policy',policy),('contract',contract),('builder',builder),('validator',validator)]: ck(n+'_exists',p.is_file())
if policy.is_file():
 p=json.loads(policy.read_text()); profiles=p.get('package_profiles',{})
 ck('edit_profile','edit' in profiles); ck('cli_run_profile','cli_run' in profiles); ck('model_run_profile','model_run' in profiles)
 ck('production_aliases_edit',profiles.get('production',{}).get('alias_of')=='edit')
 cli=profiles.get('cli_run',{}); model=profiles.get('model_run',{})
 ck('cli_reachability_based',cli.get('selection')=='jit_runtime_reachability_closure')
 ck('model_reachability_based',model.get('selection')=='jit_model_execution_reachability_closure')
 ck('model_forbidden_surfaces',{'authoring_data_layer','development_history','golden_reference_artifacts'} <= set(model.get('forbidden_surfaces',[])))
if contract.is_file():
 c=json.loads(contract.read_text()); d=c.get('profiles',{})
 ck('contract_three_profiles',{'EDIT','CLI_RUN','MODEL_RUN'} <= set(d))
 ck('source_identity_declared',bool(c.get('source_identity_files')))
 sid=set(c.get('source_identity_files') or []); ck('source_identity_canonical_only','source/program.ordo.yaml' in sid and not any(x.startswith('compiled/') for x in sid))
failed=[n for n,c,d in checks if not c]
print(json.dumps({'status':'PASS' if not failed else 'FAIL','passed':sum(c for _,c,_ in checks),'total':len(checks),'failed':failed},indent=2)); sys.exit(0 if not failed else 1)
