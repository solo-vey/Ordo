#!/usr/bin/env python3
from pathlib import Path
import tempfile, yaml, json, subprocess, copy, sys
ROOT=Path(__file__).resolve().parents[1]; PROGRAM=ROOT/'source/program.ordo.yaml'; VALIDATOR=ROOT/'tools/validate_execution_graph_connectivity.py'
def run(data):
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'p.yaml'; p.write_text(yaml.safe_dump(data,sort_keys=False),encoding='utf-8')
  q=subprocess.run([sys.executable,str(VALIDATOR),str(p)],capture_output=True,text=True)
  return q.returncode,json.loads(q.stdout)
base=yaml.safe_load(PROGRAM.read_text())
cases=[]
rc,r=run(base); cases.append({'id':'connected_positive','pass':rc==0 and r['status']=='PASS'})
x=copy.deepcopy(base); x['nodes'][-1].pop('next',None); x['nodes'][-1].pop('gates',None); rc,r=run(x); cases.append({'id':'dead_end_negative','pass':rc!=0 and 'ACCIDENTAL_DEAD_ENDS' in r['errors']})
x=copy.deepcopy(base); x['nodes'][0]['on_complete']['next']='MISSING_NODE'; rc,r=run(x); cases.append({'id':'dangling_negative','pass':rc!=0 and 'DANGLING_TARGETS' in r['errors']})
x=copy.deepcopy(base); x['nodes'][6]['id']='N007_ORPHAN_COPY'; x['execution_graph_contract']['route_authorized_node_ids'][6]='N007_ORPHAN_COPY'; rc,r=run(x); cases.append({'id':'unreachable_negative','pass':rc!=0 and ('UNREACHABLE_NODES' in r['errors'] or 'ORPHANS' in r['errors'])})
x=copy.deepcopy(base); x['execution_graph_contract']['entrypoint']='NO_ENTRY'; rc,r=run(x); cases.append({'id':'missing_entry_negative','pass':rc!=0 and 'MISSING_ENTRYPOINT' in r['errors']})
out={'schema_version':'ordo.execution_graph_connectivity.acceptance.v1','status':'PASS' if all(c['pass'] for c in cases) else 'FAIL','passed':sum(c['pass'] for c in cases),'total':len(cases),'cases':cases}
path=ROOT/'reports/EXECUTION_GRAPH_CONNECTIVITY_ACCEPTANCE_TESTS.json'; path.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); raise SystemExit(0 if out['status']=='PASS' else 2)
