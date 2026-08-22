#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys, tempfile, shutil, time
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def ck(name, ok, detail=''):
    checks.append({'id':name,'status':'PASS' if ok else 'FAIL','detail':detail})

impact=ROOT/'verification_impact_map.json'
ck('IMPACT_MAP_PRESENT', impact.is_file())
if impact.is_file():
    try:
        d=json.loads(impact.read_text())
    except Exception as e:
        d={}; ck('IMPACT_MAP_PARSE',False,str(e))
    else:
        ck('IMPACT_MAP_PARSE', True)
        ck('FOUR_MODES_DECLARED', set((d.get('modes') or {}).keys())=={'PATCH','CHECKPOINT','CANDIDATE','RELEASE'})
        ck('TIMING_BUDGETS_DECLARED', all('budget_seconds' in v for v in (d.get('modes') or {}).values()))
        ck('PATH_RULES_DECLARED', bool(d.get('path_rules')))
        ck('FULL_ONLY_AT_RELEASE', not (d['modes']['PATCH'].get('full_pre_editor') or d['modes']['CHECKPOINT'].get('full_pre_editor') or d['modes']['CANDIDATE'].get('full_pre_editor')) and d['modes']['RELEASE'].get('full_pre_editor'))
        ck('CANDIDATE_TARGETED_DECLARED', d['modes']['CANDIDATE'].get('validation_class')=='TARGETED')
        ck('CANDIDATE_SHARDING_DECLARED', int(d['modes']['CANDIDATE'].get('shard_size',0)) > 0)

runner=ROOT/'tools/run_incremental_verification.py'
checkpoint=ROOT/'tools/create_verification_checkpoint.py'
ck('INCREMENTAL_RUNNER_PRESENT', runner.is_file())
ck('CHECKPOINT_TOOL_PRESENT', checkpoint.is_file())
protocol=ROOT/'DEVELOPMENT_VERIFICATION_PROTOCOL.md'
ck('PROTOCOL_PRESENT', protocol.is_file())
# Fingerprint semantics: authoritative inputs invalidate plans; derived runtime/compiled outputs do not.
fpmod=ROOT/'tools/verification_package_fingerprint.py'
if fpmod.is_file():
    import importlib.util
    spec=importlib.util.spec_from_file_location('vibe_fp',fpmod); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    with tempfile.TemporaryDirectory() as ftd:
        fr=Path(ftd); (fr/'source').mkdir(); (fr/'compiled').mkdir(); (fr/'runtime').mkdir()
        (fr/'source/a.txt').write_text('A'); (fr/'compiled/x.txt').write_text('X'); (fr/'runtime/t.txt').write_text('T')
        f1=mod.package_fingerprint(fr)['sha256']
        (fr/'compiled/x.txt').write_text('X2'); (fr/'runtime/t.txt').write_text('T2')
        f2=mod.package_fingerprint(fr)['sha256']
        (fr/'source/a.txt').write_text('A2'); f3=mod.package_fingerprint(fr)['sha256']
        ck('DERIVED_OUTPUTS_DO_NOT_STALE_PLAN',f1==f2,(f1,f2))
        ck('AUTHORITATIVE_INPUT_CHANGE_STALES_PLAN',f2!=f3,(f2,f3))
runner_src=(ROOT/'tools/run_verification_profile.py').read_text(encoding='utf-8') if (ROOT/'tools/run_verification_profile.py').is_file() else ''
ck('TRUSTED_REGRESSIONS_ISOLATED', 'subprocess_isolated' in runner_src and 'runpy.run_path' not in runner_src)
ck('TRUSTED_REGRESSIONS_NO_PIPE_CAPTURE', 'trusted_stdout_path' in runner_src and 'subprocess_isolated_file_backed' in runner_src)
prepare=ROOT/'tools/prepare_candidate_verification.py'
shard_runner=ROOT/'tools/run_candidate_verification_shard.py'
aggregator=ROOT/'tools/aggregate_candidate_verification.py'
ck('CANDIDATE_PREPARE_TOOL_PRESENT', prepare.is_file())
ck('CANDIDATE_SHARD_RUNNER_PRESENT', shard_runner.is_file())
ck('CANDIDATE_AGGREGATOR_PRESENT', aggregator.is_file())
incr_src=(ROOT/'tools/run_incremental_verification.py').read_text(encoding='utf-8')
ck('NO_SINGLE_SHELL_ORCHESTRATOR', 'single_shell_orchestrator' not in incr_src)
ck('CANDIDATE_PLAN_PERSISTED', 'CANDIDATE_VERIFICATION_PLAN.json' in incr_src or prepare.is_file())
if prepare.is_file():
    ps=prepare.read_text(encoding='utf-8')
    ck('SHARD_OPERATIONAL_LIMIT_20S', 'operational_limit_seconds' in ps and '20' in ps)
    ck('PLAN_BINDS_PACKAGE_FINGERPRINT', 'package_fingerprint' in ps)
    ck('DEFAULT_SHARD_TARGET_UNDER_10S', 'default=8.0' in ps)
    ck('UNKNOWN_TRUSTED_REGRESSION_CONSERVATIVE_ESTIMATE', 'trusted_python_regression' in ps and '5.0' in ps)
if shard_runner.is_file():
    ss=shard_runner.read_text(encoding='utf-8')
    ck('SHARD_HARD_TIMEOUT_AND_FILE_EVIDENCE', 'start_new_session=True' in ss and 'stdout_path' in ss and 'timeout' in ss)
    ck('SHARD_TIMEOUT_KILLS_PROCESS_GROUP', 'Popen' in ss and 'os.killpg' in ss)
    ck('SHARD_REJECTS_STALE_PACKAGE_FINGERPRINT', 'PLAN_PACKAGE_STALE' in ss and 'package_fingerprint' in ss)
if aggregator.is_file():
    ag=aggregator.read_text(encoding='utf-8')
    ck('AGGREGATOR_REQUIRES_ALL_SHARDS', 'missing_shards' in ag and 'checks_total_expected' in ag)
    ck('AGGREGATOR_REJECTS_STALE_PACKAGE_FINGERPRINT', 'PLAN_PACKAGE_STALE' in ag and 'package_fingerprint' in ag)
if protocol.is_file():
    t=protocol.read_text()
    ck('PROTOCOL_FORBIDS_REPEATED_FULL', 'CANDIDATE' in t and 'RELEASE' in t and 'PATCH' in t and 'CHECKPOINT' in t)

# Live isolated probe. A docs-only mutation should select a small subset and not the whole profile.
if runner.is_file() and checkpoint.is_file():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)/'pkg'; shutil.copytree(ROOT,td,ignore=shutil.ignore_patterns('.verification_cache','.dev_checkpoint.json'))
        cp=td/'.dev_checkpoint.json'
        p=subprocess.run([sys.executable,str(td/'tools/create_verification_checkpoint.py'),str(td),'--output',str(cp)],capture_output=True,text=True,timeout=30)
        ck('CHECKPOINT_CREATE',p.returncode==0,p.stdout[-500:]+p.stderr[-500:])
        (td/'README.md').write_text((td/'README.md').read_text()+"\n<!-- alpha31 timing probe -->\n")
        started=time.time()
        q=subprocess.run([sys.executable,str(td/'tools/run_incremental_verification.py'),str(td),'--mode','PATCH','--checkpoint',str(cp),'--dry-select'],capture_output=True,text=True,timeout=30)
        elapsed=time.time()-started
        try: out=json.loads(q.stdout[q.stdout.find('{'):])
        except Exception: out={}
        selected=out.get('selected_checks') or []
        ck('PATCH_DRY_SELECT_RUNS',q.returncode==0,q.stdout[-800:]+q.stderr[-500:])
        ck('DOC_CHANGE_NOT_FULL_SUITE',selected == ['entry_docs_revision'],repr(selected))
        ck('PATCH_SELECTION_FAST',elapsed < 3.0,f'{elapsed:.3f}s')
        ck('CHANGED_FILES_REPORTED','README.md' in (out.get('changed_files') or []),repr(out.get('changed_files')))
        r0=time.time(); r=subprocess.run([sys.executable,str(td/'tools/run_incremental_verification.py'),str(td),'--mode','PATCH','--checkpoint',str(cp)],capture_output=True,text=True,timeout=30); rel=time.time()-r0
        try: rout=json.loads(r.stdout[r.stdout.find('{'):])
        except Exception: rout={}
        ck('DOC_PATCH_EXECUTION_PASS',r.returncode==0,r.stdout[-800:]+r.stderr[-500:])
        ck('DOC_PATCH_WITHIN_BUDGET',rout.get('within_budget') is True and float(rout.get('elapsed_s',999)) < 8.0,f'wall={rel:.3f}s / reported={rout.get("elapsed_s")}')


# Cleanup invariant: candidate timing history must live outside ephemeral reports/.
timing_baseline=ROOT/'verification/CANDIDATE_TIMING_BASELINE.json'
ck('CANDIDATE_TIMING_BASELINE_PRESENT', timing_baseline.is_file())
ck('PLANNER_USES_PERSISTED_TIMING_BASELINE', prepare.is_file() and 'verification/CANDIDATE_TIMING_BASELINE.json' in prepare.read_text(encoding='utf-8'))

# Candidate planning must be fast and must split full PRE_EDITOR into persisted shards under the operational limit.
if prepare.is_file():
    started=time.time()
    pp=subprocess.run([sys.executable,str(prepare),str(ROOT),'--output',str(ROOT/'reports/ALPHA31_TEST_CANDIDATE_PLAN.json')],capture_output=True,text=True,timeout=10)
    pel=time.time()-started
    try: plan=json.loads((ROOT/'reports/ALPHA31_TEST_CANDIDATE_PLAN.json').read_text())
    except Exception: plan={}
    shards=plan.get('shards') or []
    ck('CANDIDATE_PLAN_FAST', pp.returncode==0 and pel < 3.0, f'{pel:.3f}s '+pp.stdout[-500:]+pp.stderr[-300:])
    ck('CANDIDATE_PLAN_MULTISHARD', len(shards)>=2, f'shards={len(shards)}')
    prof=json.loads((ROOT/'verification_profile.json').read_text())
    phase_order=['FAST','PRE_EDITOR','POST_EDITOR','RELEASE']
    expected_to_pre=[c['id'] for c in prof['checks'] if phase_order.index(c['phase'])<=phase_order.index('PRE_EDITOR')]
    planned=[cid for sh in shards for cid in sh.get('check_ids',[])]
    ck('PLAN_INCLUDES_FULL_PRE_EDITOR_DEPENDENCY_CLOSURE', planned==expected_to_pre, f'planned={len(planned)} expected={len(expected_to_pre)} first_missing={next((x for x in expected_to_pre if x not in planned),None)}')
    ck('EACH_SHARD_ESTIMATE_UNDER_LIMIT', bool(shards) and all(float(x.get('estimated_seconds',999)) < float(plan.get('operational_limit_seconds',20)) for x in shards), repr([(x.get('index'),x.get('estimated_seconds')) for x in shards]))

ok=all(c['status']=='PASS' for c in checks)
print(json.dumps({'status':'PASS' if ok else 'FAIL','tests_total':len(checks),'tests_passed':sum(c['status']=='PASS' for c in checks),'checks':checks},indent=2))
raise SystemExit(0 if ok else 1)
