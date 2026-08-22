from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1]
errs=[]
def load(p): return json.load(open(R/p))
p=load('source/lifecycle-release-family-governance-policy.json')
for req in ['source/release-family-manifest.schema.json','source/validation-capability-matrix.json','source/tool-purity-contract.schema.json','source/execution-engine-parity-policy.json','source/learning-extraction-policy.json','source/release-coverage-thresholds.json']:
    if not (R/req).exists(): errs.append('missing:'+req)
mat=load('source/validation-capability-matrix.json')
if list(mat['levels'])!=['L0','L1','L2','L3','L4']: errs.append('validation_levels')
par=load('source/execution-engine-parity-policy.json')
if set(par['required_equal'])!={'target_bundle_identity','planner_contract','write_engine','verification_engine'}: errs.append('parity')
cov=load('source/release-coverage-thresholds.json')
if any(v!=100 for v in cov['minimums'].values()): errs.append('coverage_threshold')
learn=load('source/learning-extraction-policy.json')
if set(learn['classes'])!={'SESSION_EXECUTION_ERROR','DOMAIN_CONTRACT_DISCOVERY','FRAMEWORK_PROCESS_DEFECT','PLATFORM_LIMITATION'}: errs.append('learning')
prod=load('source/generated-playbook-production-package-policy.json')
edit=prod['package_profiles']['edit']['required_surfaces']
if 'data_layer' not in edit: errs.append('edit_missing_data_layer')
rel=load('source/release-distribution-profile-policy.json')
if rel['release_requires']!=['EDIT','CLI_RUN','MODEL_RUN']: errs.append('profiles')
print('ALPHA46 P2 GOVERNANCE:', 'PASS' if not errs else 'FAIL', 'errors='+str(len(errs)))
for e in errs: print('ERROR',e)
sys.exit(bool(errs))
