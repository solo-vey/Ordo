#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path

REV_RE=re.compile(r"0\.1\.0-alpha\.\d+")

def _json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e: return {'__error__':str(e)}

def _revision_records(data):
    revs=data.get('revisions') if isinstance(data,dict) else None
    if not isinstance(revs,list): return [],['revisions_not_list']
    out=[]; errors=[]
    for i,x in enumerate(revs):
        if not isinstance(x,dict) or not isinstance(x.get('revision'),str):
            errors.append(f'revision_entry_not_object:{i}:{x!r}')
        else: out.append(x['revision'])
    return out,errors

def validate_revision_evidence(root: Path) -> dict:
    root=Path(root).resolve(); findings=[]
    # Accept either flat fixture layout or real handoff layout.
    candidates={
      'matrix':[root/'VERSION_MATRIX.json',root/'02_VERSION_HISTORY/VERSION_MATRIX.json'],
      'registry':[root/'VERSION_ISSUE_REGISTRY.json',root/'03_ISSUE_AND_TIME_KNOWLEDGE/VERSION_ISSUE_REGISTRY.json'],
      'log':[root/'VERSION_ISSUE_LOG.md',root/'03_ISSUE_AND_TIME_KNOWLEDGE/VERSION_ISSUE_LOG.md'],
    }
    paths={k:next((p for p in ps if p.is_file()),None) for k,ps in candidates.items()}
    if not all(paths.values()):
        missing=[k for k,v in paths.items() if v is None]
        return {'status':'FAIL','root':str(root),'findings':[{'code':'GP_REVISION_EVIDENCE_INCONSISTENT','reason':'missing_required_history_artifacts','missing':missing}]}
    md=_json(paths['matrix']); rd=_json(paths['registry'])
    if '__error__' in md or '__error__' in rd:
        findings.append({'code':'GP_REVISION_EVIDENCE_INCONSISTENT','reason':'invalid_json','matrix_error':md.get('__error__'),'registry_error':rd.get('__error__')})
    mrev,merr=_revision_records(md); rrev,rerr=_revision_records(rd)
    log_text=paths['log'].read_text(encoding='utf-8')
    lrev=[]
    for x in REV_RE.findall(log_text):
        if x not in lrev: lrev.append(x)
    if merr or rerr:
        findings.append({'code':'GP_REVISION_EVIDENCE_INCONSISTENT','reason':'non_object_revision_record','matrix_errors':merr,'registry_errors':rerr})
    sets={'matrix':set(mrev),'registry':set(rrev),'log':set(lrev)}
    union=set().union(*sets.values())
    for rev in sorted(union):
        missing=[name for name,s in sets.items() if rev not in s]
        if missing:
            findings.append({'code':'GP_REVISION_EVIDENCE_INCONSISTENT','reason':'revision_missing_from_artifact','revision':rev,'missing_from':missing})
    for name,revs in [('matrix',mrev),('registry',rrev)]:
        if len(revs)!=len(set(revs)):
            findings.append({'code':'GP_REVISION_EVIDENCE_INCONSISTENT','reason':'duplicate_revision','artifact':name})
    # If current_revision is declared, it must be represented as a full record everywhere.
    current=None
    if isinstance(rd,dict): current=rd.get('current_revision')
    if isinstance(current,str) and current not in set(rrev):
        findings.append({'code':'GP_REVISION_EVIDENCE_INCONSISTENT','reason':'current_revision_missing_full_record','revision':current})
    return {'schema_version':'1.0','validator_id':'VIBE_REVISION_EVIDENCE_CONSISTENCY_V1','status':'PASS' if not findings else 'FAIL','root':str(root),'revision_sets':{k:sorted(v) for k,v in sets.items()},'findings':findings}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.')
    a=ap.parse_args(); r=validate_revision_evidence(Path(a.root)); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
