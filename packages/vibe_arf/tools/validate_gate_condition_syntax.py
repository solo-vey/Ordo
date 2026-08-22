#!/usr/bin/env python3
from pathlib import Path
import sys,re,yaml,json
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
prog=yaml.safe_load((root/'source/program.ordo.yaml').read_text()) or {}
issues=[]; checked=0
for sec in ('nodes','gates'):
    for e in prog.get(sec) or []:
        if not isinstance(e,dict): continue
        c=e.get('condition')
        if not isinstance(c,str): continue
        for m in re.finditer(r'is one of\s+(.+?)(?=\s+and\s+state\.|$)',c):
            checked+=1; raw=m.group(1).strip()
            # Multiple enum values MUST be comma-separated. A whitespace-only list is ambiguous
            # and current Editor runtime treats it as one token.
            if ',' not in raw and len(raw.split())>1:
                issues.append({'element_id':e.get('id'),'condition':c,'enum_segment':raw,'code':'ONE_OF_VALUES_NOT_COMMA_SEPARATED'})
# also require authoring binding parity where a contract is declared
proj=yaml.safe_load((root/'authoring/ordo_projection.yaml').read_text()) or {}
byid={e.get('id'):e for sec in ('nodes','gates') for e in (prog.get(sec) or []) if isinstance(e,dict) and e.get('id')}
for row in proj.get('gate_condition_contracts') or []:
    if not isinstance(row,dict): continue
    gid=row.get('gate_id'); expected=row.get('condition'); actual=(byid.get(gid) or {}).get('condition')
    if actual!=expected: issues.append({'element_id':gid,'code':'AUTHORING_GATE_CONDITION_PARITY_MISMATCH','expected':expected,'actual':actual})
out={'status':'PASS' if not issues else 'FAIL','checked_one_of_clauses':checked,'declared_gate_condition_contracts':len(proj.get('gate_condition_contracts') or []),'issues':issues}
print(json.dumps(out,indent=2))
sys.exit(0 if not issues else 1)
