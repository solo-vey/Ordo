#!/usr/bin/env python3
import argparse, hashlib, json, sys
from pathlib import Path
import yaml

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 p=Path(p); return json.loads(p.read_text()) if p.suffix=='.json' else yaml.safe_load(p.read_text())
def norm_rule(r):
 return {k:r.get(k) for k in ['rule_id','requirement','condition','severity','blocking','exceptions','lineage_requirement','terminal_predicate']}
def verdict(rule,fixture):
 field=rule.get('requirement',{}).get('field') if isinstance(rule.get('requirement'),dict) else None
 kind=rule.get('requirement',{}).get('kind') if isinstance(rule.get('requirement'),dict) else None
 if kind=='required': return field in fixture and fixture.get(field) not in (None,'')
 if kind=='forbidden': return field not in fixture
 if kind=='equals': return fixture.get(field)==rule['requirement'].get('value')
 return True
def main():
 a=argparse.ArgumentParser(); a.add_argument('--external',required=True); a.add_argument('--internal',required=True); a.add_argument('--binding',required=True); a.add_argument('--fixtures'); a.add_argument('--report',required=True); a.add_argument('--regenerate',action='store_true'); x=a.parse_args()
 ext=load(x.external); inte=load(x.internal); bind=load(x.binding)
 expected=bind['external_contract']; dif=[]
 actual_sha=sha(x.external)
 if expected.get('contract_id')!=ext.get('contract_id'): dif.append({'type':'wrong_contract_binding'})
 if expected.get('contract_version')!=ext.get('contract_version'): dif.append({'type':'stale_contract_binding'})
 if expected.get('contract_sha256') not in ('AUTO',actual_sha): dif.append({'type':'stale_contract_binding','field':'checksum'})
 er={r['rule_id']:norm_rule(r) for r in ext.get('rules',[])}; ir={r['rule_id']:norm_rule(r) for r in inte.get('rules',[])}
 for rid,r in er.items():
  if rid not in ir: dif.append({'type':'missing_internal_rule','rule_id':rid}); continue
  q=ir[rid]
  for k in ['requirement','condition','severity','blocking','exceptions','lineage_requirement','terminal_predicate']:
   if q.get(k)!=r.get(k): dif.append({'type':'weaker_internal_rule' if k in ('severity','blocking','requirement') else 'contradictory_rule','rule_id':rid,'field':k,'external':r.get(k),'internal':q.get(k)})
 approved=set(bind.get('approved_extra_rule_ids',[]))
 for rid,r in ir.items():
  if rid not in er and r.get('blocking') and rid not in approved: dif.append({'type':'unapproved_extra_blocking_rule','rule_id':rid})
 regenerated=False
 if dif and x.regenerate:
  inte={'schema_version':'ordo.internal_validation_rules.v1','bound_contract_id':ext['contract_id'],'bound_contract_version':ext['contract_version'],'bound_contract_sha256':actual_sha,'rules':ext.get('rules',[])}
  Path(x.internal).write_text(yaml.safe_dump(inte,sort_keys=False,allow_unicode=True)); regenerated=True; dif=[]; ir=er
 eq={'positive':True,'negative':True,'boundary':True}
 if x.fixtures:
  fs=load(x.fixtures)
  for kind in eq:
   for f in fs.get(kind,[]):
    ev=all(verdict(r,f) for r in er.values()); iv=all(verdict(r,f) for r in ir.values())
    if ev!=iv: eq[kind]=False
 status='PASS' if not dif and all(eq.values()) else 'FAIL_CLOSED'
 rep={'status':status,'node_id':bind['node_id'],'template_id':bind['template_id'],'external_contract':{'contract_id':ext['contract_id'],'contract_version':ext['contract_version'],'contract_sha256':actual_sha},'checksums':{'external':actual_sha,'internal':sha(x.internal)},'differences':dif,'unresolved_difference_count':len(dif),'verdict_equivalence':eq,'regenerated':regenerated}
 Path(x.report).parent.mkdir(parents=True,exist_ok=True); Path(x.report).write_text(json.dumps(rep,indent=2)+'\n')
 return 0 if status=='PASS' else 2
if __name__=='__main__': raise SystemExit(main())
