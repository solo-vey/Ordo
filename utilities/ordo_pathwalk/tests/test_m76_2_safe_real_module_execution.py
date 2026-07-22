import json
from pathlib import Path
from utilities.ordo_pathwalk.runner.real_module_execution import create_real_module_execution_plan, run_real_module_execution_job, collect_real_module_execution_results

ROOT=Path(__file__).resolve().parents[3]
SUMMARY=ROOT/'utilities/ordo_pathwalk/examples/m60_7_3_clean_path_testcases/SUMMARY.json'
SOURCE=ROOT/'utilities/ordo_pathwalk/examples/m60_7_2_terminal_path_enumeration/source/program.ordo.yaml'

def test_plan_is_artifact_only(tmp_path):
    p=create_real_module_execution_plan(summary_path=SUMMARY, source_path=SOURCE, out_dir=tmp_path/'run', timeout_seconds=10)
    assert p['execution_contract']=='one-job-one-child-process-collect-only-parent'
    assert len(p['jobs'])==3
    assert not (tmp_path/'run/results').exists()

def test_one_job_executes_in_isolated_child(tmp_path):
    p=create_real_module_execution_plan(summary_path=SUMMARY, source_path=SOURCE, out_dir=tmp_path/'run', timeout_seconds=20)
    r=run_real_module_execution_job(tmp_path/'run/REAL_MODULE_EXECUTION_PLAN.json', p['jobs'][0]['job_id'])
    assert r['status']=='passed'
    assert r['raw_evidence_ready'] is True
    assert r['isolation']['source_copied'] is True
    assert r['scoring_performed'] is False

def test_collect_only_reports_missing(tmp_path):
    p=create_real_module_execution_plan(summary_path=SUMMARY, source_path=SOURCE, out_dir=tmp_path/'run', timeout_seconds=20)
    run_real_module_execution_job(tmp_path/'run/REAL_MODULE_EXECUTION_PLAN.json', p['jobs'][0]['job_id'])
    s=collect_real_module_execution_results(tmp_path/'run/REAL_MODULE_EXECUTION_PLAN.json')
    assert s['status']=='incomplete_or_failed'
    assert s['counts']['missing']==2

def test_all_jobs_collect_pass(tmp_path):
    p=create_real_module_execution_plan(summary_path=SUMMARY, source_path=SOURCE, out_dir=tmp_path/'run', timeout_seconds=20)
    for j in p['jobs']:
        assert run_real_module_execution_job(tmp_path/'run/REAL_MODULE_EXECUTION_PLAN.json', j['job_id'])['status']=='passed'
    s=collect_real_module_execution_results(tmp_path/'run/REAL_MODULE_EXECUTION_PLAN.json')
    assert s['status']=='passed'
    assert s['counts']['passed']==3
