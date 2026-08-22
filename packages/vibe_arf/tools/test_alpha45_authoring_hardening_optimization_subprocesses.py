#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, sys, yaml
R=Path(__file__).resolve().parents[1]
checks=[]
def ck(name, cond, detail=''): checks.append((name,bool(cond),detail))

# Canonical reusable policies/templates
for rel in [
    'source/quality-hardening-subprocess-policy.json',
    'source/performance-token-optimization-subprocess-policy.json',
    'source/development-subprocess-routing-policy.json',
    'authoring_templates/reusable/QUALITY_HARDENING_LOOP.template.yaml',
    'authoring_templates/reusable/PERFORMANCE_TOKEN_OPTIMIZATION_LOOP.template.yaml',
]: ck('exists_'+rel.replace('/','_'), (R/rel).is_file())

# State-machine nodes/gates must be real executable graph elements.
prog=yaml.safe_load((R/'source/program.ordo.yaml').read_text())
nodes={n['id']:n for n in prog.get('nodes',[])}
gates={g['id']:g for g in prog.get('gates',[])}
qh_nodes=['N_QH_BASELINE_CAPTURE','N_QH_DEFECT_CLASSIFY','N_QH_RED_REGRESSION_DEFINE','N_QH_RED_REGRESSION_RUN','N_QH_MINIMAL_REPAIR','N_QH_GREEN_RUN','N_QH_IMPACTED_REGRESSIONS','N_QH_FINAL_CONFIRM']
qh_gates=['G_QH_RED_CONFIRMED','G_QH_GREEN','G_QH_IMPACTED_GREEN']
po_nodes=['N_PO_BASELINE_CAPTURE','N_PO_TELEMETRY_COLLECT','N_PO_HOTSPOT_RANK','N_PO_HYPOTHESIS_DEFINE','N_PO_OPTIMIZATION_APPLY','N_PO_TARGETED_COMPARE','N_PO_ACCEPT_REJECT']
po_gates=['G_PO_QUALITY_BASELINE_STABLE','G_PO_SEMANTIC_EQUIVALENCE','G_PO_PERFORMANCE_IMPROVED']
for x in qh_nodes+po_nodes: ck('node_'+x, x in nodes)
for x in qh_gates+po_gates: ck('gate_'+x, x in gates)

# Quality hardening order/invariants.
if all(x in nodes for x in qh_nodes) and all(x in gates for x in qh_gates):
    ck('qh_red_before_repair', nodes['N_QH_RED_REGRESSION_RUN'].get('on_answer',{}).get('next')=='G_QH_RED_CONFIRMED')
    ck('qh_red_gate_to_repair', gates['G_QH_RED_CONFIRMED'].get('on_pass')=='N_QH_MINIMAL_REPAIR')
    ck('qh_repair_to_green', nodes['N_QH_MINIMAL_REPAIR'].get('on_answer',{}).get('next')=='N_QH_GREEN_RUN')
    ck('qh_green_then_impacted', gates['G_QH_GREEN'].get('on_pass')=='N_QH_IMPACTED_REGRESSIONS')
    ck('qh_fail_returns_to_cause', gates['G_QH_GREEN'].get('on_fail') in {'N_QH_DEFECT_CLASSIFY','N_QH_RED_REGRESSION_DEFINE'})

# Performance optimization safety/invariants.
if all(x in nodes for x in po_nodes) and all(x in gates for x in po_gates):
    ck('po_quality_first', nodes['N_PO_BASELINE_CAPTURE'].get('on_answer',{}).get('next')=='G_PO_QUALITY_BASELINE_STABLE')
    ck('po_baseline_gate_blocks_unstable', gates['G_PO_QUALITY_BASELINE_STABLE'].get('on_fail') in {'N_QH_BASELINE_CAPTURE','N_QH_DEFECT_CLASSIFY'})
    ck('po_telemetry_before_hypothesis', nodes['N_PO_TELEMETRY_COLLECT'].get('on_answer',{}).get('next')=='N_PO_HOTSPOT_RANK')
    ck('po_compare_to_semantic_gate', nodes['N_PO_TARGETED_COMPARE'].get('on_answer',{}).get('next')=='G_PO_SEMANTIC_EQUIVALENCE')
    ck('po_semantics_before_speed', gates['G_PO_SEMANTIC_EQUIVALENCE'].get('on_pass')=='G_PO_PERFORMANCE_IMPROVED')
    ck('po_semantic_fail_rejects', gates['G_PO_SEMANTIC_EQUIVALENCE'].get('on_fail')=='N_PO_ACCEPT_REJECT')
    ck('po_performance_accept_only_on_improvement', gates['G_PO_PERFORMANCE_IMPROVED'].get('on_pass')=='N_PO_ACCEPT_REJECT' and gates['G_PO_PERFORMANCE_IMPROVED'].get('on_fail')!='N_PO_ACCEPT_REJECT')

# Canonical state fields and contracts.
state=prog.get('state',{}).get('schema',{})
for f in ['development_subprocess_recommendation','quality_hardening_status','quality_hardening_evidence','performance_optimization_status','performance_baseline','performance_hotspot_rank','performance_comparison_evidence']:
    ck('state_'+f, f in state)

# Generalized Data Layer contracts, no applied-domain coupling.
obj=yaml.safe_load((R/'authoring/information_object_catalog.yaml').read_text())
objs={x['id']:x for x in obj.get('objects',[])}
for oid in ['I_QUALITY_HARDENING_SUBPROCESS_CONTRACT','I_PERFORMANCE_TOKEN_OPTIMIZATION_SUBPROCESS_CONTRACT','I_DEVELOPMENT_SUBPROCESS_ROUTING_CONTRACT']:
    ck('data_layer_'+oid, oid in objs)
    if oid in objs:
        text=json.dumps(objs[oid],ensure_ascii=False).lower()
        ck('domain_neutral_'+oid, not any(t in text for t in ['passport','jira','risk_factor','company_terminated']))

# Laws and incentive/diagnostic policy.
laws=(R/'PLAYBOOK_LAWS.md').read_text()
for lid in ['E85_STANDARD_QUALITY_HARDENING_SUBPROCESS','E86_STANDARD_PERFORMANCE_TOKEN_OPTIMIZATION_SUBPROCESS','E87_EVIDENCE_DRIVEN_DEVELOPMENT_SUBPROCESS_ROUTING']:
    ck('law_'+lid, lid in laws)
reg=json.loads((R/'source/design_rule_incentive_registry.v1.json').read_text())
rules={x['id']:x for x in reg.get('rules',[])}
for rid in ['UNEXPLAINED_REPEAT_PASS','QUALITY_REGRESSION_DURING_OPTIMIZATION','OBSERVABILITY_COVERAGE_GAP']:
    ck('rule_'+rid, rid in rules)
if 'QUALITY_REGRESSION_DURING_OPTIMIZATION' in rules:
    ck('quality_regression_is_hard', rules['QUALITY_REGRESSION_DURING_OPTIMIZATION'].get('enforcement') in {'HARD_INELIGIBLE','BLOCKED'})
if 'UNEXPLAINED_REPEAT_PASS' in rules:
    ck('repeat_pass_zero_score_diag', rules['UNEXPLAINED_REPEAT_PASS'].get('score_effect')==0)

# Generated-playbook inheritance and verification profile registration.
gen=json.loads((R/'source/generated-playbook-execution-inheritance-policy.json').read_text())
blob=json.dumps(gen,ensure_ascii=False)
ck('generated_inherits_quality_loop','QUALITY_HARDENING_LOOP' in blob)
ck('generated_inherits_perf_loop','PERFORMANCE_TOKEN_OPTIMIZATION_LOOP' in blob)
vp=json.loads((R/'verification_profile.json').read_text())
blob=json.dumps(vp,ensure_ascii=False)
ck('verification_profile_has_alpha45_subprocess_regression','alpha45_authoring_hardening_optimization_subprocesses' in blob)

failed=[(n,d) for n,c,d in checks if not c]
print(json.dumps({'status':'PASS' if not failed else 'FAIL','passed':sum(c for _,c,_ in checks),'total':len(checks),'failed':[n for n,_ in failed],'details':{n:d for n,d in failed if d}},ensure_ascii=False,indent=2))
sys.exit(0 if not failed else 1)
