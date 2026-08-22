#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]

def req(cond,msg):
    if not cond: raise AssertionError(msg)

policy_path=ROOT/'source/adaptive-artifact-quality-policy.json'
req(policy_path.exists(),'adaptive artifact quality policy missing')
policy=json.loads(policy_path.read_text())
req(policy['validation_architecture']=='HYBRID_DETERMINISTIC_PLUS_SEMANTIC_MODEL','hybrid validation architecture missing')
req(policy['semantic_model_gate']['canonical_state_mutation_allowed'] is False,'semantic validator must be read-only over canonical state')
req(policy['semantic_model_gate']['deterministic_failure_override_allowed'] is False,'model must not override deterministic failure')
req(policy['completeness_profile']['roles']==['REQUIRED_CONSEQUENTIAL','DERIVABLE','OPTIONAL','IMPLEMENTATION_DETAIL','INAPPLICABLE'],'adaptive completeness roles mismatch')
req(policy['materialization']['synthetic_unknown_forbidden'] is True,'synthetic UNKNOWN must be forbidden')
req(policy['derived_outputs']['derive_before_analyst_escalation'] is True,'derived outputs must self-generate before analyst escalation')
req(policy['quality_routing']['priority']==['DERIVABLE_FIX','SOURCE_REQUIRED','ANALYST_DECISION_REQUIRED','IMPLEMENTATION_DETAIL'],'quality routing priority mismatch')
req(policy['metrics']['DERIVABLE_UNKNOWN_COUNT']['target']==0,'DERIVABLE_UNKNOWN_COUNT target must be zero')

schema=ROOT/'source/semantic-artifact-quality-gate.schema.json'
req(schema.exists(),'semantic quality output schema missing')
s=json.loads(schema.read_text())
props=s['properties']
req(set(props['quality_status']['enum'])=={'PASS','PASS_WITH_NOTES','BLOCK'},'quality status enum mismatch')
req('canonical_state_patch' not in props,'semantic gate schema must not expose canonical state mutation channel')

reg=ROOT/'authoring_templates/reusable/TEMPLATE_KIT_REGISTRY.json'
r=json.loads(reg.read_text())
req('adaptive_artifact_quality' in r['templates'],'adaptive quality reusable template not registered')
tpl=ROOT/r['templates']['adaptive_artifact_quality']['path']
req(tpl.exists(),'adaptive quality reusable template missing')

evaluator=ROOT/'tools/evaluate_adaptive_artifact_quality.py'
req(evaluator.exists(),'deterministic adaptive quality evaluator missing')

def evaluate(payload):
    with tempfile.TemporaryDirectory() as td:
        inp=Path(td)/'in.json'; out=Path(td)/'out.json'
        inp.write_text(json.dumps(payload),encoding='utf-8')
        cp=subprocess.run([sys.executable,str(evaluator),'--input',str(inp),'--output',str(out)],capture_output=True,text=True)
        req(cp.returncode in (0,2),cp.stderr or cp.stdout)
        return json.loads(out.read_text())

base={
 'canonical_fields':{
  'rule.trigger':{'value':'status=CANCELLED','resolution_status':'KNOWN','completeness_role':'REQUIRED_CONSEQUENTIAL','provenance_type':'analyst'},
  'expected.negative':{'value':None,'resolution_status':'UNKNOWN_CONFIRMED','completeness_role':'DERIVABLE','derivation_available':True,'provenance_type':'analyst'},
  'impl.retry':{'value':None,'resolution_status':'UNASKED','completeness_role':'IMPLEMENTATION_DETAIL'},
 },
 'template_sections':[{'section_id':'behavior','substantive':True,'resolution_strategy':'canonical_or_derived'}],
 'artifact_fields':[{'field_id':'expected.negative','rendered_value':'UNKNOWN','rendered_provenance_type':'analyst'}],
 'derived_outputs':[], 'generated_tests':[], 'deterministic_failures':[], 'semantic_findings':[]
}
res=evaluate(base)
req(res['quality_status']=='BLOCK','derivable unknown must block quality readiness')
req(res['metrics']['DERIVABLE_UNKNOWN_COUNT']==1,'derivable unknown count wrong')
req(any(i['code']=='DERIVABLE_UNKNOWN' for i in res['issues']),'derivable unknown issue missing')

synthetic={**base,'canonical_fields':{
 'rule.trigger':base['canonical_fields']['rule.trigger'],
 'expected.negative':{'value':None,'resolution_status':'UNASKED','completeness_role':'OPTIONAL'},
},'artifact_fields':[{'field_id':'expected.negative','rendered_value':'UNKNOWN','rendered_provenance_type':None}]}
res2=evaluate(synthetic)
req(any(i['code']=='SYNTHETIC_UNKNOWN' for i in res2['issues']),'synthetic unknown must be detected')

orphan={**base,'canonical_fields':{'rule.trigger':base['canonical_fields']['rule.trigger']},'template_sections':[{'section_id':'tests','substantive':True,'resolution_strategy':None}],'artifact_fields':[]}
res3=evaluate(orphan)
req(any(i['code']=='ORPHAN_SUBSTANTIVE_SECTION' for i in res3['issues']),'orphan substantive section must be detected')

# Strong generated tests are rule-linked and concrete; weak generic tests are not accepted as semantic coverage evidence.
weak={**base,'canonical_fields':{'rule.trigger':base['canonical_fields']['rule.trigger']},'artifact_fields':[],
 'generated_tests':[{'test_id':'t1','source_rule_ids':['rule.trigger'],'precondition':'some value','expected':'works correctly'}]}
res4=evaluate(weak)
req(any(i['code']=='WEAK_GENERATED_TEST' for i in res4['issues']),'weak generated test must be flagged')

# Semantic findings are routed, but never mutate canonical state.
findings={**base,'canonical_fields':{'rule.trigger':base['canonical_fields']['rule.trigger']},'artifact_fields':[],
 'semantic_findings':[
  {'category':'DERIVABLE_FIX','severity':'high','finding':'missing negative case','requires_analyst_input':False},
  {'category':'ANALYST_DECISION_REQUIRED','severity':'high','finding':'business precedence unknown','requires_analyst_input':True},
  {'category':'IMPLEMENTATION_DETAIL','severity':'low','finding':'retry tuning deferred','requires_analyst_input':False}
 ]}
res5=evaluate(findings)
req(res5['routes']['self_fix']==1,'derivable semantic finding must route to self-fix')
req(res5['routes']['analyst']==1,'true analyst decision must route to analyst')
req(res5['routes']['downstream']==1,'implementation detail must route downstream/nonblocking')

# Deterministic failure dominates model PASS.
dom={**findings,'deterministic_failures':[{'code':'BROKEN_REFERENCE','message':'broken'}], 'semantic_quality_status':'PASS'}
res6=evaluate(dom)
req(res6['quality_status']=='BLOCK','semantic PASS must not override deterministic failure')

oc=yaml.safe_load((ROOT/'authoring/information_object_catalog.yaml').read_text()) or {}
objs={x['id']:x for x in oc.get('objects') or [] if isinstance(x,dict) and x.get('id')}
for oid in ['I_ADAPTIVE_COMPLETENESS_PROFILE_CONTRACT','I_DERIVED_OUTPUT_GENERATION_CONTRACT','I_HYBRID_ARTIFACT_QUALITY_VALIDATION_CONTRACT','I_SEMANTIC_QUALITY_FINDING_CONTRACT']:
    req(oid in objs,f'missing Data Layer object {oid}')

prog=yaml.safe_load((ROOT/'source/program.ordo.yaml').read_text()) or {}
laws={x.get('id'):x.get('text','') for x in ((prog.get('playbook_laws') or {}).get('laws') or []) if isinstance(x,dict)}
for lid in ['E70_ADAPTIVE_COMPLETENESS_PROFILE','E71_DERIVED_OUTPUTS_FROM_CANONICAL_CONTRACT','E72_HYBRID_ARTIFACT_QUALITY_VALIDATION','E73_QUALITY_SELF_REPAIR_AND_ALIGNMENT']:
    req(lid in laws,f'missing canonical law {lid}')

print('ALPHA42 ADAPTIVE ARTIFACT QUALITY: PASS')
