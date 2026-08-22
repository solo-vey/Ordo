#!/usr/bin/env python3
import json, subprocess, tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]; err=[]
def ck(x,m):
    if not x: err.append(m)
reg=R/'source/design_rule_incentive_registry.v1.json'; ck(reg.exists(),'registry missing')
if reg.exists():
 d=json.loads(reg.read_text()); rules=d.get('rules',[]); ids={r.get('id') for r in rules}
 ck(len(ids)==len(rules),'duplicate rule ids')
 for r in rules:
  ck(r.get('canonical_law'),'canonical_law missing '+str(r.get('id')))
  ck(r.get('detector_class') in {'DETERMINISTIC','HYBRID','MODEL_JUDGMENT'},'bad detector class '+str(r.get('id')))
  ck(r.get('regression_asset'),'regression asset missing '+str(r.get('id')))
  if r.get('detector_class')=='MODEL_JUDGMENT': ck(r.get('enforcement') not in {'HARD_INELIGIBLE','HARD_UNSCORABLE'},'model judgment cannot hard-invalidate')
 ck('VALIDATION_LATENCY' in ids,'VALIDATION_LATENCY missing')
a=json.loads((R/'source/autonomous-playbook-improvement-policy.json').read_text())
term=a.get('termination',{}); ck(term.get('cycle_budget')==24,'cycle budget'); ck(term.get('invalid_revision_streak_limit')==3,'invalid streak')
ident=a.get('evaluation_regime',{}).get('identity_fields',[]); ck('holdout_split_hash' in ident,'holdout hash identity')
q=json.loads((R/'source/quality_acceptance_policy.json').read_text()); ps=q['process_score']
ck(ps.get('floor')==0,'process floor missing'); caps=ps.get('family_caps',{})
for k in ['open_question','group_mixing','reasked_known','nonadaptive','prefilled_confirmation']: ck(k in caps,'cap missing '+k)
ck('tiers' in q,'tier taxonomy missing')
if err:
 print('ALPHA42 INCENTIVE REGISTRY: FAIL'); [print('-',e) for e in err]; raise SystemExit(1)
print('ALPHA42 INCENTIVE REGISTRY: PASS')
