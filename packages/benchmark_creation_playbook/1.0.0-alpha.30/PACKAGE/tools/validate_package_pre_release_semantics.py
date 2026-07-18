#!/usr/bin/env python3
import argparse,json,yaml,pathlib,sys

def targets(obj):
 out=[]
 for k in ('next','on_pass','on_fail','on_complete'):
  v=obj.get(k)
  if isinstance(v,str): out.append(v)
  elif isinstance(v,dict) and isinstance(v.get('next'),str): out.append(v['next'])
 for b in obj.get('branches',[]) or []:
  if isinstance(b,dict) and isinstance(b.get('next'),str): out.append(b['next'])
 return out

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('program'); ap.add_argument('--out',required=True); a=ap.parse_args()
 d=yaml.safe_load(pathlib.Path(a.program).read_text())
 items={x['id']:x for k in ('nodes','gates','terminals') for x in d.get(k,[])}
 entry=(d.get('process_rail') or {}).get('entry_node') or (d.get('execution_graph_contract') or {}).get('entry_node') or d.get('entrypoint') or d['nodes'][0]['id']
 adj={i:targets(x) for i,x in items.items()}
 allowed_external={'T_SUCCESS','T_BLOCKED'}
 dangling=sorted({t for ts in adj.values() for t in ts if t not in items and t not in allowed_external})
 seen=set(); stack=[entry]
 while stack:
  x=stack.pop()
  if x in seen or x not in items: continue
  seen.add(x); stack.extend(adj.get(x,[]))
 unreachable=sorted(set(items)-seen)
 required_route=['N074_BUILD_DECLARED_CONTRACT_INVENTORY','N075_SEAL_EXTERNAL_TESTING_CANDIDATE','N076_SELF_APPLY_DECLARED_CONTRACTS','N077_SCOPED_DECLARED_CONTRACT_CORRECTION','N078_DECLARED_CONTRACT_RETRY_DECISION','G_DECLARED_CONTRACT_ARCHIVE_RELEASE','T_PRE_RELEASE_DECLARED_CONTRACT_MISMATCH']
 route_present=all(x in items for x in required_route)
 required_edges={('N074_BUILD_DECLARED_CONTRACT_INVENTORY','N075_SEAL_EXTERNAL_TESTING_CANDIDATE'),('N075_SEAL_EXTERNAL_TESTING_CANDIDATE','N076_SELF_APPLY_DECLARED_CONTRACTS'),('N076_SELF_APPLY_DECLARED_CONTRACTS','G_DECLARED_CONTRACT_ARCHIVE_RELEASE'),('N076_SELF_APPLY_DECLARED_CONTRACTS','N077_SCOPED_DECLARED_CONTRACT_CORRECTION'),('N077_SCOPED_DECLARED_CONTRACT_CORRECTION','N078_DECLARED_CONTRACT_RETRY_DECISION'),('N078_DECLARED_CONTRACT_RETRY_DECISION','N075_SEAL_EXTERNAL_TESTING_CANDIDATE'),('N078_DECLARED_CONTRACT_RETRY_DECISION','T_PRE_RELEASE_DECLARED_CONTRACT_MISMATCH')}
 edge_set={(a,b) for a,bs in adj.items() for b in bs}
 route_connected=required_edges.issubset(edge_set)
 rep={'status':'PASS' if not dangling and route_present and route_connected else 'FAIL','entrypoint':entry,'node_count':len(d.get('nodes',[])),'gate_count':len(d.get('gates',[])),'terminal_count':len(d.get('terminals',[])),'reachable_count':len(seen),'dangling_targets':dangling,'unreachable_ids_in_global_graph':unreachable,'required_bl050_route_present':route_present,'required_bl050_route_connected':route_connected}
 pathlib.Path(a.out).write_text(json.dumps(rep,indent=2)+'\n'); print(json.dumps(rep,indent=2)); return 0 if rep['status']=='PASS' else 2
if __name__=='__main__': raise SystemExit(main())
