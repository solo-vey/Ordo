from __future__ import annotations
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('editor_service_r1_7132', ROOT/'editor_service.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


def _hist(missing):
    return {'role':'assistant','node_id':'G_TEST_COVERAGE_COMPLETE','debug':{'runtime':{'deterministic_gate':{'result':'fail','missing_coverage':missing}}}}


def test_coverage_progress_first_failure_routes():
    r=mod._coverage_recovery_progress([], 'G_TEST_COVERAGE_COMPLETE', ['a','b'])
    assert r['classification']=='first_failure' and not r['stop']


def test_coverage_progress_strict_subset_only():
    r=mod._coverage_recovery_progress([_hist(['a','b','c'])], 'G_TEST_COVERAGE_COMPLETE', ['a','b'])
    assert r['classification']=='progress' and not r['stop'] and r['resolved_ids']==['c']
    stalled=mod._coverage_recovery_progress([_hist(['a','b'])], 'G_TEST_COVERAGE_COMPLETE', ['a','b'])
    assert stalled['classification']=='stall' and stalled['stop'] and stalled['stop_reason']=='no_progress_recovery_loop'
    regressed=mod._coverage_recovery_progress([_hist(['a','b'])], 'G_TEST_COVERAGE_COMPLETE', ['a','c'])
    assert regressed['classification']=='regression' and regressed['stop']


def test_coverage_progress_round_limit_lives_in_runtime():
    history=[_hist(['a','b','c','d']),_hist(['a','b','c']),_hist(['a','b'])]
    r=mod._coverage_recovery_progress(history,'G_TEST_COVERAGE_COMPLETE',['a'])
    assert r['stop'] and r['stop_reason']=='coverage_recovery_round_limit'


def test_unknown_custom_provider_does_not_probe_strict():
    schema={'type':'object','additionalProperties':False,'required':['x'],'properties':{'x':{'type':'string'}}}
    ok,reason=mod._runtime_strict_schema_compatible(schema,{'provider':'custom','api_style':'chat_completions'})
    assert not ok and ('unknown/unsupported' in reason or 'strict schema disabled by structured-output mode json_object' in reason)


def test_strict_checker_rejects_conditional_keywords():
    base={'type':'object','additionalProperties':False,'required':['x'],'properties':{'x':{'type':'string'}}}
    for keyword,value in [('allOf',[]),('if',{}),('then',{}),('else',{}),('not',{})]:
        schema=dict(base); schema[keyword]=value
        ok,_=mod._runtime_strict_schema_compatible(schema,{'provider':'openai','api_style':'chat_completions'})
        assert not ok, keyword


def test_strict_checker_allows_closed_anyof_variants():
    variant=lambda const: {'type':'object','additionalProperties':False,'required':['op'],'properties':{'op':{'const':const}}}
    schema={'anyOf':[variant('append'),variant('set')]}
    ok,_=mod._runtime_strict_schema_compatible(schema,{'provider':'openai','api_style':'chat_completions'})
    assert ok
