#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, sys
R=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]).resolve()
p=R/'source/optimization-history-ledger.json'
errs=[]
try: d=json.loads(p.read_text())
except Exception as e:
    print(json.dumps({'status':'FAIL','errors':['LEDGER_READ:'+str(e)]},indent=2)); raise SystemExit(1)
if d.get('append_only') is not True: errs.append('APPEND_ONLY_NOT_TRUE')
req=['problem','baseline_evidence','hypothesis','protected_invariants','regression_asset','change','comparison_evidence','measured_result','limitations','decision']
prev=None
for i,e in enumerate(d.get('entries',[]),1):
    if e.get('sequence') != i: errs.append(f'SEQUENCE:{i}')
    if e.get('previous_entry_hash') != prev: errs.append(f'PREV_HASH:{i}')
    for k in req:
        if k not in e: errs.append(f'MISSING:{i}:{k}')
    claimed=e.get('entry_hash')
    x=dict(e); x.pop('entry_hash',None)
    actual='sha256:'+hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    if claimed!=actual: errs.append(f'ENTRY_HASH:{i}')
    prev=claimed
print(json.dumps({'status':'PASS' if not errs else 'FAIL','entries':len(d.get('entries',[])),'head':prev,'errors':errs},indent=2))
raise SystemExit(0 if not errs else 1)
