#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); a=ap.parse_args(); r=Path(a.root).resolve(); findings=[]
    def need(cond,code,**detail):
        if not cond: findings.append({'code':code,**detail})
    for rel in ['source/packaging-continuity-policy.json','source/validator-applicability-policy.json','source/package-continuity-manifest.schema.json','DISTRIBUTION_PACKAGE_CONTRACT.json','tools/build_three_profile_playbook_distribution.py','tools/validate_distribution_package.py']:
        need((r/rel).is_file(),'MISSING_REQUIRED_PACKAGING_CONTINUITY_ASSET',path=rel)
    try: p=json.loads((r/'source/packaging-continuity-policy.json').read_text()); c=json.loads((r/'DISTRIBUTION_PACKAGE_CONTRACT.json').read_text()); a1=json.loads((r/'source/validator-applicability-policy.json').read_text())
    except Exception as e:
        p={}; c={}; a1={}; findings.append({'code':'POLICY_PARSE_ERROR','error':str(e)})
    need(p.get('source_of_truth')=='canonical_source_only','CANONICAL_SOURCE_POLICY')
    need(p.get('historical_candidates')=='evidence_only_never_source_of_truth','HISTORICAL_CANDIDATE_AUTHORITY')
    need(set(c.get('profiles',{}))=={'EDIT','CLI_RUN','MODEL_RUN'},'PROFILE_SET')
    need(c.get('packaging_continuity_policy')=='source/packaging-continuity-policy.json','CONTINUITY_POLICY_BINDING')
    need(c.get('validator_applicability_policy')=='source/validator-applicability-policy.json','APPLICABILITY_POLICY_BINDING')
    need(a1.get('default')=='NOT_APPLICABLE_UNLESS_DECLARED','APPLICABILITY_DEFAULT')
    # stale canonical release vocabulary is a continuity defect in active package-flow nodes
    import yaml
    prog=yaml.safe_load((r/'source/program.ordo.yaml').read_text()) or {}
    package_nodes=[x for x in prog.get('nodes',[]) if isinstance(x,dict) and x.get('id','').startswith(('N_PI_GENERATED_PLAYBOOK_PACKAGE_','N_OUT_GENERATED_PACKAGE_'))]
    stale=[]
    for n in package_nodes:
        text=json.dumps(n,ensure_ascii=False)
        if 'DEV/RUN' in text or 'both distributions' in text or 'build_dual_playbook_distribution.py' in text or 'dual_package_' in text: stale.append(n.get('id'))
    need(not stale,'STALE_DUAL_DISTRIBUTION_VOCABULARY',nodes=stale)
    report={'status':'PASS' if not findings else 'FAIL','findings':findings,'profiles':sorted(c.get('profiles',{})),'packaging_policy_sha256':sha(r/'source/packaging-continuity-policy.json') if (r/'source/packaging-continuity-policy.json').is_file() else None,'validator_applicability_policy_sha256':sha(r/'source/validator-applicability-policy.json') if (r/'source/validator-applicability-policy.json').is_file() else None}
    out={'schema_version':'state_updates_v1','report':report,'state_updates':{'packaging_continuity_status':report['status'],'packaging_continuity_report':report}}
    print(json.dumps(out,ensure_ascii=False,indent=2)); return 0 if not findings else 1
if __name__=='__main__': raise SystemExit(main())
