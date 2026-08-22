#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys, tempfile, shutil
ROOT=Path(__file__).resolve().parents[1]
passes=0; fails=0

def chk(name, cond, detail=''):
    global passes,fails
    if cond:
        passes+=1; print('PASS',name)
    else:
        fails+=1; print('FAIL',name,detail)

# Blocker A: PATCH/CHECKPOINT may never be escalated to CANDIDATE/RELEASE by path rules.
impact=json.loads((ROOT/'verification_impact_map.json').read_text())
chk('no_candidate_minimum_mode_path_rules', all(r.get('minimum_mode') not in {'CANDIDATE','RELEASE'} for r in impact.get('path_rules',[])))
# dry selection against synthetic checkpoint with only canonical_support changed
with tempfile.TemporaryDirectory() as td:
    t=Path(td); shutil.copytree(ROOT,t/'pkg',dirs_exist_ok=True); pkg=t/'pkg'
    cp=pkg/'.blocker_checkpoint.json'
    # make checkpoint current then mutate canonical_support file
    inv={}
    import hashlib, fnmatch
    def ignored(rel): return any(fnmatch.fnmatch(rel,g) for g in impact.get('ignore_globs',[]))
    for p in sorted(pkg.rglob('*')):
        if p.is_file():
            rel=p.relative_to(pkg).as_posix()
            if not ignored(rel): inv[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
    cp.write_text(json.dumps({'files':inv,'passed_checks':{}}))
    target=next((p for p in (pkg/'canonical_support').rglob('*') if p.is_file()),None)
    if target:
        target.write_bytes(target.read_bytes()+b'\n')
        out=subprocess.check_output([sys.executable,str(pkg/'tools/run_incremental_verification.py'),str(pkg),'--mode','CHECKPOINT','--checkpoint',str(cp),'--dry-select'],text=True)
        rep=json.loads(out)
        chk('checkpoint_stays_checkpoint', rep['effective_mode']=='CHECKPOINT', rep.get('effective_mode'))
        chk('checkpoint_stays_fast', rep['validation_class']=='FAST', rep.get('validation_class'))
    else:
        chk('checkpoint_stays_checkpoint',False,'no canonical_support file'); chk('checkpoint_stays_fast',False,'no canonical_support file')

# Blocker B: selected golden refs are materialized into evaluator-only bundle and never exposed to optimizer.
policy_path=ROOT/'source/evaluator-reference-input-bundle-policy.json'
chk('reference_bundle_policy_exists', policy_path.is_file())
if policy_path.is_file():
    p=json.loads(policy_path.read_text())
    chk('bundle_evaluator_only', p.get('access_scope')=='evaluator_only')
    chk('optimizer_denied', 'optimizer' in p.get('denied_consumers',[]))
    chk('generator_denied', 'generator' in p.get('denied_consumers',[]))
for f in ['tools/build_evaluator_reference_bundle.py','tools/validate_evaluator_reference_bundle.py']:
    chk(f'{Path(f).name}_exists',(ROOT/f).is_file())

mod=(ROOT/'source/modules/30_vibe_architecture.ordo.module.yaml').read_text()
chk('bundle_node_exists','N_AI_BUILD_EVALUATOR_REFERENCE_BUNDLE' in mod)
chk('bundle_validator_gate_exists','G_AI_EVALUATOR_REFERENCE_BUNDLE_VALID' in (ROOT/'source/modules/60_validation_outputs.ordo.module.yaml').read_text())
# evaluator node must reference bundle path, not analyst context directly only
idx=mod.find('- id: N_AI_RUN_FRESH_COMPARATIVE_EVALUATOR')
frag=mod[idx:idx+2200] if idx>=0 else ''
chk('fresh_evaluator_gets_bundle','evaluator/reference_bundle' in frag or 'improvement_evaluator_reference_bundle' in frag)
# sanitizer remains before optimizer handoff
chk('sanitizer_present','N_AI_SANITIZE_EVALUATION_DEFECTS' in mod)
print(json.dumps({'passes':passes,'fails':fails}))
raise SystemExit(1 if fails else 0)
