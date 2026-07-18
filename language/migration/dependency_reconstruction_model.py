from collections import defaultdict,deque
def validate_dependency_graph(graph,mapping,source_clause_ids):
 nodes=graph.get('nodes',[]); edges=graph.get('edges',[]); ids={n['node_id'] for n in nodes}; issues=[]
 if any(e['from'] not in ids or e['to'] not in ids for e in edges): issues.append({'code':'MIG-GRAPH-REF-001'})
 mapped={e['unit_id']:e for e in mapping.get('entries',[])}
 if ids-set(mapped): issues.append({'code':'MIG-MAP-001','unit_ids':sorted(ids-set(mapped))})
 if any(n.get('mandatory') and mapped.get(n['node_id'],{}).get('mapping_mode')=='unresolved' for n in nodes): issues.append({'code':'MIG-MAP-MANDATORY-001'})
 rel={'precedes','requires','authorizes','guards','produces','consumes','evidences'}; adj=defaultdict(list); indeg={i:0 for i in ids}
 for e in edges:
  if e['relation'] in rel and e['from'] in ids and e['to'] in ids: adj[e['from']].append(e['to']); indeg[e['to']]+=1
 q=deque(sorted(i for i,d in indeg.items() if d==0)); out=[]
 while q:
  x=q.popleft(); out.append(x)
  for y in adj[x]: indeg[y]-=1; q.append(y) if indeg[y]==0 else None
 if len(out)!=len(ids): issues.append({'code':'MIG-GRAPH-CYCLE-001'})
 return {'status':'passed' if not issues else 'blocked','issues':issues,'topological_order':out if len(out)==len(ids) else []}
